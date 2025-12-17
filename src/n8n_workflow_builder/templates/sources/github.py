"""GitHub Template Source"""
import httpx
import json
import base64
import logging
from typing import List, Dict, Optional
from datetime import datetime
from .base import TemplateSource, TemplateMetadata

logger = logging.getLogger("n8n-workflow-builder")


class GitHubSource(TemplateSource):
    """Fetch templates from GitHub repositories"""

    def __init__(self, repos: List[str] = None, github_token: Optional[str] = None, cache_path: Optional[str] = None):
        """
        Initialize GitHub source

        Args:
            repos: List of GitHub repos in format "owner/repo" or "owner/repo/path"
            github_token: Optional GitHub personal access token for private repos
            cache_path: Optional path to cache database
        """
        super().__init__("github")
        self.repos = repos or []
        self.github_token = github_token
        self.cache: Dict[str, TemplateMetadata] = {}
        self.client = httpx.AsyncClient(timeout=30.0)

        self.headers = {"Accept": "application/vnd.github+json"}
        if github_token:
            self.headers["Authorization"] = f"Bearer {github_token}"

        # Initialize persistent cache
        from ..cache import TemplateCache
        self.persistent_cache = TemplateCache(cache_path)

    async def fetch_templates(self) -> List[TemplateMetadata]:
        """Fetch all templates from configured GitHub repos"""
        templates = []

        for repo_path in self.repos:
            repo_templates = await self._fetch_repo_templates(repo_path)
            templates.extend(repo_templates)

        return templates

    async def _fetch_repo_templates(self, repo_path: str) -> List[TemplateMetadata]:
        """Fetch templates from a single GitHub repo"""
        templates = []

        # Parse repo path: "owner/repo" or "owner/repo/path/to/templates"
        parts = repo_path.split("/")
        if len(parts) < 2:
            return []

        owner, repo = parts[0], parts[1]
        path = "/".join(parts[2:]) if len(parts) > 2 else "workflows"

        try:
            # List files in repo
            url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
            response = await self.client.get(url, headers=self.headers)

            if response.status_code != 200:
                return []

            files = response.json()

            # Find all .json workflow files
            for file_info in files:
                if file_info["type"] == "file" and file_info["name"].endswith(".json"):
                    template = await self._fetch_workflow_file(
                        owner, repo, file_info["path"], file_info
                    )
                    if template:
                        templates.append(template)
                        self.cache[template.id] = template

        except Exception as e:
            print(f"Error fetching from {repo_path}: {e}")

        return templates

    async def _fetch_workflow_file(
        self, owner: str, repo: str, file_path: str, file_info: Dict
    ) -> Optional[TemplateMetadata]:
        """Fetch and parse a workflow JSON file from GitHub"""
        try:
            # Get file content
            url = file_info["download_url"]
            response = await self.client.get(url)

            if response.status_code != 200:
                return None

            workflow_data = response.json()

            # Generate template ID
            template_id = f"github_{owner}_{repo}_{file_info['name'].replace('.json', '')}"

            return self.normalize_template(workflow_data, template_id, owner, repo, file_path)

        except Exception as e:
            print(f"Error fetching workflow file {file_path}: {e}")
            return None

    async def get_template(self, template_id: str) -> Optional[TemplateMetadata]:
        """Get specific template"""
        if template_id in self.cache:
            return self.cache[template_id]

        # Try to fetch from GitHub
        await self.refresh()
        return self.cache.get(template_id)

    async def search_templates(self, query: str) -> List[TemplateMetadata]:
        """Search templates"""
        query_lower = query.lower()
        all_templates = await self.fetch_templates()

        results = []
        for template in all_templates:
            if (query_lower in template.name.lower() or
                query_lower in template.description.lower() or
                query_lower in template.category.lower() or
                any(query_lower in tag.lower() for tag in template.tags)):
                results.append(template)

        return results

    async def refresh(self) -> int:
        """Refresh template cache"""
        templates = await self.fetch_templates()
        return len(templates)

    def normalize_template(
        self, workflow_data: Dict, template_id: str, owner: str, repo: str, file_path: str
    ) -> TemplateMetadata:
        """Convert GitHub workflow to TemplateMetadata"""
        name = workflow_data.get("name", file_path.split("/")[-1])
        description = workflow_data.get("meta", {}).get("description", "")

        nodes = workflow_data.get("nodes", [])
        connections = workflow_data.get("connections", {})
        settings = workflow_data.get("settings", {})

        # Extract tags from workflow or use defaults
        tags = workflow_data.get("tags", [])
        if isinstance(tags, list) and tags and isinstance(tags[0], dict):
            tags = [tag.get("name", "") for tag in tags]

        # Analyze complexity
        node_count = len(nodes)
        complexity = "beginner" if node_count < 5 else "intermediate" if node_count < 10 else "advanced"

        # Extract trigger type
        trigger_type = None
        for node in nodes:
            node_type = node.get("type", "")
            if "trigger" in node_type.lower():
                trigger_type = node_type
                break

        # Check for credentials
        uses_credentials = any(node.get("credentials") for node in nodes)

        # Check for error handling
        has_error_handling = any(
            "error" in node.get("type", "").lower() or
            node.get("continueOnFail", False)
            for node in nodes
        )

        # Determine category
        category = "integration"
        if any(tag in ["api", "http", "webhook"] for tag in tags):
            category = "api"
        elif any(tag in ["database", "postgres", "mysql"] for tag in tags):
            category = "database"
        elif any(tag in ["reporting", "dashboard"] for tag in tags):
            category = "reporting"

        return TemplateMetadata(
            id=template_id,
            source=self.source_name,
            name=name,
            description=description,
            category=category,
            tags=tags,
            n8n_version=">=1.0",
            template_version="1.0.0",
            nodes=nodes,
            connections=connections,
            settings=settings,
            complexity=complexity,
            node_count=node_count,
            estimated_setup_time=f"{node_count * 3} minutes",
            trigger_type=trigger_type,
            author=owner,
            source_url=f"https://github.com/{owner}/{repo}/blob/main/{file_path}",
            created_at=datetime.now(),
            has_error_handling=has_error_handling,
            has_documentation=bool(description),
            uses_credentials=uses_credentials
        )

    def add_repo(self, repo_path: str):
        """Add a new GitHub repo to fetch from"""
        if repo_path not in self.repos:
            self.repos.append(repo_path)

    def remove_repo(self, repo_path: str):
        """Remove a GitHub repo"""
        if repo_path in self.repos:
            self.repos.remove(repo_path)

    async def discover_repos(
        self,
        query: str = "n8n workflows",
        limit: int = 10
    ) -> List[Dict]:
        """
        Discover GitHub repositories containing n8n workflows

        Uses GitHub Search API to find:
        - Repos with "n8n" in name/description
        - Topics: n8n, n8n-workflows, automation
        - Contains .json workflow files

        Args:
            query: Search query
            limit: Max repos to discover

        Returns:
            List of repo metadata dicts
        """
        repos = []

        try:
            # Search for n8n-related repositories
            search_url = "https://api.github.com/search/repositories"
            params = {
                "q": f"{query} in:name,description,readme topic:n8n",
                "sort": "stars",
                "order": "desc",
                "per_page": min(limit, 100)  # GitHub API max
            }

            response = await self.client.get(search_url, headers=self.headers, params=params)

            if response.status_code == 200:
                data = response.json()
                for repo in data.get("items", [])[:limit]:
                    repos.append({
                        "owner": repo["owner"]["login"],
                        "name": repo["name"],
                        "full_name": repo["full_name"],
                        "description": repo.get("description", ""),
                        "stars": repo.get("stargazers_count", 0),
                        "url": repo["html_url"],
                        "default_branch": repo.get("default_branch", "main"),
                        "topics": repo.get("topics", []),
                        "language": repo.get("language"),
                        "updated_at": repo.get("updated_at")
                    })
            elif response.status_code == 403:
                print("GitHub API rate limit exceeded. Consider using a GitHub token.")
            else:
                print(f"GitHub search failed: {response.status_code}")

        except Exception as e:
            print(f"Error discovering GitHub repos: {e}")

        return repos

    async def fetch_workflows_from_discovered_repo(
        self,
        repo_info: Dict
    ) -> List[TemplateMetadata]:
        """
        Fetch workflows from a discovered repository

        Searches common n8n workflow paths:
        - .n8n/workflows/
        - workflows/
        - n8n-workflows/
        - root directory (*.json)

        Args:
            repo_info: Repository metadata from discover_repos()

        Returns:
            List of TemplateMetadata objects
        """
        owner = repo_info["owner"]
        repo = repo_info["name"]
        branch = repo_info.get("default_branch", "main")

        templates = []

        # Common paths for n8n workflows
        search_paths = [
            ".n8n/workflows",
            "workflows",
            "n8n-workflows",
            "n8n/workflows",
            ""  # Root directory
        ]

        for path in search_paths:
            try:
                url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
                params = {"ref": branch}

                response = await self.client.get(url, headers=self.headers, params=params)

                if response.status_code == 200:
                    contents = response.json()

                    # Handle single file vs directory listing
                    if not isinstance(contents, list):
                        contents = [contents]

                    for item in contents:
                        # Only process .json files
                        if item["type"] == "file" and item["name"].endswith(".json"):
                            # Fetch the actual workflow file
                            template = await self._fetch_workflow_from_url(
                                item["download_url"],
                                owner,
                                repo,
                                item["path"],
                                repo_info
                            )

                            if template:
                                templates.append(template)
                                self.cache[template.id] = template

                                # Cache in persistent storage
                                self._cache_template(template)

            except Exception as e:
                # Path doesn't exist - continue to next path
                continue

        return templates

    async def _fetch_workflow_from_url(
        self,
        download_url: str,
        owner: str,
        repo: str,
        file_path: str,
        repo_info: Dict
    ) -> Optional[TemplateMetadata]:
        """Fetch and validate workflow from download URL"""
        try:
            response = await self.client.get(download_url)

            if response.status_code != 200:
                return None

            workflow_data = response.json()

            # Validate it's an n8n workflow
            if not self._is_valid_n8n_workflow(workflow_data):
                return None

            # Generate unique template ID
            file_name = file_path.split("/")[-1].replace(".json", "")
            template_id = f"github_{owner}_{repo}_{file_name}".replace("-", "_").lower()

            return self._normalize_github_template(
                workflow_data,
                template_id,
                owner,
                repo,
                file_path,
                repo_info
            )

        except Exception as e:
            print(f"Error fetching workflow from {download_url}: {e}")
            return None

    def _is_valid_n8n_workflow(self, workflow: Dict) -> bool:
        """Validate if JSON is a valid n8n workflow"""
        return (
            isinstance(workflow, dict) and
            "nodes" in workflow and
            "connections" in workflow and
            isinstance(workflow["nodes"], list)
        )

    def _normalize_github_template(
        self,
        workflow_data: Dict,
        template_id: str,
        owner: str,
        repo: str,
        file_path: str,
        repo_info: Dict
    ) -> TemplateMetadata:
        """Convert GitHub workflow to TemplateMetadata with enhanced metadata"""
        name = workflow_data.get("name", file_path.split("/")[-1])
        description = workflow_data.get("meta", {}).get("description", "")

        # Use repo description if workflow has none
        if not description:
            description = f"{repo_info.get('description', '')} (from {repo_info['full_name']})"

        nodes = workflow_data.get("nodes", [])
        connections = workflow_data.get("connections", {})

        # Extract tags from repo topics + workflow tags
        tags = list(set(repo_info.get("topics", []) + workflow_data.get("tags", [])))

        # Enhanced complexity detection
        node_count = len(nodes)
        connection_count = len(connections)

        if node_count <= 3:
            complexity = "beginner"
        elif node_count <= 8 and connection_count <= 10:
            complexity = "intermediate"
        else:
            complexity = "advanced"

        # Detect trigger type
        trigger_type = None
        for node in nodes:
            node_type = node.get("type", "")
            if "trigger" in node_type.lower():
                trigger_type = node_type.split(".")[-1] if "." in node_type else node_type
                break

        # Check for error handling
        has_error_handling = any(
            "error" in node.get("type", "").lower() or
            node.get("continueOnFail", False) or
            "onError" in node
            for node in nodes
        )

        # Check for credentials
        uses_credentials = any(node.get("credentials") for node in nodes)

        # Smart category detection
        category = self._detect_category_from_workflow(nodes, tags, repo_info)

        return TemplateMetadata(
            id=template_id,
            source=self.source_name,
            name=name,
            description=description,
            category=category,
            tags=tags,
            n8n_version=">=1.0",
            template_version="1.0.0",
            nodes=nodes,
            connections=connections,
            settings=workflow_data.get("settings", {}),
            complexity=complexity,
            node_count=node_count,
            estimated_setup_time=self._estimate_setup_time(complexity, node_count),
            trigger_type=trigger_type,
            author=owner,
            source_url=f"https://github.com/{owner}/{repo}/blob/{repo_info.get('default_branch', 'main')}/{file_path}",
            created_at=datetime.now(),
            has_error_handling=has_error_handling,
            has_documentation=bool(description or repo_info.get("description")),
            uses_credentials=uses_credentials
        )

    def _detect_category_from_workflow(
        self,
        nodes: List[Dict],
        tags: List[str],
        repo_info: Dict
    ) -> str:
        """Smart category detection from nodes, tags, and repo info"""
        # Extract node types
        node_types = [node.get("type", "").lower() for node in nodes]
        all_text = " ".join(node_types + tags + [repo_info.get("description", "")]).lower()

        # Category detection rules
        categories = {
            "api": ["http", "webhook", "api", "rest"],
            "data_pipeline": ["database", "postgres", "mysql", "mongodb", "etl", "transform"],
            "communication": ["slack", "email", "telegram", "discord", "teams", "notification"],
            "automation": ["schedule", "cron", "trigger", "workflow"],
            "ai": ["openai", "anthropic", "langchain", "gpt", "claude", "ai", "llm"],
            "integration": ["github", "gitlab", "jira", "salesforce", "integration"],
            "monitoring": ["alert", "monitor", "health", "status"],
            "reporting": ["report", "dashboard", "analytics"],
        }

        for category, keywords in categories.items():
            if any(keyword in all_text for keyword in keywords):
                return category

        return "other"

    def _estimate_setup_time(self, complexity: str, node_count: int) -> str:
        """Estimate setup time based on complexity and node count"""
        if complexity == "beginner":
            return "5-10 minutes"
        elif complexity == "intermediate":
            return f"{max(15, node_count * 2)} minutes"
        else:
            return f"{max(30, node_count * 3)} minutes"

    def _cache_template(self, template: TemplateMetadata):
        """Cache template in persistent storage"""
        logger.info(f"🔵 [GITHUB] _cache_template called for: {template.id}")
        logger.info(f"   Name: {template.name}")
        logger.info(f"   Source: {template.source}")
        logger.info(f"   Category: {template.category}")
        logger.info(f"   Tags: {template.tags}")
        logger.info(f"   Cache instance ID: {id(self.persistent_cache)}")

        template_dict = {
            "id": template.id,
            "source": template.source,
            "name": template.name,
            "description": template.description,
            "category": template.category,
            "tags": template.tags,
            "nodes": template.nodes,
            "author": template.author,
            "source_url": template.source_url,
            "totalViews": 0,  # GitHub doesn't provide view count
            "createdAt": template.created_at.isoformat() if template.created_at else None,
            "metadata": {
                "complexity": template.complexity,
                "node_count": template.node_count,
                "estimated_setup_time": template.estimated_setup_time,
                "trigger_type": template.trigger_type,
                "has_error_handling": template.has_error_handling,
                "has_documentation": template.has_documentation,
                "uses_credentials": template.uses_credentials,
            }
        }

        logger.info(f"   Calling persistent_cache.add_template()...")
        result = self.persistent_cache.add_template(template_dict)
        logger.info(f"   add_template returned: {result}")

        if result:
            logger.info(f"✅ [GITHUB] Successfully cached: {template.id}")
        else:
            logger.error(f"❌ [GITHUB] FAILED to cache: {template.id}")
