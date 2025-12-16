"""GitHub Template Source"""
import httpx
import json
import base64
from typing import List, Dict, Optional
from datetime import datetime
from .base import TemplateSource, TemplateMetadata


class GitHubSource(TemplateSource):
    """Fetch templates from GitHub repositories"""

    def __init__(self, repos: List[str] = None, github_token: Optional[str] = None):
        """
        Initialize GitHub source

        Args:
            repos: List of GitHub repos in format "owner/repo" or "owner/repo/path"
            github_token: Optional GitHub personal access token for private repos
        """
        super().__init__("github")
        self.repos = repos or []
        self.github_token = github_token
        self.cache: Dict[str, TemplateMetadata] = {}
        self.client = httpx.AsyncClient(timeout=30.0)

        self.headers = {"Accept": "application/vnd.github+json"}
        if github_token:
            self.headers["Authorization"] = f"Bearer {github_token}"

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
