"""N8n Official Template Source"""
import httpx
from typing import List, Dict, Optional
from datetime import datetime
from .base import TemplateSource, TemplateMetadata


class N8nOfficialSource(TemplateSource):
    """Fetch templates from official n8n template repository"""

    def __init__(self):
        super().__init__("n8n_official")
        self.base_url = "https://api.n8n.io/api/templates"
        self.cache: Dict[str, TemplateMetadata] = {}
        self.client = httpx.AsyncClient(timeout=30.0)

    async def fetch_templates(self) -> List[TemplateMetadata]:
        """Fetch all official n8n templates"""
        try:
            # Try official API first
            response = await self.client.get(f"{self.base_url}/search")
            if response.status_code == 200:
                templates_data = response.json().get("workflows", [])
                templates = []
                for raw in templates_data:
                    template = self.normalize_template(raw)
                    self.cache[template.id] = template
                    templates.append(template)
                return templates
        except Exception:
            pass

        # Fallback: Use hardcoded official templates
        return self._get_hardcoded_templates()

    async def get_template(self, template_id: str) -> Optional[TemplateMetadata]:
        """Get specific template"""
        if template_id in self.cache:
            return self.cache[template_id]

        try:
            response = await self.client.get(f"{self.base_url}/{template_id}")
            if response.status_code == 200:
                template = self.normalize_template(response.json())
                self.cache[template_id] = template
                return template
        except Exception:
            pass

        return None

    async def search_templates(self, query: str) -> List[TemplateMetadata]:
        """Search templates"""
        query_lower = query.lower()
        all_templates = await self.fetch_templates()

        results = []
        for template in all_templates:
            # Search in name, description, tags, category
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

    def normalize_template(self, raw: Dict) -> TemplateMetadata:
        """Convert n8n API response to TemplateMetadata"""
        # Extract basic info
        template_id = raw.get("id", raw.get("name", "unknown"))
        name = raw.get("name", "Unknown Template")
        description = raw.get("description", "")

        # Extract workflow structure
        nodes = raw.get("nodes", [])
        connections = raw.get("connections", {})
        settings = raw.get("settings", {})

        # Extract metadata
        tags = raw.get("tags", [])
        if isinstance(tags, list) and tags and isinstance(tags[0], dict):
            tags = [tag.get("name", "") for tag in tags]

        category = raw.get("category", ["other"])[0] if raw.get("category") else "other"

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

        return TemplateMetadata(
            id=template_id,
            source=self.source_name,
            name=name,
            description=description,
            category=category,
            tags=tags,
            n8n_version=">=1.0",  # Assume compatible
            template_version="1.0.0",
            nodes=nodes,
            connections=connections,
            settings=settings,
            complexity=complexity,
            node_count=node_count,
            estimated_setup_time=f"{node_count * 3} minutes",
            trigger_type=trigger_type,
            author=raw.get("author", "n8n Team"),
            source_url=raw.get("url", "https://n8n.io/workflows"),
            created_at=datetime.now(),
            has_error_handling=has_error_handling,
            has_documentation=bool(description),
            uses_credentials=uses_credentials
        )

    def _get_hardcoded_templates(self) -> List[TemplateMetadata]:
        """Fallback hardcoded official templates"""
        from ...templates.recommender import WORKFLOW_TEMPLATES

        templates = []
        for template_id, template_dict in WORKFLOW_TEMPLATES.items():
            # Convert node names to full node objects
            full_nodes = []
            for node_info in template_dict["nodes"]:
                if isinstance(node_info, dict):
                    full_nodes.append(node_info)
                else:
                    # Node info is dict with name and type
                    full_nodes.append({
                        "name": node_info["name"],
                        "type": node_info["type"],
                        "position": [0, 0],
                        "parameters": {}
                    })

            # Determine trigger type
            trigger_type = None
            for node in full_nodes:
                if "trigger" in node.get("type", "").lower():
                    trigger_type = node.get("type")
                    break

            template = TemplateMetadata(
                id=template_id,
                source=self.source_name,
                name=template_dict["name"],
                description=template_dict["description"],
                category=template_dict["category"],
                tags=template_dict["tags"],
                n8n_version=">=1.0",
                template_version="1.0.0",
                nodes=full_nodes,
                connections={},
                settings={},
                complexity=template_dict.get("complexity", template_dict.get("difficulty", "intermediate")),
                node_count=len(full_nodes),
                estimated_setup_time=template_dict["estimated_time"],
                trigger_type=trigger_type,
                author="n8n Team",
                source_url="https://n8n.io/workflows",
                has_documentation=True
            )
            templates.append(template)
            self.cache[template.id] = template

        return templates
