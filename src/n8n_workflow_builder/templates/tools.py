"""
Template MCP Tools
Provides MCP tools for template sync, search, and management
"""
import asyncio
from typing import Dict, List, Optional
from .sources import N8nOfficialSource, GitHubSource
from .cache import TemplateCache
from .intent_matcher import IntentMatcher


class TemplateManager:
    """Manager for template operations exposed via MCP tools"""

    def __init__(self):
        # Initialize cache first (shared by all sources)
        self.cache = TemplateCache()

        # Initialize sources with shared cache
        self.n8n_source = N8nOfficialSource(cache_path=None)  # Will create default cache
        self.github_source = GitHubSource(cache_path=None)  # Will create default cache

        # Override their caches with our shared instance
        self.n8n_source.persistent_cache = self.cache
        self.github_source.persistent_cache = self.cache

        self.intent_matcher = IntentMatcher()

    async def sync_templates(
        self,
        source: str = "all",
        force: bool = False
    ) -> Dict:
        """
        Sync templates from specified source(s)

        Args:
            source: Source to sync ("all", "n8n_official", "github", "community")
            force: Force sync even if recently synced

        Returns:
            Sync results with counts and status
        """
        results = {
            "synced_sources": [],
            "total_templates": 0,
            "errors": []
        }

        # Handle n8n_official source
        if source in ["all", "n8n_official"]:
            try:
                # Force sync by clearing sync status if needed
                if force:
                    # Delete sync status to force re-sync
                    cursor = self.cache.conn.cursor()
                    cursor.execute("DELETE FROM sync_status WHERE source = ?", ("n8n_official",))
                    self.cache.conn.commit()

                # Fetch templates (will sync if needed)
                templates = await self.n8n_source.fetch_templates()

                results["synced_sources"].append("n8n_official")
                results["total_templates"] += len(templates)
            except Exception as e:
                results["errors"].append(f"n8n_official: {str(e)}")

        # Handle github source
        if source in ["all", "github"]:
            try:
                # Force sync by clearing sync status if needed
                if force:
                    cursor = self.cache.conn.cursor()
                    cursor.execute("DELETE FROM sync_status WHERE source = ?", ("github",))
                    self.cache.conn.commit()

                # Fetch templates from configured GitHub repos
                templates = await self.github_source.fetch_templates()

                results["synced_sources"].append("github")
                results["total_templates"] += len(templates)
            except Exception as e:
                results["errors"].append(f"github: {str(e)}")

        # Community source not yet implemented
        if source in ["all", "community"]:
            results["errors"].append("community: Not yet implemented")

        return results

    async def search_templates(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        node_types: Optional[List[str]] = None,
        source: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict]:
        """
        Search templates with various filters

        Args:
            query: Full-text search query (uses FTS5)
            category: Filter by category
            tags: Filter by tags (match any)
            node_types: Filter by node types used
            source: Filter by source ("n8n_official", "github", etc.)
            limit: Max results to return

        Returns:
            List of matching templates
        """
        # Use n8n_source.search_templates for query-based search
        if query:
            templates = await self.n8n_source.search_templates(query)
            # Convert to dicts
            return [self._template_to_dict(t) for t in templates[:limit]]

        # Use cache.search for filter-based search
        results = self.cache.search(
            query=query,
            source=source,
            category=category,
            tags=tags,
            node_types=node_types,
            limit=limit
        )
        return results

    def get_template_stats(self) -> Dict:
        """
        Get statistics about cached templates

        Returns:
            Dict with counts, popular tags, categories, etc.
        """
        stats = self.cache.get_stats()

        # Add sync status for all sources
        sync_statuses = {}
        for source in ["n8n_official", "github", "community"]:
            status = self.cache.get_sync_status(source)
            if status:
                sync_statuses[source] = {
                    "last_sync": status["last_sync"],
                    "template_count": status["template_count"],
                    "success": bool(status["success"]),
                    "error": status["error_message"]
                }
            else:
                sync_statuses[source] = {"synced": False}

        stats["sync_status"] = sync_statuses
        return stats

    def get_popular_templates(self, limit: int = 10) -> List[Dict]:
        """
        Get most popular templates by view count

        Args:
            limit: Max templates to return

        Returns:
            List of popular templates
        """
        return self.cache.get_popular_templates(limit=limit)

    def get_recent_templates(self, limit: int = 10) -> List[Dict]:
        """
        Get most recently added templates

        Args:
            limit: Max templates to return

        Returns:
            List of recent templates
        """
        return self.cache.get_recent_templates(limit=limit)

    async def search_templates_by_intent(
        self,
        query: str,
        min_score: float = 0.3,
        limit: int = 20
    ) -> List[Dict]:
        """
        Search templates using intent-based semantic matching

        Args:
            query: Natural language description of what you want to build
            min_score: Minimum intent match score (0.0-1.0)
            limit: Max results to return

        Returns:
            List of templates with match scores
        """
        # Get all cached templates
        all_templates = self.cache.search(limit=1000)

        # Use intent matcher to score and rank
        matches = self.intent_matcher.match(
            query=query,
            templates=all_templates,
            min_score=min_score,
            limit=limit
        )

        # Return templates with scores
        return [
            {
                **template,
                "match_score": score,
                "match_percentage": f"{int(score * 100)}%"
            }
            for template, score in matches
        ]

    def explain_template_match(self, query: str, template_id: str) -> Dict:
        """
        Explain why a template matches a query

        Args:
            query: Natural language query
            template_id: Template ID to explain

        Returns:
            Detailed explanation of match scoring
        """
        # Get template
        template = self.cache.get_template(template_id)
        if not template:
            return {"error": "Template not found"}

        # Extract intent from query
        intent = self.intent_matcher.extractor.extract(query)

        # Get detailed explanation
        return self.intent_matcher.explain_match(intent, template)

    async def discover_github_templates(
        self,
        query: str = "n8n workflows",
        limit: int = 10
    ) -> List[Dict]:
        """
        Discover n8n workflows in GitHub repositories

        Args:
            query: Search query (e.g., 'n8n automation')
            limit: Max repos to discover

        Returns:
            List of discovered repositories with metadata
        """
        return await self.github_source.discover_repos(query=query, limit=limit)

    async def import_github_repo(
        self,
        repo_full_name: str,
        add_to_sync: bool = True
    ) -> Dict:
        """
        Import templates from a GitHub repository

        Args:
            repo_full_name: Repository in format "owner/repo"
            add_to_sync: Whether to add repo to regular sync list

        Returns:
            Import results with template count
        """
        # Add repo to source if requested
        if add_to_sync:
            self.github_source.add_repo(repo_full_name)

        # Fetch repo info first
        repos = await self.github_source.discover_repos(query=repo_full_name, limit=1)
        if not repos:
            return {
                "success": False,
                "error": "Repository not found or not accessible"
            }

        repo_info = repos[0]

        # Fetch workflows from repo
        templates = await self.github_source.fetch_workflows_from_discovered_repo(repo_info)

        return {
            "success": True,
            "repo": repo_full_name,
            "templates_imported": len(templates),
            "templates": [self._template_to_dict(t) for t in templates],
            "added_to_sync": add_to_sync
        }

    async def get_template_by_id(self, template_id: str) -> Optional[Dict]:
        """
        Get specific template by ID

        Args:
            template_id: Template identifier

        Returns:
            Template data or None if not found
        """
        # Try cache first
        cached = self.cache.get_template(template_id)
        if cached:
            return cached

        # Try fetching from source
        template = await self.n8n_source.get_template(template_id)
        if template:
            return self._template_to_dict(template)

        return None

    def clear_cache(self, source: Optional[str] = None) -> Dict:
        """
        Clear template cache

        Args:
            source: Specific source to clear, or None for all

        Returns:
            Result with cleared count
        """
        if source:
            self.cache.clear_cache(source)
            return {"cleared": source}
        else:
            # Clear all sources
            for src in ["n8n_official", "github", "community"]:
                self.cache.clear_cache(src)
            return {"cleared": "all"}

    def _template_to_dict(self, template) -> Dict:
        """Convert TemplateMetadata to dict"""
        return {
            "id": template.id,
            "source": template.source,
            "name": template.name,
            "description": template.description,
            "category": template.category,
            "tags": template.tags,
            "nodes": template.nodes,
            "complexity": getattr(template, "complexity", "intermediate"),
            "node_count": getattr(template, "node_count", 0),
            "estimated_setup_time": getattr(template, "estimated_setup_time", "Unknown"),
            "trigger_type": getattr(template, "trigger_type", None),
            "author": getattr(template, "author", "Unknown"),
            "source_url": getattr(template, "source_url", ""),
            "has_error_handling": getattr(template, "has_error_handling", False),
            "has_documentation": getattr(template, "has_documentation", False),
        }
