"""
n8n Documentation Access Module

Provides access to official n8n documentation for nodes, credentials, and concepts.
"""
from typing import Dict, List, Optional
import re


class N8nDocumentation:
    """Access official n8n documentation"""

    BASE_URL = "https://docs.n8n.io"

    # Core nodes documentation paths
    CORE_NODES = {
        "code": "/integrations/builtin/core-nodes/n8n-nodes-base.code/",
        "http": "/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/",
        "httprequest": "/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/",
        "webhook": "/integrations/builtin/core-nodes/n8n-nodes-base.webhook/",
        "if": "/integrations/builtin/core-nodes/n8n-nodes-base.if/",
        "switch": "/integrations/builtin/core-nodes/n8n-nodes-base.switch/",
        "merge": "/integrations/builtin/core-nodes/n8n-nodes-base.merge/",
        "set": "/integrations/builtin/core-nodes/n8n-nodes-base.set/",
        "filter": "/integrations/builtin/core-nodes/n8n-nodes-base.filter/",
        "split": "/integrations/builtin/core-nodes/n8n-nodes-base.splitinbatches/",
        "aggregate": "/integrations/builtin/core-nodes/n8n-nodes-base.aggregate/",
        "schedule": "/integrations/builtin/core-nodes/n8n-nodes-base.scheduletrigger/",
        "cron": "/integrations/builtin/core-nodes/n8n-nodes-base.scheduletrigger/",
        "manual": "/integrations/builtin/core-nodes/n8n-nodes-base.manualtrigger/",
        "error": "/integrations/builtin/core-nodes/n8n-nodes-base.errortrigger/",
        "wait": "/integrations/builtin/core-nodes/n8n-nodes-base.wait/",
        "execute": "/integrations/builtin/core-nodes/n8n-nodes-base.executeworkflow/",
        "spreadsheet": "/integrations/builtin/core-nodes/n8n-nodes-base.spreadsheetfile/",
        "email": "/integrations/builtin/core-nodes/n8n-nodes-base.emailsend/",
        "ssh": "/integrations/builtin/core-nodes/n8n-nodes-base.ssh/",
        "ftp": "/integrations/builtin/core-nodes/n8n-nodes-base.ftp/",
        "html": "/integrations/builtin/core-nodes/n8n-nodes-base.html/",
        "xml": "/integrations/builtin/core-nodes/n8n-nodes-base.xml/",
        "markdown": "/integrations/builtin/core-nodes/n8n-nodes-base.markdown/",
        "crypto": "/integrations/builtin/core-nodes/n8n-nodes-base.crypto/",
        "compression": "/integrations/builtin/core-nodes/n8n-nodes-base.compression/",
        "datetime": "/integrations/builtin/core-nodes/n8n-nodes-base.datetime/",
        "sort": "/integrations/builtin/core-nodes/n8n-nodes-base.sort/",
        "limit": "/integrations/builtin/core-nodes/n8n-nodes-base.limit/",
        "removeDuplicates": "/integrations/builtin/core-nodes/n8n-nodes-base.removeduplicates/",
    }

    # Common app nodes
    APP_NODES = {
        "googlesheets": "/integrations/builtin/app-nodes/n8n-nodes-base.googlesheets/",
        "googledrive": "/integrations/builtin/app-nodes/n8n-nodes-base.googledrive/",
        "gmail": "/integrations/builtin/app-nodes/n8n-nodes-base.gmail/",
        "slack": "/integrations/builtin/app-nodes/n8n-nodes-base.slack/",
        "telegram": "/integrations/builtin/app-nodes/n8n-nodes-base.telegram/",
        "discord": "/integrations/builtin/app-nodes/n8n-nodes-base.discord/",
        "airtable": "/integrations/builtin/app-nodes/n8n-nodes-base.airtable/",
        "notion": "/integrations/builtin/app-nodes/n8n-nodes-base.notion/",
        "github": "/integrations/builtin/app-nodes/n8n-nodes-base.github/",
        "gitlab": "/integrations/builtin/app-nodes/n8n-nodes-base.gitlab/",
        "jira": "/integrations/builtin/app-nodes/n8n-nodes-base.jira/",
        "trello": "/integrations/builtin/app-nodes/n8n-nodes-base.trello/",
        "asana": "/integrations/builtin/app-nodes/n8n-nodes-base.asana/",
        "mysql": "/integrations/builtin/app-nodes/n8n-nodes-base.mysql/",
        "postgres": "/integrations/builtin/app-nodes/n8n-nodes-base.postgres/",
        "postgresql": "/integrations/builtin/app-nodes/n8n-nodes-base.postgres/",
        "mongodb": "/integrations/builtin/app-nodes/n8n-nodes-base.mongodb/",
        "redis": "/integrations/builtin/app-nodes/n8n-nodes-base.redis/",
        "stripe": "/integrations/builtin/app-nodes/n8n-nodes-base.stripe/",
        "paypal": "/integrations/builtin/app-nodes/n8n-nodes-base.paypal/",
        "shopify": "/integrations/builtin/app-nodes/n8n-nodes-base.shopify/",
        "woocommerce": "/integrations/builtin/app-nodes/n8n-nodes-base.woocommerce/",
        "wordpress": "/integrations/builtin/app-nodes/n8n-nodes-base.wordpress/",
        "aws": "/integrations/builtin/app-nodes/n8n-nodes-base.aws/",
        "s3": "/integrations/builtin/app-nodes/n8n-nodes-base.awss3/",
        "lambda": "/integrations/builtin/app-nodes/n8n-nodes-base.awslambda/",
        "ses": "/integrations/builtin/app-nodes/n8n-nodes-base.awsses/",
    }

    # Documentation sections
    SECTIONS = {
        "core-nodes": "/integrations/builtin/core-nodes/",
        "app-nodes": "/integrations/builtin/app-nodes/",
        "trigger-nodes": "/integrations/builtin/trigger-nodes/",
        "credentials": "/integrations/builtin/credentials/",
        "workflow-basics": "/workflows/",
        "data-transformation": "/data/",
        "error-handling": "/workflows/error-workflows/",
        "webhooks": "/integrations/builtin/core-nodes/n8n-nodes-base.webhook/",
        "code-node": "/code/",
        "expressions": "/code/expressions/",
        "javascript": "/code/builtin/javascript-code/",
        "python": "/code/builtin/python-code/",
    }

    def __init__(self):
        """Initialize documentation access"""
        pass

    def get_node_doc_url(self, node_type: str) -> Optional[str]:
        """
        Get documentation URL for a node type

        Args:
            node_type: Node type (e.g., "n8n-nodes-base.code", "code", "googleSheets")

        Returns:
            Full documentation URL or None if not found
        """
        # Normalize node type
        node_name = self._normalize_node_name(node_type)

        # Check core nodes
        if node_name in self.CORE_NODES:
            return self.BASE_URL + self.CORE_NODES[node_name]

        # Check app nodes
        if node_name in self.APP_NODES:
            return self.BASE_URL + self.APP_NODES[node_name]

        # Try to construct URL from node_type
        if node_type.startswith("n8n-nodes-base."):
            node_slug = node_type.replace("n8n-nodes-base.", "")
            # Try core nodes first
            core_url = f"{self.BASE_URL}/integrations/builtin/core-nodes/{node_type}/"
            return core_url

        return None

    def _normalize_node_name(self, node_type: str) -> str:
        """
        Normalize node type to lowercase name

        Args:
            node_type: Node type string

        Returns:
            Normalized node name
        """
        # Remove n8n-nodes-base. prefix
        name = node_type.replace("n8n-nodes-base.", "")

        # Convert to lowercase
        name = name.lower()

        # Remove common suffixes
        name = name.replace("trigger", "")
        name = name.replace("node", "")

        # Strip whitespace
        name = name.strip()

        return name

    def get_section_url(self, section: str) -> Optional[str]:
        """
        Get URL for a documentation section

        Args:
            section: Section name (e.g., "core-nodes", "expressions", "error-handling")

        Returns:
            Full URL to documentation section
        """
        section_lower = section.lower()

        if section_lower in self.SECTIONS:
            return self.BASE_URL + self.SECTIONS[section_lower]

        return None

    def search_documentation(self, query: str) -> List[Dict[str, str]]:
        """
        Search for relevant documentation

        Args:
            query: Search query

        Returns:
            List of relevant documentation links with descriptions
        """
        query_lower = query.lower()
        results = []

        # Search core nodes
        for node_name, path in self.CORE_NODES.items():
            if query_lower in node_name:
                results.append({
                    "type": "core-node",
                    "name": node_name,
                    "url": self.BASE_URL + path,
                    "category": "Core Nodes"
                })

        # Search app nodes
        for node_name, path in self.APP_NODES.items():
            if query_lower in node_name:
                results.append({
                    "type": "app-node",
                    "name": node_name,
                    "url": self.BASE_URL + path,
                    "category": "App Nodes"
                })

        # Search sections
        for section_name, path in self.SECTIONS.items():
            if query_lower in section_name:
                results.append({
                    "type": "section",
                    "name": section_name,
                    "url": self.BASE_URL + path,
                    "category": "Documentation"
                })

        return results

    def get_common_patterns_url(self) -> str:
        """Get URL to common workflow patterns"""
        return f"{self.BASE_URL}/workflows/create-starter-workflows/"

    def get_best_practices_url(self) -> str:
        """Get URL to best practices"""
        return f"{self.BASE_URL}/workflows/create-starter-workflows/"

    def get_troubleshooting_url(self) -> str:
        """Get URL to troubleshooting guide"""
        return f"{self.BASE_URL}/hosting/troubleshooting/"

    def get_api_reference_url(self) -> str:
        """Get URL to API reference"""
        return f"{self.BASE_URL}/api/"

    def format_doc_summary(self, node_type: str, doc_content: str) -> str:
        """
        Format documentation content for display

        Args:
            node_type: Node type
            doc_content: Raw documentation content

        Returns:
            Formatted markdown summary
        """
        url = self.get_node_doc_url(node_type)

        summary = f"# 📖 Documentation: {node_type}\n\n"

        if url:
            summary += f"**Official Docs:** {url}\n\n"

        summary += "## Overview\n\n"
        summary += doc_content[:500]

        if len(doc_content) > 500:
            summary += f"...\n\n[Read full documentation]({url})"

        return summary
