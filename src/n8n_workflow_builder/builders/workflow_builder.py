#!/usr/bin/env python3
"""
Workflow Builder Module
AI-powered workflow builder with node suggestions and analysis
"""
import json
from typing import Dict, List

# n8n Node Knowledge Base - The most common and useful nodes
NODE_KNOWLEDGE = {
    "triggers": {
        "webhook": {
            "name": "Webhook",
            "desc": "Receives HTTP requests from external sources",
            "use_cases": ["API endpoints", "External integrations", "Form submissions"],
            "best_practices": ["Use authentication", "Validate input data", "Return proper status codes"]
        },
        "schedule": {
            "name": "Schedule Trigger",
            "desc": "Runs workflows on a schedule",
            "use_cases": ["Daily reports", "Periodic data syncs", "Cleanup tasks"],
            "best_practices": ["Use cron for complex schedules", "Consider timezone", "Avoid peak times"]
        },
        "manual": {
            "name": "Manual Trigger",
            "desc": "Manually start workflows",
            "use_cases": ["Testing", "One-time tasks", "Manual interventions"],
            "best_practices": ["Add clear description", "Use for development"]
        }
    },
    "logic": {
        "if": {
            "name": "IF",
            "desc": "Conditional branching based on rules",
            "use_cases": ["Data validation", "Route based on conditions", "Error handling"],
            "best_practices": ["Keep conditions simple", "Use meaningful names", "Handle both paths"]
        },
        "switch": {
            "name": "Switch",
            "desc": "Multi-way branching",
            "use_cases": ["Multiple conditions", "Status-based routing", "Category routing"],
            "best_practices": ["Add default case", "Use for 3+ branches", "Clear case names"]
        },
        "merge": {
            "name": "Merge",
            "desc": "Combine data from multiple sources",
            "use_cases": ["Combine API results", "Aggregate data", "Join datasets"],
            "best_practices": ["Choose right merge mode", "Handle missing data", "Check data structure"]
        },
        "code": {
            "name": "Code",
            "desc": "Execute JavaScript/Python code",
            "use_cases": ["Complex transforms", "Custom logic", "Data processing"],
            "best_practices": ["Keep code simple", "Add comments", "Handle errors", "Use $input for data"]
        }
    },
    "data": {
        "http_request": {
            "name": "HTTP Request",
            "desc": "Make HTTP API calls",
            "use_cases": ["API integration", "Web scraping", "External services"],
            "best_practices": ["Set timeout", "Handle errors", "Use retry logic", "Validate responses"]
        },
        "set": {
            "name": "Edit Fields (Set)",
            "desc": "Transform and set data fields",
            "use_cases": ["Data mapping", "Format conversion", "Add calculated fields"],
            "best_practices": ["Use expressions", "Keep transforms simple", "Clear field names"]
        },
        "function": {
            "name": "Function",
            "desc": "Transform data with JavaScript",
            "use_cases": ["Complex calculations", "Array operations", "String manipulation"],
            "best_practices": ["Return items array", "Handle edge cases", "Use lodash when needed"]
        }
    },
    "storage": {
        "postgres": {
            "name": "Postgres",
            "desc": "PostgreSQL database operations",
            "use_cases": ["Data persistence", "Complex queries", "Transactions"],
            "best_practices": ["Use parameterized queries", "Index lookups", "Batch operations"]
        },
        "redis": {
            "name": "Redis",
            "desc": "Redis key-value store",
            "use_cases": ["Caching", "Rate limiting", "Session storage"],
            "best_practices": ["Set TTL", "Use appropriate data types", "Handle connection errors"]
        }
    },
    "integrations": {
        "slack": {
            "name": "Slack",
            "desc": "Slack messaging integration",
            "use_cases": ["Notifications", "Bot interactions", "Team updates"],
            "best_practices": ["Format messages", "Use thread replies", "Handle rate limits"]
        },
        "telegram": {
            "name": "Telegram",
            "desc": "Telegram bot integration",
            "use_cases": ["Notifications", "Bot commands", "Interactive messages"],
            "best_practices": ["Parse mode HTML/Markdown", "Keyboard layouts", "Handle commands"]
        },
        "gmail": {
            "name": "Gmail",
            "desc": "Gmail email operations",
            "use_cases": ["Email automation", "Read emails", "Send emails"],
            "best_practices": ["Use filters", "Batch operations", "Handle attachments"]
        }
    }
}


