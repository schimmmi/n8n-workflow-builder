"""
Authentication Auditor

Checks for missing or weak authentication in workflows.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class AuthIssueType(Enum):
    """Types of authentication issues"""
    MISSING_AUTH = "missing_auth"
    WEAK_AUTH = "weak_auth"
    NO_CREDENTIALS = "no_credentials"
    INSECURE_TRANSPORT = "insecure_transport"
    BASIC_AUTH_PLAIN = "basic_auth_plain"
    MISSING_OAUTH = "missing_oauth"
    API_KEY_IN_URL = "api_key_in_url"


class AuthSeverity(Enum):
    """Severity of authentication issues"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class AuthFinding:
    """Authentication security finding"""
    issue_type: AuthIssueType
    severity: AuthSeverity
    node_id: str
    node_name: str
    node_type: str
    description: str
    recommendation: str
    affected_field: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "issue_type": self.issue_type.value,
            "severity": self.severity.value,
            "node_id": self.node_id,
            "node_name": self.node_name,
            "node_type": self.node_type,
            "description": self.description,
            "recommendation": self.recommendation,
            "affected_field": self.affected_field
        }


class AuthenticationAuditor:
    """
    Audits workflow nodes for authentication and security issues
    """

    # Nodes that should have authentication
    AUTH_REQUIRED_NODES = {
        "n8n-nodes-base.httpRequest": "HTTP Request",
        "n8n-nodes-base.webhook": "Webhook",
        "n8n-nodes-base.postgres": "PostgreSQL",
        "n8n-nodes-base.mysql": "MySQL",
        "n8n-nodes-base.mongodb": "MongoDB",
        "n8n-nodes-base.redis": "Redis",
        "n8n-nodes-base.aws": "AWS",
        "n8n-nodes-base.googleSheets": "Google Sheets",
        "n8n-nodes-base.googleDrive": "Google Drive",
        "n8n-nodes-base.slack": "Slack",
        "n8n-nodes-base.github": "GitHub",
        "n8n-nodes-base.gitlab": "GitLab",
        "n8n-nodes-base.stripe": "Stripe",
        "n8n-nodes-base.openai": "OpenAI",
    }

    # Services that should use OAuth
    OAUTH_RECOMMENDED = {
        "google", "microsoft", "github", "gitlab", "slack",
        "dropbox", "trello", "salesforce", "hubspot"
    }

    def __init__(self):
        pass

    def audit_workflow(self, workflow: Dict) -> List[AuthFinding]:
        """
        Audit entire workflow for authentication issues

        Args:
            workflow: Workflow dict with nodes

        Returns:
            List of AuthFinding objects
        """
        findings = []

        nodes = workflow.get("nodes", [])
        for node in nodes:
            node_findings = self.audit_node(node)
            findings.extend(node_findings)

        return findings

    def audit_node(self, node: Dict) -> List[AuthFinding]:
        """
        Audit single node for authentication issues

        Args:
            node: Node data dict

        Returns:
            List of AuthFinding objects
        """
        findings = []

        node_id = node.get("id", "unknown")
        node_name = node.get("name", "Unknown")
        node_type = node.get("type", "unknown")

        # Check HTTP Request nodes
        if "httpRequest" in node_type.lower():
            findings.extend(self._audit_http_node(node))

        # Check Webhook nodes
        elif "webhook" in node_type.lower():
            findings.extend(self._audit_webhook_node(node))

        # Check Database nodes
        elif any(db in node_type.lower() for db in ["postgres", "mysql", "mongodb", "redis"]):
            findings.extend(self._audit_database_node(node))

        # Check for missing credentials on auth-required nodes
        if node_type in self.AUTH_REQUIRED_NODES:
            if not self._has_credentials(node):
                findings.append(AuthFinding(
                    issue_type=AuthIssueType.NO_CREDENTIALS,
                    severity=AuthSeverity.HIGH,
                    node_id=node_id,
                    node_name=node_name,
                    node_type=node_type,
                    description=f"Node '{node_name}' of type {self.AUTH_REQUIRED_NODES[node_type]} has no credentials configured",
                    recommendation="Add appropriate credentials for this node type"
                ))

        # Check for OAuth opportunities
        findings.extend(self._check_oauth_opportunities(node))

        return findings

    def _audit_http_node(self, node: Dict) -> List[AuthFinding]:
        """Audit HTTP Request node for auth issues"""
        findings = []
        node_id = node.get("id", "unknown")
        node_name = node.get("name", "Unknown")
        node_type = node.get("type", "unknown")
        params = node.get("parameters", {})

        # Check for authentication
        auth_type = params.get("authentication", "none")

        if auth_type == "none" or not auth_type:
            # Check if URL suggests auth is needed
            url = params.get("url", "")
            if self._url_needs_auth(url):
                findings.append(AuthFinding(
                    issue_type=AuthIssueType.MISSING_AUTH,
                    severity=AuthSeverity.HIGH,
                    node_id=node_id,
                    node_name=node_name,
                    node_type=node_type,
                    description=f"HTTP Request to '{url}' has no authentication configured",
                    recommendation="Add authentication (API Key, OAuth2, or Bearer Token)",
                    affected_field="parameters.authentication"
                ))

        # Check for insecure HTTP (not HTTPS)
        url = params.get("url", "")
        if url.startswith("http://") and not self._is_local_url(url):
            findings.append(AuthFinding(
                issue_type=AuthIssueType.INSECURE_TRANSPORT,
                severity=AuthSeverity.MEDIUM,
                node_id=node_id,
                node_name=node_name,
                node_type=node_type,
                description=f"HTTP Request uses insecure HTTP instead of HTTPS: {url}",
                recommendation="Use HTTPS to encrypt data in transit",
                affected_field="parameters.url"
            ))

        # Check for API keys in URL
        if "api" in url.lower() and ("key=" in url or "token=" in url):
            findings.append(AuthFinding(
                issue_type=AuthIssueType.API_KEY_IN_URL,
                severity=AuthSeverity.HIGH,
                node_id=node_id,
                node_name=node_name,
                node_type=node_type,
                description="API key appears to be in URL query parameters",
                recommendation="Use header-based authentication instead of URL parameters",
                affected_field="parameters.url"
            ))

        # Check for Basic Auth without HTTPS
        if auth_type == "basicAuth" and url.startswith("http://"):
            findings.append(AuthFinding(
                issue_type=AuthIssueType.BASIC_AUTH_PLAIN,
                severity=AuthSeverity.CRITICAL,
                node_id=node_id,
                node_name=node_name,
                node_type=node_type,
                description="Basic Authentication over HTTP sends credentials in plain text",
                recommendation="Use HTTPS with Basic Auth, or switch to Bearer Token/OAuth2",
                affected_field="parameters.authentication"
            ))

        return findings

    def _audit_webhook_node(self, node: Dict) -> List[AuthFinding]:
        """Audit Webhook node for security issues"""
        findings = []
        node_id = node.get("id", "unknown")
        node_name = node.get("name", "Unknown")
        node_type = node.get("type", "unknown")
        params = node.get("parameters", {})

        # Check for webhook authentication
        auth_mode = params.get("authentication", "none")
        webhook_id = params.get("webhookId", "")

        if auth_mode == "none" or not auth_mode:
            findings.append(AuthFinding(
                issue_type=AuthIssueType.MISSING_AUTH,
                severity=AuthSeverity.CRITICAL,
                node_id=node_id,
                node_name=node_name,
                node_type=node_type,
                description=f"Webhook '{node_name}' has no authentication enabled - anyone can trigger it",
                recommendation="Enable webhook authentication (Header Auth, Basic Auth, or IP Whitelist)",
                affected_field="parameters.authentication"
            ))

        # Check for production webhooks
        if "prod" in webhook_id.lower() or "production" in node_name.lower():
            if auth_mode == "none":
                findings.append(AuthFinding(
                    issue_type=AuthIssueType.MISSING_AUTH,
                    severity=AuthSeverity.CRITICAL,
                    node_id=node_id,
                    node_name=node_name,
                    node_type=node_type,
                    description="Production webhook has no authentication - security risk!",
                    recommendation="URGENT: Enable authentication for production webhooks",
                    affected_field="parameters.authentication"
                ))

        return findings

    def _audit_database_node(self, node: Dict) -> List[AuthFinding]:
        """Audit database node for auth issues"""
        findings = []
        node_id = node.get("id", "unknown")
        node_name = node.get("name", "Unknown")
        node_type = node.get("type", "unknown")

        # Check for credentials
        if not self._has_credentials(node):
            findings.append(AuthFinding(
                issue_type=AuthIssueType.NO_CREDENTIALS,
                severity=AuthSeverity.CRITICAL,
                node_id=node_id,
                node_name=node_name,
                node_type=node_type,
                description=f"Database node '{node_name}' has no credentials configured",
                recommendation="Add database credentials with proper authentication"
            ))

        # Check for connection string in parameters (shouldn't be there)
        params = node.get("parameters", {})
        connection_string = params.get("connectionString", "")
        if connection_string and "://" in connection_string:
            # Connection string with credentials
            if "@" in connection_string:
                findings.append(AuthFinding(
                    issue_type=AuthIssueType.NO_CREDENTIALS,
                    severity=AuthSeverity.HIGH,
                    node_id=node_id,
                    node_name=node_name,
                    node_type=node_type,
                    description="Database credentials appear to be in connection string",
                    recommendation="Use n8n credentials instead of hardcoding connection strings",
                    affected_field="parameters.connectionString"
                ))

        return findings

    def _check_oauth_opportunities(self, node: Dict) -> List[AuthFinding]:
        """Check if node should use OAuth but doesn't"""
        findings = []
        node_id = node.get("id", "unknown")
        node_name = node.get("name", "Unknown")
        node_type = node.get("type", "unknown")

        # Check if this service recommends OAuth
        for service in self.OAUTH_RECOMMENDED:
            if service in node_type.lower() or service in node_name.lower():
                # Check if using OAuth
                credentials = node.get("credentials", {})
                auth_type = str(credentials).lower() if credentials else ""

                if "oauth" not in auth_type:
                    findings.append(AuthFinding(
                        issue_type=AuthIssueType.MISSING_OAUTH,
                        severity=AuthSeverity.MEDIUM,
                        node_id=node_id,
                        node_name=node_name,
                        node_type=node_type,
                        description=f"{service.title()} integration should use OAuth2 for better security",
                        recommendation=f"Use OAuth2 credentials for {service.title()} instead of API keys"
                    ))
                break

        return findings

    def _has_credentials(self, node: Dict) -> bool:
        """Check if node has credentials configured"""
        credentials = node.get("credentials", {})
        return bool(credentials and len(credentials) > 0)

    def _url_needs_auth(self, url: str) -> bool:
        """Check if URL suggests authentication is needed"""
        if not url:
            return False

        # APIs usually need auth
        if "/api/" in url or url.endswith("/api"):
            return True

        # External services need auth
        if any(domain in url for domain in [
            "github.com", "gitlab.com", "api.stripe.com",
            "googleapis.com", "slack.com", "openai.com"
        ]):
            return True

        return False

    def _is_local_url(self, url: str) -> bool:
        """Check if URL is local/internal"""
        local_indicators = [
            "localhost", "127.0.0.1", "0.0.0.0",
            "192.168.", "10.", "172.16."
        ]
        return any(indicator in url for indicator in local_indicators)
