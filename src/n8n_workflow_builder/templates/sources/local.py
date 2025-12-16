"""Local Template Source"""
import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from .base import TemplateSource, TemplateMetadata


class LocalSource(TemplateSource):
    """Fetch templates from local filesystem (private repos, custom templates)"""

    def __init__(self, directories: List[str] = None):
        """
        Initialize local source

        Args:
            directories: List of local directories containing workflow JSON files
        """
        super().__init__("local")
        self.directories = directories or []
        self.cache: Dict[str, TemplateMetadata] = {}

    async def fetch_templates(self) -> List[TemplateMetadata]:
        """Fetch all templates from configured local directories"""
        templates = []

        for directory in self.directories:
            dir_templates = await self._fetch_directory_templates(directory)
            templates.extend(dir_templates)

        return templates

    async def _fetch_directory_templates(self, directory: str) -> List[TemplateMetadata]:
        """Fetch templates from a single directory"""
        templates = []
        dir_path = Path(directory)

        if not dir_path.exists() or not dir_path.is_dir():
            return []

        # Find all .json files recursively
        for json_file in dir_path.rglob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    workflow_data = json.load(f)

                # Skip if not a valid n8n workflow
                if "nodes" not in workflow_data:
                    continue

                template = self.normalize_template(workflow_data, json_file, directory)
                if template:
                    templates.append(template)
                    self.cache[template.id] = template

            except Exception as e:
                print(f"Error loading template from {json_file}: {e}")
                continue

        return templates

    async def get_template(self, template_id: str) -> Optional[TemplateMetadata]:
        """Get specific template"""
        if template_id in self.cache:
            return self.cache[template_id]

        # Try to refresh and find it
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
        self, workflow_data: Dict, file_path: Path, base_directory: str
    ) -> Optional[TemplateMetadata]:
        """Convert local workflow to TemplateMetadata"""
        try:
            name = workflow_data.get("name", file_path.stem)
            description = workflow_data.get("meta", {}).get("description", "")

            nodes = workflow_data.get("nodes", [])
            connections = workflow_data.get("connections", {})
            settings = workflow_data.get("settings", {})

            # Extract tags
            tags = workflow_data.get("tags", [])
            if isinstance(tags, list) and tags and isinstance(tags[0], dict):
                tags = [tag.get("name", "") for tag in tags]

            # Generate template ID from file path
            relative_path = file_path.relative_to(base_directory)
            template_id = f"local_{str(relative_path).replace('/', '_').replace('.json', '')}"

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
            category = "custom"
            if any(tag in ["api", "http", "webhook"] for tag in tags):
                category = "api"
            elif any(tag in ["database", "postgres", "mysql"] for tag in tags):
                category = "database"
            elif any(tag in ["reporting", "dashboard"] for tag in tags):
                category = "reporting"

            # Get file stats
            file_stats = file_path.stat()
            created_at = datetime.fromtimestamp(file_stats.st_ctime)
            updated_at = datetime.fromtimestamp(file_stats.st_mtime)

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
                author="Local",
                source_url=str(file_path),
                created_at=created_at,
                updated_at=updated_at,
                has_error_handling=has_error_handling,
                has_documentation=bool(description),
                uses_credentials=uses_credentials
            )

        except Exception as e:
            print(f"Error normalizing template from {file_path}: {e}")
            return None

    def add_directory(self, directory: str):
        """Add a new directory to scan"""
        if directory not in self.directories:
            self.directories.append(directory)

    def remove_directory(self, directory: str):
        """Remove a directory"""
        if directory in self.directories:
            self.directories.remove(directory)
