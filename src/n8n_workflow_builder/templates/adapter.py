"""
Template Adaptation - From Community Template to Production-Ready Workflow

Transforms:
  "Community workflow from 2022"
→ "2025-compatible, secure workflow"

Key adaptations:
1. Replace placeholders with user values
2. Abstract credentials
3. Modernize deprecated nodes
4. Add error handling
5. Security hardening
"""
import re
from typing import Dict, List, Optional
from copy import deepcopy
from .sources.base import TemplateMetadata


class TemplateAdapter:
    """Adapts templates for modern deployment"""

    # Deprecated node mappings (old → new)
    DEPRECATED_NODES = {
        "n8n-nodes-base.httpRequest": "n8n-nodes-base.httpRequest",  # Same but params changed
        "n8n-nodes-base.function": "n8n-nodes-base.code",
        "n8n-nodes-base.functionItem": "n8n-nodes-base.code"
    }

    # Placeholder patterns
    PLACEHOLDER_PATTERNS = [
        r"\{\{.*?\}\}",  # {{ placeholder }}
        r"\$\{.*?\}",    # ${placeholder}
        r"<.*?>",        # <placeholder>
        r"YOUR_.*",      # YOUR_API_KEY
        r"EXAMPLE_.*",   # EXAMPLE_URL
    ]

    def __init__(self):
        self.adaptation_log: List[str] = []

    def adapt_template(
        self,
        template: TemplateMetadata,
        replacements: Optional[Dict[str, str]] = None,
        add_error_handling: bool = True,
        modernize_nodes: bool = True,
        abstract_credentials: bool = True
    ) -> Dict:
        """
        Adapt template to be production-ready

        Args:
            template: Template to adapt
            replacements: Placeholder replacements {"API_URL": "https://api.example.com"}
            add_error_handling: Add error handling if missing
            modernize_nodes: Replace deprecated nodes
            abstract_credentials: Replace hardcoded credentials

        Returns:
            Adapted workflow dict ready to deploy
        """
        self.adaptation_log = []
        replacements = replacements or {}

        # Deep copy to avoid modifying original
        adapted = {
            "name": template.name,
            "nodes": deepcopy(template.nodes),
            "connections": deepcopy(template.connections),
            "settings": deepcopy(template.settings)
        }

        # 1. Replace placeholders
        adapted["nodes"] = self._replace_placeholders(adapted["nodes"], replacements)

        # 2. Abstract credentials
        if abstract_credentials:
            adapted["nodes"] = self._abstract_credentials(adapted["nodes"])

        # 3. Modernize deprecated nodes
        if modernize_nodes:
            adapted["nodes"] = self._modernize_nodes(adapted["nodes"])

        # 4. Add error handling
        if add_error_handling:
            adapted["nodes"] = self._add_error_handling(adapted["nodes"])

        # 5. Security hardening
        adapted["nodes"] = self._security_hardening(adapted["nodes"])

        self.adaptation_log.append(f"✅ Template adapted successfully with {len(self.adaptation_log)} changes")

        return adapted

    def _replace_placeholders(self, nodes: List[Dict], replacements: Dict[str, str]) -> List[Dict]:
        """Replace placeholders in node parameters"""
        for node in nodes:
            parameters = node.get("parameters", {})

            # Recursively replace in parameters
            node["parameters"] = self._replace_in_dict(parameters, replacements)

        if replacements:
            self.adaptation_log.append(f"Replaced {len(replacements)} placeholder(s)")

        return nodes

    def _replace_in_dict(self, data: any, replacements: Dict[str, str]) -> any:
        """Recursively replace placeholders in dict/list/str"""
        if isinstance(data, dict):
            return {k: self._replace_in_dict(v, replacements) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._replace_in_dict(item, replacements) for item in data]
        elif isinstance(data, str):
            # Try to find placeholders
            for pattern in self.PLACEHOLDER_PATTERNS:
                matches = re.findall(pattern, data)
                for match in matches:
                    # Extract key from placeholder
                    key = re.sub(r'[{}$<>]', '', match).strip()

                    if key in replacements:
                        data = data.replace(match, replacements[key])

            return data
        else:
            return data

    def _abstract_credentials(self, nodes: List[Dict]) -> List[Dict]:
        """Replace hardcoded credentials with credential references"""
        for node in nodes:
            parameters = node.get("parameters", {})

            # Common credential fields
            credential_fields = [
                "apiKey", "api_key", "token", "password", "secret",
                "accessToken", "clientSecret", "privateKey"
            ]

            for field in credential_fields:
                if field in parameters:
                    value = parameters[field]

                    # Check if it looks like a hardcoded credential
                    if isinstance(value, str) and len(value) > 10 and not value.startswith("={{"):
                        # Move to credentials
                        node_type = node.get("type", "").replace("n8n-nodes-base.", "")

                        if "credentials" not in node:
                            node["credentials"] = {}

                        # Create credential reference
                        credential_name = f"{node_type}Api"
                        node["credentials"][credential_name] = {
                            "id": "CREDENTIAL_ID",  # User must configure
                            "name": f"{node.get('name', 'Node')} Credentials"
                        }

                        # Remove hardcoded value
                        del parameters[field]

                        self.adaptation_log.append(
                            f"⚠️  Abstracted hardcoded '{field}' in node '{node.get('name')}'"
                        )

        return nodes

    def _modernize_nodes(self, nodes: List[Dict]) -> List[Dict]:
        """Replace deprecated nodes with modern equivalents"""
        for node in nodes:
            node_type = node.get("type", "")

            if node_type in self.DEPRECATED_NODES:
                new_type = self.DEPRECATED_NODES[node_type]

                if new_type != node_type:
                    node["type"] = new_type
                    self.adaptation_log.append(
                        f"🔄 Modernized '{node.get('name')}': {node_type} → {new_type}"
                    )

                # Special handling for function → code migration
                if node_type == "n8n-nodes-base.function":
                    parameters = node.get("parameters", {})
                    if "functionCode" in parameters:
                        parameters["jsCode"] = parameters.pop("functionCode")

        return nodes

    def _add_error_handling(self, nodes: List[Dict]) -> List[Dict]:
        """Add error handling to nodes that don't have it"""
        error_prone_types = [
            "n8n-nodes-base.httprequest",
            "n8n-nodes-base.postgres",
            "n8n-nodes-base.mysql",
            "n8n-nodes-base.mongodb"
        ]

        for node in nodes:
            node_type = node.get("type", "").lower()

            # Check if node is error-prone and doesn't have error handling
            if any(prone in node_type for prone in error_prone_types):
                if not node.get("continueOnFail"):
                    node["continueOnFail"] = False  # Set explicit (don't continue by default)

                    # But ensure onError is set to stop workflow
                    node["onError"] = "stopWorkflow"

                    self.adaptation_log.append(
                        f"✨ Added error handling to '{node.get('name')}'"
                    )

        return nodes

    def _security_hardening(self, nodes: List[Dict]) -> List[Dict]:
        """Security hardening for common vulnerabilities"""
        for node in nodes:
            node_type = node.get("type", "").lower()
            parameters = node.get("parameters", {})

            # 1. Webhook security
            if "webhook" in node_type:
                if not parameters.get("authentication") or parameters.get("authentication") == "none":
                    parameters["authentication"] = "headerAuth"
                    parameters["headerAuth"] = {
                        "name": "X-Webhook-Token",
                        "value": "={{$env.WEBHOOK_TOKEN}}"
                    }

                    self.adaptation_log.append(
                        f"🔒 Added authentication to webhook '{node.get('name')}'"
                    )

            # 2. HTTP request security
            if "httprequest" in node_type:
                # Ensure timeout is set
                if "timeout" not in parameters:
                    parameters["timeout"] = 30000  # 30 seconds

                # Ensure retry is configured
                if "options" not in parameters:
                    parameters["options"] = {}

                if "retry" not in parameters["options"]:
                    parameters["options"]["retry"] = {
                        "maxRetries": 3,
                        "retryInterval": 1000
                    }

                    self.adaptation_log.append(
                        f"🔄 Added retry logic to HTTP request '{node.get('name')}'"
                    )

            # 3. Database security
            if any(db in node_type for db in ["postgres", "mysql", "mongodb"]):
                # Ensure credentials are used
                if "credentials" not in node or not node["credentials"]:
                    self.adaptation_log.append(
                        f"⚠️  Database node '{node.get('name')}' needs credentials configuration"
                    )

        return nodes

    def get_required_credentials(self, template: TemplateMetadata) -> List[Dict]:
        """Extract list of required credentials"""
        credentials = []
        seen = set()

        for node in template.nodes:
            node_credentials = node.get("credentials", {})

            for cred_type, cred_info in node_credentials.items():
                cred_id = f"{cred_type}_{cred_info.get('name', 'Unknown')}"

                if cred_id not in seen:
                    seen.add(cred_id)

                    credentials.append({
                        "type": cred_type,
                        "name": cred_info.get("name", "Unknown"),
                        "node": node.get("name", "Unknown"),
                        "required": True
                    })

        return credentials

    def get_placeholders(self, template: TemplateMetadata) -> List[Dict]:
        """Extract list of placeholders that need to be filled"""
        placeholders = []
        seen = set()

        for node in template.nodes:
            parameters = node.get("parameters", {})
            self._find_placeholders_in_dict(parameters, placeholders, seen, node.get("name", "Unknown"))

        return placeholders

    def _find_placeholders_in_dict(self, data: any, placeholders: List[Dict], seen: set, node_name: str):
        """Recursively find placeholders"""
        if isinstance(data, dict):
            for key, value in data.items():
                self._find_placeholders_in_dict(value, placeholders, seen, node_name)
        elif isinstance(data, list):
            for item in data:
                self._find_placeholders_in_dict(item, placeholders, seen, node_name)
        elif isinstance(data, str):
            for pattern in self.PLACEHOLDER_PATTERNS:
                matches = re.findall(pattern, data)
                for match in matches:
                    key = re.sub(r'[{}$<>]', '', match).strip()

                    if key not in seen:
                        seen.add(key)
                        placeholders.append({
                            "key": key,
                            "placeholder": match,
                            "node": node_name,
                            "required": True
                        })

    def get_adaptation_log(self) -> List[str]:
        """Get log of all adaptations made"""
        return self.adaptation_log


# Global singleton adapter instance
template_adapter = TemplateAdapter()
