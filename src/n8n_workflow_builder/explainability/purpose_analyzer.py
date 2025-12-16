"""
Workflow Purpose Analyzer - Determines WHY a workflow exists

Analyzes:
- Workflow name, description, tags
- Trigger type and configuration
- First few nodes to understand intent
- Intent metadata if available
- Business domain classification
"""

from typing import Dict, List, Optional
import re


class WorkflowPurposeAnalyzer:
    """Analyzes workflow to determine its purpose and business domain"""

    # Business domain keywords
    DOMAIN_KEYWORDS = {
        "e-commerce": ["order", "payment", "checkout", "cart", "product", "inventory", "shipping", "customer"],
        "devops": ["deploy", "build", "test", "ci/cd", "pipeline", "docker", "kubernetes", "monitoring"],
        "data_processing": ["etl", "transform", "aggregate", "sync", "migrate", "import", "export", "batch"],
        "notifications": ["alert", "notify", "email", "slack", "sms", "notification", "message"],
        "crm": ["lead", "contact", "customer", "sales", "deal", "opportunity", "pipeline"],
        "hr": ["employee", "recruit", "onboard", "payroll", "attendance", "leave", "training"],
        "finance": ["invoice", "billing", "payment", "transaction", "accounting", "expense"],
        "marketing": ["campaign", "email", "social", "analytics", "lead", "conversion", "seo"],
        "support": ["ticket", "issue", "support", "helpdesk", "zendesk", "jira"],
        "integration": ["sync", "webhook", "api", "integration", "connect", "bridge"],
    }

    # Workflow type patterns
    WORKFLOW_TYPES = {
        "event_driven": ["webhook", "trigger", "on", "when"],
        "scheduled": ["cron", "schedule", "daily", "hourly", "weekly", "interval"],
        "manual": ["manual", "button", "on-demand"],
        "data_sync": ["sync", "replicate", "mirror", "backup"],
        "automation": ["automate", "automatic", "auto"],
        "monitoring": ["monitor", "watch", "check", "alert"],
    }

    @staticmethod
    def analyze_purpose(workflow: Dict) -> Dict:
        """
        Analyze workflow to determine its purpose

        Returns:
            {
                "primary_purpose": str,
                "business_domain": str,
                "workflow_type": str,
                "confidence": float,
                "evidence": List[str],
                "description": str,
                "trigger_description": str,
                "expected_outcomes": List[str]
            }
        """
        name = workflow.get("name", "")
        nodes = workflow.get("nodes", [])
        settings = workflow.get("settings", {})

        # Extract trigger information
        trigger_node = next((n for n in nodes if n.get("type", "").endswith("Trigger")), None)

        # Analyze business domain
        domain_analysis = WorkflowPurposeAnalyzer._classify_business_domain(workflow)

        # Analyze workflow type
        type_analysis = WorkflowPurposeAnalyzer._classify_workflow_type(workflow, trigger_node)

        # Generate primary purpose description
        primary_purpose = WorkflowPurposeAnalyzer._generate_primary_purpose(
            workflow, domain_analysis, type_analysis, trigger_node
        )

        # Extract expected outcomes
        expected_outcomes = WorkflowPurposeAnalyzer._extract_expected_outcomes(workflow, nodes)

        # Generate trigger description
        trigger_description = WorkflowPurposeAnalyzer._describe_trigger(trigger_node)

        # Combine evidence
        evidence = domain_analysis["evidence"] + type_analysis["evidence"]

        # Calculate overall confidence
        confidence = (domain_analysis["confidence"] + type_analysis["confidence"]) / 2

        return {
            "primary_purpose": primary_purpose,
            "business_domain": domain_analysis["domain"],
            "workflow_type": type_analysis["type"],
            "confidence": round(confidence, 2),
            "evidence": evidence,
            "description": WorkflowPurposeAnalyzer._generate_description(
                primary_purpose, domain_analysis["domain"], type_analysis["type"]
            ),
            "trigger_description": trigger_description,
            "expected_outcomes": expected_outcomes,
        }

    @staticmethod
    def _classify_business_domain(workflow: Dict) -> Dict:
        """Classify workflow into business domain"""
        name = workflow.get("name", "").lower()
        nodes = workflow.get("nodes", [])
        tags = workflow.get("tags", [])

        # Collect text to analyze
        text_to_analyze = f"{name} {' '.join(str(t) for t in tags)}"

        # Add node names and types
        for node in nodes:
            node_name = node.get("name", "").lower()
            node_type = node.get("type", "").lower()
            text_to_analyze += f" {node_name} {node_type}"

        # Score each domain
        domain_scores = {}
        domain_evidence = {}

        for domain, keywords in WorkflowPurposeAnalyzer.DOMAIN_KEYWORDS.items():
            score = 0
            evidence = []

            for keyword in keywords:
                if keyword in text_to_analyze:
                    score += text_to_analyze.count(keyword)
                    evidence.append(f"Keyword '{keyword}' found")

            if score > 0:
                domain_scores[domain] = score
                domain_evidence[domain] = evidence

        # Find best match
        if domain_scores:
            best_domain = max(domain_scores, key=domain_scores.get)
            max_score = max(domain_scores.values())
            total_keywords = sum(len(keywords) for keywords in WorkflowPurposeAnalyzer.DOMAIN_KEYWORDS.values())
            confidence = min(0.95, max_score / 5)  # Cap at 0.95

            return {
                "domain": best_domain,
                "confidence": confidence,
                "evidence": domain_evidence[best_domain][:3],  # Top 3 pieces of evidence
            }
        else:
            return {
                "domain": "general",
                "confidence": 0.3,
                "evidence": ["No specific domain keywords found"],
            }

    @staticmethod
    def _classify_workflow_type(workflow: Dict, trigger_node: Optional[Dict]) -> Dict:
        """Classify workflow type (event-driven, scheduled, manual, etc.)"""
        name = workflow.get("name", "").lower()
        settings = workflow.get("settings", {})

        evidence = []
        detected_type = "manual"  # Default
        confidence = 0.5

        if trigger_node:
            trigger_type = trigger_node.get("type", "")
            trigger_params = trigger_node.get("parameters", {})

            # Check trigger type
            if "webhook" in trigger_type.lower():
                detected_type = "event_driven"
                confidence = 0.9
                evidence.append(f"Webhook trigger: {trigger_type}")
            elif "schedule" in trigger_type.lower() or "cron" in trigger_type.lower():
                detected_type = "scheduled"
                confidence = 0.9
                cron_expr = trigger_params.get("rule", {}).get("interval", "")
                evidence.append(f"Schedule trigger with interval: {cron_expr}")
            elif "manual" in trigger_type.lower():
                detected_type = "manual"
                confidence = 0.95
                evidence.append("Manual trigger - user-initiated")
            else:
                # Check for event-driven keywords in trigger
                if any(kw in trigger_type.lower() for kw in ["event", "watch", "poll"]):
                    detected_type = "event_driven"
                    confidence = 0.75
                    evidence.append(f"Event-driven trigger: {trigger_type}")

        # Check workflow name for type hints
        for wf_type, keywords in WorkflowPurposeAnalyzer.WORKFLOW_TYPES.items():
            if any(kw in name for kw in keywords):
                if not evidence:  # Only use name-based detection if no trigger evidence
                    detected_type = wf_type
                    confidence = 0.6
                evidence.append(f"Workflow name contains '{wf_type}' keywords")
                break

        if not evidence:
            evidence.append("No clear workflow type indicators found")

        return {
            "type": detected_type,
            "confidence": confidence,
            "evidence": evidence,
        }

    @staticmethod
    def _generate_primary_purpose(
        workflow: Dict,
        domain_analysis: Dict,
        type_analysis: Dict,
        trigger_node: Optional[Dict]
    ) -> str:
        """Generate human-readable primary purpose"""
        name = workflow.get("name", "")
        domain = domain_analysis["domain"]
        wf_type = type_analysis["type"]

        # Build purpose string
        purpose_parts = []

        # Add workflow type context
        if wf_type == "event_driven":
            purpose_parts.append("Automatically responds to events")
        elif wf_type == "scheduled":
            purpose_parts.append("Runs on a schedule")
        elif wf_type == "manual":
            purpose_parts.append("User-initiated workflow")
        elif wf_type == "data_sync":
            purpose_parts.append("Synchronizes data")
        elif wf_type == "monitoring":
            purpose_parts.append("Monitors systems and sends alerts")

        # Add domain context
        if domain != "general":
            domain_purposes = {
                "e-commerce": "for e-commerce operations",
                "devops": "for DevOps and deployment automation",
                "data_processing": "for data processing and transformation",
                "notifications": "for notifications and alerts",
                "crm": "for CRM and sales management",
                "hr": "for HR and employee management",
                "finance": "for financial operations",
                "marketing": "for marketing campaigns",
                "support": "for customer support",
                "integration": "for system integration",
            }
            purpose_parts.append(domain_purposes.get(domain, f"for {domain}"))

        # Fallback to workflow name if nothing specific found
        if len(purpose_parts) == 0:
            return f"Workflow '{name}' - purpose unclear from structure"

        return " ".join(purpose_parts)

    @staticmethod
    def _describe_trigger(trigger_node: Optional[Dict]) -> str:
        """Generate human-readable trigger description"""
        if not trigger_node:
            return "No trigger configured (workflow must be executed manually or called by another workflow)"

        trigger_type = trigger_node.get("type", "")
        trigger_name = trigger_node.get("name", "")
        trigger_params = trigger_node.get("parameters", {})

        descriptions = []

        # Type-specific descriptions
        if "webhook" in trigger_type.lower():
            path = trigger_params.get("path", "")
            method = trigger_params.get("httpMethod", "POST")
            descriptions.append(f"Webhook endpoint: {method} {path}")
            descriptions.append("Triggered by external HTTP requests")

        elif "schedule" in trigger_type.lower() or "cron" in trigger_type.lower():
            rule = trigger_params.get("rule", {})
            # Handle both dict and list formats
            if isinstance(rule, dict):
                interval = rule.get("interval", [])
            elif isinstance(rule, list):
                interval = rule
            else:
                interval = []

            if isinstance(interval, list) and interval:
                cron_expr = interval[0].get("expression", "") if isinstance(interval[0], dict) else str(interval[0])
                if cron_expr:
                    descriptions.append(f"Runs on schedule: {cron_expr}")
            descriptions.append("Automatically executes at specified times")

        elif "manual" in trigger_type.lower():
            descriptions.append("Manual trigger - started by user")
            descriptions.append("Can be executed from n8n UI or API")

        else:
            descriptions.append(f"Trigger type: {trigger_type}")
            descriptions.append(f"Trigger name: {trigger_name}")

        return " | ".join(descriptions)

    @staticmethod
    def _extract_expected_outcomes(workflow: Dict, nodes: List[Dict]) -> List[str]:
        """Extract expected outcomes from workflow structure"""
        outcomes = []

        # Look for output nodes (nodes that send data somewhere)
        for node in nodes:
            node_type = node.get("type", "").lower()
            node_name = node.get("name", "")

            # Email nodes
            if "email" in node_type or "send" in node_type:
                outcomes.append(f"Sends email notifications via '{node_name}'")

            # Slack/messaging nodes
            elif "slack" in node_type or "telegram" in node_type or "discord" in node_type:
                outcomes.append(f"Sends messages to chat platform via '{node_name}'")

            # Database nodes
            elif any(db in node_type for db in ["postgres", "mysql", "mongo", "redis", "database"]):
                outcomes.append(f"Writes data to database via '{node_name}'")

            # HTTP Request nodes (potential API calls)
            elif "httprequest" in node_type:
                params = node.get("parameters", {})
                method = params.get("method", "GET")
                url = params.get("url", "")
                if method in ["POST", "PUT", "PATCH"]:
                    outcomes.append(f"Sends data to external API via '{node_name}'")

            # Spreadsheet nodes
            elif "sheets" in node_type or "excel" in node_type or "airtable" in node_type:
                outcomes.append(f"Updates spreadsheet data via '{node_name}'")

            # File operations
            elif "file" in node_type or "ftp" in node_type or "s3" in node_type:
                outcomes.append(f"Manages files/storage via '{node_name}'")

        if not outcomes:
            outcomes.append("No clear output destinations identified")

        return outcomes

    @staticmethod
    def _generate_description(primary_purpose: str, domain: str, wf_type: str) -> str:
        """Generate comprehensive workflow description"""
        return (
            f"{primary_purpose}. "
            f"This workflow is classified as '{wf_type}' in the '{domain}' domain. "
            f"It automates processes to reduce manual work and ensure consistency."
        )
