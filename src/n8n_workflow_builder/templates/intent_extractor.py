"""Template Intent Extraction - Makes templates thinkable, not just executable"""
from typing import Dict, List, Optional
from .sources.base import TemplateMetadata


class TemplateIntentExtractor:
    """
    Extracts the "WHY" from templates:
    - Purpose: What does this template do?
    - Assumptions: What does it assume about the environment?
    - Risks: What could go wrong?
    - External Systems: What services does it depend on?
    - Data Flow: How does data move through it?
    """

    @staticmethod
    def extract_intent(template: TemplateMetadata) -> Dict:
        """
        Extract intent metadata from template

        Returns:
            {
                "intent": "Synchronize CRM contacts to database",
                "purpose": "Automate data sync between systems",
                "assumptions": ["CRM API is stable", "IDs are immutable"],
                "risks": ["Duplicate records", "Rate limiting"],
                "external_systems": ["Salesforce", "PostgreSQL"],
                "trigger_type": "schedule",
                "data_flow": "CRM API → Transform → Database"
            }
        """
        nodes = template.nodes
        connections = template.connections
        name = template.name
        description = template.description

        # Extract intent from name and description
        intent = TemplateIntentExtractor._extract_purpose(name, description, nodes)

        # Extract purpose
        purpose = TemplateIntentExtractor._classify_purpose(nodes)

        # Extract assumptions
        assumptions = TemplateIntentExtractor._extract_assumptions(nodes)

        # Extract risks
        risks = TemplateIntentExtractor._extract_risks(nodes, connections)

        # Extract external systems
        external_systems = TemplateIntentExtractor._extract_external_systems(nodes)

        # Extract trigger type
        trigger_type = TemplateIntentExtractor._extract_trigger_type(nodes)

        # Extract data flow
        data_flow = TemplateIntentExtractor._extract_data_flow(nodes, connections)

        return {
            "intent": intent,
            "purpose": purpose,
            "assumptions": assumptions,
            "risks": risks,
            "external_systems": external_systems,
            "trigger_type": trigger_type,
            "data_flow": data_flow
        }

    @staticmethod
    def _extract_purpose(name: str, description: str, nodes: List[Dict]) -> str:
        """Extract the primary intent/purpose"""
        # Start with description if available
        if description:
            return description.split(".")[0]  # First sentence

        # Fall back to name
        if name:
            return f"Workflow: {name}"

        # Analyze nodes to infer intent
        node_types = [node.get("type", "") for node in nodes]

        if any("database" in nt.lower() for nt in node_types):
            return "Database operations workflow"
        elif any("http" in nt.lower() for nt in node_types):
            return "API integration workflow"
        elif any("slack" in nt.lower() or "email" in nt.lower() for nt in node_types):
            return "Notification workflow"
        else:
            return "Data processing workflow"

    @staticmethod
    def _classify_purpose(nodes: List[Dict]) -> str:
        """Classify high-level purpose"""
        node_types = [node.get("type", "").lower() for node in nodes]

        # Classification logic
        if any("schedule" in nt for nt in node_types):
            return "Automated data synchronization"
        elif any("webhook" in nt for nt in node_types):
            return "Event-driven automation"
        elif any("http" in nt or "api" in nt for nt in node_types):
            return "API integration"
        elif any("database" in nt or "postgres" in nt or "mysql" in nt for nt in node_types):
            return "Data management"
        elif any("slack" in nt or "email" in nt or "notification" in nt for nt in node_types):
            return "Communication automation"
        else:
            return "Data processing"

    @staticmethod
    def _extract_assumptions(nodes: List[Dict]) -> List[str]:
        """Extract implicit assumptions"""
        assumptions = []

        node_types = [node.get("type", "").lower() for node in nodes]

        # API assumptions
        if any("http" in nt or "api" in nt for nt in node_types):
            assumptions.append("External API is available and stable")
            assumptions.append("API authentication credentials are valid")

        # Database assumptions
        if any("database" in nt or "postgres" in nt or "mysql" in nt for nt in node_types):
            assumptions.append("Database connection is stable")
            assumptions.append("Database schema matches expected structure")

        # Schedule assumptions
        if any("schedule" in nt for nt in node_types):
            assumptions.append("Workflow executes within expected time window")

        # Webhook assumptions
        if any("webhook" in nt for nt in node_types):
            assumptions.append("Webhook endpoint is publicly accessible")
            assumptions.append("Webhook payload format is consistent")

        # Data assumptions
        if len(nodes) > 5:
            assumptions.append("Input data format is consistent")
            assumptions.append("Data volume is manageable")

        # Check for error handling
        has_error_handling = any(
            "error" in node.get("type", "").lower() or
            node.get("continueOnFail", False)
            for node in nodes
        )

        if not has_error_handling:
            assumptions.append("No errors will occur during execution")

        return assumptions

    @staticmethod
    def _extract_risks(nodes: List[Dict], connections: Dict) -> List[str]:
        """Extract potential risks"""
        risks = []

        node_types = [node.get("type", "").lower() for node in nodes]

        # API rate limiting risk
        if any("http" in nt for nt in node_types):
            risks.append("API rate limiting may cause failures")
            risks.append("External API changes could break integration")

        # Database risks
        if any("database" in nt or "postgres" in nt or "mysql" in nt for nt in node_types):
            risks.append("Database operations without transactions may cause data inconsistency")
            risks.append("Duplicate records if workflow runs multiple times")

        # Webhook security
        if any("webhook" in nt for nt in node_types):
            webhook_nodes = [n for n in nodes if "webhook" in n.get("type", "").lower()]
            for node in webhook_nodes:
                params = node.get("parameters", {})
                if not params.get("authentication") or params.get("authentication") == "none":
                    risks.append("Webhook has no authentication - security risk")

        # Error handling
        has_error_handling = any(
            "error" in node.get("type", "").lower() or
            node.get("continueOnFail", False)
            for node in nodes
        )

        if not has_error_handling:
            risks.append("No error handling - failures will stop workflow")

        # Complexity risk
        if len(nodes) > 15:
            risks.append("High complexity increases maintenance difficulty")

        # Data loss risk
        has_database_write = any("database" in nt or "postgres" in nt or "mysql" in nt for nt in node_types)
        has_http_post = any(
            node.get("type", "").lower() == "n8n-nodes-base.httprequest" and
            node.get("parameters", {}).get("method") == "POST"
            for node in nodes
        )

        if has_database_write or has_http_post:
            risks.append("Data loss possible if operations fail partway through")

        return risks

    @staticmethod
    def _extract_external_systems(nodes: List[Dict]) -> List[str]:
        """Extract external system dependencies"""
        systems = set()

        # Service mapping
        service_patterns = {
            "slack": "Slack",
            "email": "Email (SMTP)",
            "gmail": "Gmail",
            "postgres": "PostgreSQL",
            "mysql": "MySQL",
            "mongodb": "MongoDB",
            "redis": "Redis",
            "http": "HTTP API",
            "webhook": "Webhook",
            "github": "GitHub",
            "gitlab": "GitLab",
            "jira": "Jira",
            "salesforce": "Salesforce",
            "hubspot": "HubSpot",
            "stripe": "Stripe",
            "aws": "AWS",
            "gcp": "Google Cloud",
            "azure": "Azure",
            "s3": "AWS S3",
            "lambda": "AWS Lambda",
            "notion": "Notion",
            "airtable": "Airtable",
            "google": "Google Sheets/Drive"
        }

        for node in nodes:
            node_type = node.get("type", "").lower()

            for pattern, service_name in service_patterns.items():
                if pattern in node_type:
                    systems.add(service_name)
                    break

        return sorted(list(systems))

    @staticmethod
    def _extract_trigger_type(nodes: List[Dict]) -> Optional[str]:
        """Extract trigger type"""
        for node in nodes:
            node_type = node.get("type", "").lower()

            if "schedule" in node_type:
                return "schedule"
            elif "webhook" in node_type:
                return "webhook"
            elif "manual" in node_type:
                return "manual"
            elif "trigger" in node_type:
                return node_type.replace("n8n-nodes-base.", "")

        return None

    @staticmethod
    def _extract_data_flow(nodes: List[Dict], connections: Dict) -> str:
        """Extract high-level data flow description"""
        if not nodes:
            return "No data flow"

        # Find source nodes (triggers, HTTP requests)
        sources = []
        for node in nodes:
            node_type = node.get("type", "").lower()
            if any(trigger in node_type for trigger in ["trigger", "webhook", "schedule", "http"]):
                sources.append(node.get("name", "Unknown"))

        # Find sink nodes (database, email, slack, HTTP POST)
        sinks = []
        for node in nodes:
            node_type = node.get("type", "").lower()
            if any(sink in node_type for sink in ["database", "postgres", "mysql", "email", "slack"]):
                sinks.append(node.get("name", "Unknown"))
            elif "http" in node_type:
                method = node.get("parameters", {}).get("method", "GET")
                if method in ["POST", "PUT", "PATCH"]:
                    sinks.append(node.get("name", "Unknown"))

        # Count transformation nodes
        transform_count = len(nodes) - len(sources) - len(sinks)

        # Build flow description
        if sources and sinks:
            source_str = ", ".join(sources[:2])
            sink_str = ", ".join(sinks[:2])
            return f"{source_str} → {transform_count} transformation(s) → {sink_str}"
        elif sources:
            return f"{', '.join(sources[:2])} → {len(nodes) - len(sources)} node(s)"
        else:
            return f"{len(nodes)} node(s) processing"