class WorkflowBuilder:
    """AI-powered workflow builder"""

    @staticmethod
    def suggest_nodes(description: str) -> List[Dict]:
        """Suggest nodes based on workflow description"""
        description_lower = description.lower()
        suggestions = []

        # Trigger detection
        if any(word in description_lower for word in ["api", "endpoint", "webhook", "http"]):
            suggestions.append(NODE_KNOWLEDGE["triggers"]["webhook"])
        elif any(word in description_lower for word in ["schedule", "daily", "hourly", "cron"]):
            suggestions.append(NODE_KNOWLEDGE["triggers"]["schedule"])

        # Integration detection
        if "slack" in description_lower:
            suggestions.append(NODE_KNOWLEDGE["integrations"]["slack"])
        if "telegram" in description_lower:
            suggestions.append(NODE_KNOWLEDGE["integrations"]["telegram"])
        if "email" in description_lower or "gmail" in description_lower:
            suggestions.append(NODE_KNOWLEDGE["integrations"]["gmail"])

        # Logic detection
        if any(word in description_lower for word in ["if", "condition", "check", "validate"]):
            suggestions.append(NODE_KNOWLEDGE["logic"]["if"])
        if any(word in description_lower for word in ["switch", "multiple", "cases"]):
            suggestions.append(NODE_KNOWLEDGE["logic"]["switch"])

        # Data operations
        if any(word in description_lower for word in ["transform", "map", "convert"]):
            suggestions.append(NODE_KNOWLEDGE["data"]["set"])
        if any(word in description_lower for word in ["api call", "fetch", "get data"]):
            suggestions.append(NODE_KNOWLEDGE["data"]["http_request"])

        # Storage
        if any(word in description_lower for word in ["database", "postgres", "sql"]):
            suggestions.append(NODE_KNOWLEDGE["storage"]["postgres"])
        if any(word in description_lower for word in ["cache", "redis"]):
            suggestions.append(NODE_KNOWLEDGE["storage"]["redis"])

        return suggestions

    @staticmethod
    def generate_workflow_outline(description: str, suggested_nodes: List[Dict]) -> str:
        """Generate a workflow outline"""
        outline = f"# Workflow: {description}\n\n"
        outline += "## Suggested Structure:\n\n"

        for i, node in enumerate(suggested_nodes, 1):
            outline += f"{i}. **{node['name']}**\n"
            outline += f"   - Purpose: {node['desc']}\n"
            outline += f"   - Use Cases: {', '.join(node['use_cases'])}\n\n"

        outline += "\n## Best Practices:\n\n"
        for node in suggested_nodes:
            outline += f"### {node['name']}\n"
            for practice in node['best_practices']:
                outline += f"- {practice}\n"
            outline += "\n"

        return outline

    @staticmethod
    def analyze_workflow(workflow: Dict) -> Dict:
        """Analyze a workflow for potential issues"""
        issues = []
        suggestions = []
        nodes = workflow.get("nodes", [])

        # Check for common issues
        if not nodes:
            issues.append("Workflow has no nodes")

        # Check for missing error handling
        has_error_handling = any(
            node.get("type") == "n8n-nodes-base.errorTrigger"
            for node in nodes
        )
        if not has_error_handling and len(nodes) > 3:
            suggestions.append("Consider adding error handling nodes")

        # Check for hardcoded values
        for node in nodes:
            node_str = json.dumps(node)
            if "password" in node_str.lower() and not "{{" in node_str:
                issues.append(f"Node '{node.get('name')}' may contain hardcoded credentials")

        # Check workflow structure
        if len(nodes) > 20:
            suggestions.append("Consider splitting into sub-workflows for better maintainability")

        # Check for proper naming
        default_names = ["Webhook", "HTTP Request", "Set", "IF"]
        unnamed_nodes = [
            node.get("name") for node in nodes
            if node.get("name") in default_names
        ]
        if unnamed_nodes:
            suggestions.append(f"Consider renaming default node names: {', '.join(set(unnamed_nodes))}")

        return {
            "total_nodes": len(nodes),
            "issues": issues,
            "suggestions": suggestions,
            "complexity": "Low" if len(nodes) < 5 else "Medium" if len(nodes) < 15 else "High"
        }
