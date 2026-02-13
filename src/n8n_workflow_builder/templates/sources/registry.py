"""Template Registry - Aggregates all sources"""
from typing import List, Dict, Optional
from .base import TemplateSource, TemplateMetadata
from .n8n_official import N8nOfficialSource
from .github import GitHubSource
from .local import LocalSource


class TemplateRegistry:
    """Central registry for all template sources"""

    def __init__(self):
        self.sources: Dict[str, TemplateSource] = {}
        self.cache: Dict[str, TemplateMetadata] = {}

        # Initialize default sources
        self.register_source("n8n_official", N8nOfficialSource())

    def register_source(self, name: str, source: TemplateSource):
        """Register a new template source"""
        self.sources[name] = source

    def unregister_source(self, name: str):
        """Remove a template source"""
        if name in self.sources:
            del self.sources[name]

    async def fetch_all_templates(self) -> List[TemplateMetadata]:
        """Fetch templates from all sources"""
        all_templates = []

        for source_name, source in self.sources.items():
            try:
                templates = await source.fetch_templates()
                all_templates.extend(templates)

                # Update cache
                for template in templates:
                    self.cache[template.id] = template

            except Exception as e:
                print(f"Error fetching from source {source_name}: {e}")

        return all_templates

    async def get_template(self, template_id: str) -> Optional[TemplateMetadata]:
        """Get a specific template by ID"""
        # Check cache first
        if template_id in self.cache:
            return self.cache[template_id]

        # Try each source
        for source in self.sources.values():
            try:
                template = await source.get_template(template_id)
                if template:
                    self.cache[template_id] = template
                    return template
            except Exception:
                continue

        return None

    async def search_templates(self, query: str) -> List[TemplateMetadata]:
        """Search templates across all sources"""
        all_results = []

        for source in self.sources.values():
            try:
                results = await source.search_templates(query)
                all_results.extend(results)
            except Exception as e:
                print(f"Error searching in source: {e}")

        # Deduplicate by template ID
        seen = set()
        unique_results = []
        for template in all_results:
            if template.id not in seen:
                seen.add(template.id)
                unique_results.append(template)

        return unique_results

    async def refresh_all(self) -> Dict[str, int]:
        """Refresh all sources, return count per source"""
        counts = {}

        for source_name, source in self.sources.items():
            try:
                count = await source.refresh()
                counts[source_name] = count
            except Exception as e:
                print(f"Error refreshing source {source_name}: {e}")
                counts[source_name] = 0

        return counts

    def filter_templates(
        self,
        templates: List[TemplateMetadata],
        category: Optional[str] = None,
        complexity: Optional[str] = None,
        tags: Optional[List[str]] = None,
        source: Optional[str] = None,
        has_error_handling: Optional[bool] = None
    ) -> List[TemplateMetadata]:
        """Filter templates by various criteria"""
        filtered = templates

        if category:
            filtered = [t for t in filtered if t.category == category]

        if complexity:
            filtered = [t for t in filtered if t.complexity == complexity]

        if tags:
            filtered = [
                t for t in filtered
                if any(tag in t.tags for tag in tags)
            ]

        if source:
            filtered = [t for t in filtered if t.source == source]

        if has_error_handling is not None:
            filtered = [t for t in filtered if t.has_error_handling == has_error_handling]

        return filtered

    def get_sources(self) -> List[str]:
        """Get list of registered source names"""
        return list(self.sources.keys())

    def get_statistics(self) -> Dict:
        """Get registry statistics"""
        templates = list(self.cache.values())

        stats = {
            "total_templates": len(templates),
            "sources": len(self.sources),
            "by_source": {},
            "by_category": {},
            "by_complexity": {},
            "with_error_handling": sum(1 for t in templates if t.has_error_handling),
            "with_documentation": sum(1 for t in templates if t.has_documentation),
            "uses_credentials": sum(1 for t in templates if t.uses_credentials)
        }

        # Count by source
        for template in templates:
            source = template.source
            stats["by_source"][source] = stats["by_source"].get(source, 0) + 1

        # Count by category
        for template in templates:
            category = template.category
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1

        # Count by complexity
        for template in templates:
            complexity = template.complexity
            stats["by_complexity"][complexity] = stats["by_complexity"].get(complexity, 0) + 1

        return stats


# Global singleton registry instance
template_registry = TemplateRegistry()
