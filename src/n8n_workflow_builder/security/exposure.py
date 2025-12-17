"""
Exposure Analyzer

Analyzes workflow exposure risks - public triggers, data leaks, etc.
"""

from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from enum import Enum


class ExposureType(Enum):
    """Types of exposure risks"""
    PUBLIC_WEBHOOK = "public_webhook"
    UNAUTHENTICATED_API = "unauthenticated_api"
    DATA_LEAK = "data_leak"
    PII_EXPOSURE = "pii_exposure"
    CORS_MISCONFIGURATION = "cors_misconfiguration"
    ERROR_INFO_LEAK = "error_info_leak"
    SENSITIVE_LOGGING = "sensitive_logging"
    PUBLIC_DATABASE = "public_database"


class ExposureSeverity(Enum):
    """Severity of exposure risks"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ExposureFinding:
    """Exposure security finding"""
    exposure_type: ExposureType
    severity: ExposureSeverity
    node_id: str
    node_name: str
    node_type: str
    description: str
    risk: str
    recommendation: str
    affected_field: Optional[str] = None
    exposed_data: Optional[List[str]] = None

    def to_dict(self) -> Dict:
        return {
            "exposure_type": self.exposure_type.value,
            "severity": self.severity.value,
            "node_id": self.node_id,
            "node_name": self.node_name,
            "node_type": self.node_type,
            "description": self.description,
            "risk": self.risk,
            "recommendation": self.recommendation,
            "affected_field": self.affected_field,
            "exposed_data": self.exposed_data or []
        }


class ExposureAnalyzer:
    """
    Analyzes workflows for exposure risks and data leaks
    """

    # PII field patterns
    PII_PATTERNS = {
        "email", "mail", "e-mail",
        "phone", "telephone", "mobile", "cell",
        "ssn", "social_security",
        "passport", "driver_license", "id_number",
        "address", "street", "zip", "postal",
        "dob", "date_of_birth", "birthday",
        "credit_card", "card_number", "cvv",
        "password", "pin", "secret",
        "salary", "income", "wage",
        "medical", "health", "diagnosis",
        "tax_id", "ein", "vat",
    }

    # Sensitive data keywords
    SENSITIVE_KEYWORDS = {
        "token", "key", "secret", "password", "credential",
        "auth", "bearer", "jwt", "session", "cookie"
    }

    def __init__(self):
        pass

    def analyze_workflow(self, workflow: Dict) -> List[ExposureFinding]:
        """
        Analyze entire workflow for exposure risks

        Args:
            workflow: Workflow dict

        Returns:
            List of ExposureFinding objects
        """
        findings = []

        nodes = workflow.get("nodes", [])

        # Check for public triggers
        trigger_nodes = [n for n in nodes if "trigger" in n.get("type", "").lower()]
        for trigger in trigger_nodes:
            findings.extend(self._analyze_trigger_exposure(trigger))

        # Check each node for data exposure
        for node in nodes:
            findings.extend(self._analyze_node_exposure(node))

        # Check for data flow issues
        findings.extend(self._analyze_data_flow(workflow))

        return findings

    def _analyze_trigger_exposure(self, node: Dict) -> List[ExposureFinding]:
        """Analyze trigger node for public exposure"""
        findings = []
        node_id = node.get("id", "unknown")
        node_name = node.get("name", "Unknown")
        node_type = node.get("type", "unknown")
        params = node.get("parameters", {})

        # Webhook trigger without auth
        if "webhook" in node_type.lower():
            auth_mode = params.get("authentication", "none")

            if auth_mode == "none" or not auth_mode:
                # Check HTTP method
                http_method = params.get("httpMethod", "POST")
                path = params.get("path", "")

                findings.append(ExposureFinding(
                    exposure_type=ExposureType.PUBLIC_WEBHOOK,
                    severity=ExposureSeverity.CRITICAL,
                    node_id=node_id,
                    node_name=node_name,
                    node_type=node_type,
                    description=f"Public webhook endpoint without authentication: {http_method} /{path}",
                    risk="Anyone on the internet can trigger this workflow and send data to it",
                    recommendation="Add webhook authentication (Header Auth, Basic Auth, or IP Whitelist)",
                    affected_field="parameters.authentication"
                ))

            # Check for CORS issues
            cors = params.get("options", {}).get("cors", {})
            if cors and cors.get("enabled"):
                origin = cors.get("origin", "*")
                if origin == "*":
                    findings.append(ExposureFinding(
                        exposure_type=ExposureType.CORS_MISCONFIGURATION,
                        severity=ExposureSeverity.HIGH,
                        node_id=node_id,
                        node_name=node_name,
                        node_type=node_type,
                        description="CORS configured with wildcard origin (*)",
                        risk="Any website can make requests to this webhook",
                        recommendation="Restrict CORS to specific trusted origins",
                        affected_field="parameters.options.cors.origin"
                    ))

        return findings

    def _analyze_node_exposure(self, node: Dict) -> List[ExposureFinding]:
        """Analyze individual node for data exposure"""
        findings = []
        node_id = node.get("id", "unknown")
        node_name = node.get("name", "Unknown")
        node_type = node.get("type", "unknown")
        params = node.get("parameters", {})

        # Check HTTP Response nodes for data leaks
        if "respond" in node_type.lower() or "response" in node_name.lower():
            findings.extend(self._check_response_exposure(node))

        # Check for error handling that might leak info
        if "error" in node_type.lower():
            findings.extend(self._check_error_exposure(node))

        # Check for PII in logging or outputs
        findings.extend(self._check_pii_exposure(node))

        # Check Set/Function nodes for sensitive operations
        if any(t in node_type.lower() for t in ["set", "function", "code"]):
            findings.extend(self._check_code_exposure(node))

        return findings

    def _check_response_exposure(self, node: Dict) -> List[ExposureFinding]:
        """Check HTTP response nodes for data leaks"""
        findings = []
        node_id = node.get("id", "unknown")
        node_name = node.get("name", "Unknown")
        node_type = node.get("type", "unknown")
        params = node.get("parameters", {})

        # Check what's being returned
        response_data = params.get("options", {}).get("responseData", "")

        # Look for sensitive data in response
        exposed_fields = []
        for sensitive in self.SENSITIVE_KEYWORDS:
            if sensitive in str(response_data).lower():
                exposed_fields.append(sensitive)

        if exposed_fields:
            findings.append(ExposureFinding(
                exposure_type=ExposureType.DATA_LEAK,
                severity=ExposureSeverity.HIGH,
                node_id=node_id,
                node_name=node_name,
                node_type=node_type,
                description=f"Response may include sensitive data: {', '.join(exposed_fields)}",
                risk="Sensitive data could be exposed to API consumers",
                recommendation="Filter sensitive fields before responding",
                affected_field="parameters.options.responseData",
                exposed_data=exposed_fields
            ))

        return findings

    def _check_error_exposure(self, node: Dict) -> List[ExposureFinding]:
        """Check error handling for information leaks"""
        findings = []
        node_id = node.get("id", "unknown")
        node_name = node.get("name", "Unknown")
        node_type = node.get("type", "unknown")
        params = node.get("parameters", {})

        # Check if error messages are being sent externally
        message = params.get("message", "")
        if "{{" in message and "$json" in message:
            findings.append(ExposureFinding(
                exposure_type=ExposureType.ERROR_INFO_LEAK,
                severity=ExposureSeverity.MEDIUM,
                node_id=node_id,
                node_name=node_name,
                node_type=node_type,
                description="Error handler may expose internal error details",
                risk="Stack traces or internal errors could reveal system information",
                recommendation="Sanitize error messages before sending externally",
                affected_field="parameters.message"
            ))

        return findings

    def _check_pii_exposure(self, node: Dict) -> List[ExposureFinding]:
        """Check node for PII exposure"""
        findings = []
        node_id = node.get("id", "unknown")
        node_name = node.get("name", "Unknown")
        node_type = node.get("type", "unknown")
        params = node.get("parameters", {})

        # Check parameters for PII field names
        pii_fields = self._find_pii_fields(params)

        if pii_fields:
            # Check if this node sends data externally
            is_external = any(t in node_type.lower() for t in [
                "http", "webhook", "slack", "email", "telegram"
            ])

            if is_external:
                findings.append(ExposureFinding(
                    exposure_type=ExposureType.PII_EXPOSURE,
                    severity=ExposureSeverity.HIGH,
                    node_id=node_id,
                    node_name=node_name,
                    node_type=node_type,
                    description=f"Node may expose PII: {', '.join(pii_fields)}",
                    risk="Personal Identifiable Information could be sent externally",
                    recommendation="Ensure PII is properly anonymized or encrypted before external transmission",
                    exposed_data=pii_fields
                ))

        return findings

    def _check_code_exposure(self, node: Dict) -> List[ExposureFinding]:
        """Check code nodes for exposure risks"""
        findings = []
        node_id = node.get("id", "unknown")
        node_name = node.get("name", "Unknown")
        node_type = node.get("type", "unknown")
        params = node.get("parameters", {})

        # Check for console.log or similar that might log sensitive data
        code = params.get("jsCode", "") or params.get("code", "")

        if "console.log" in code or "print(" in code:
            # Check if logging sensitive data
            for sensitive in self.SENSITIVE_KEYWORDS:
                if sensitive in code.lower():
                    findings.append(ExposureFinding(
                        exposure_type=ExposureType.SENSITIVE_LOGGING,
                        severity=ExposureSeverity.MEDIUM,
                        node_id=node_id,
                        node_name=node_name,
                        node_type=node_type,
                        description=f"Code logs potentially sensitive data: '{sensitive}'",
                        risk="Sensitive information could be exposed in n8n execution logs",
                        recommendation="Remove console.log statements or sanitize logged data",
                        affected_field="parameters.jsCode"
                    ))
                    break

        return findings

    def _analyze_data_flow(self, workflow: Dict) -> List[ExposureFinding]:
        """Analyze overall workflow data flow for exposure"""
        findings = []

        nodes = workflow.get("nodes", [])
        connections = workflow.get("connections", {})

        # Check for public trigger → database write
        trigger_nodes = [n for n in nodes if "trigger" in n.get("type", "").lower()]
        db_nodes = [n for n in nodes if any(
            db in n.get("type", "").lower()
            for db in ["postgres", "mysql", "mongodb"]
        )]

        for trigger in trigger_nodes:
            # Check if trigger is public
            if "webhook" in trigger.get("type", "").lower():
                params = trigger.get("parameters", {})
                auth = params.get("authentication", "none")

                if auth == "none":
                    # Check if this trigger connects to database
                    trigger_name = trigger.get("name", "")
                    if trigger_name in connections:
                        # Trace connections
                        for db_node in db_nodes:
                            if self._nodes_connected(trigger, db_node, connections):
                                findings.append(ExposureFinding(
                                    exposure_type=ExposureType.PUBLIC_DATABASE,
                                    severity=ExposureSeverity.CRITICAL,
                                    node_id=trigger.get("id", ""),
                                    node_name=trigger.get("name", ""),
                                    node_type=trigger.get("type", ""),
                                    description="Public webhook directly writes to database without authentication",
                                    risk="Anyone can insert/modify database records via unauthenticated webhook",
                                    recommendation="Add authentication to webhook OR add validation/authorization before database write",
                                    affected_field="authentication"
                                ))
                                break

        return findings

    def _find_pii_fields(self, data: Dict, path: str = "") -> List[str]:
        """Recursively find PII field names in data"""
        pii_fields = []

        if isinstance(data, dict):
            for key, value in data.items():
                key_lower = key.lower()
                # Check if key name suggests PII
                if any(pii in key_lower for pii in self.PII_PATTERNS):
                    field_path = f"{path}.{key}" if path else key
                    pii_fields.append(field_path)

                # Recurse
                if isinstance(value, dict):
                    pii_fields.extend(self._find_pii_fields(value, f"{path}.{key}" if path else key))

        return pii_fields

    def _nodes_connected(self, node1: Dict, node2: Dict, connections: Dict) -> bool:
        """Check if two nodes are connected (directly or indirectly)"""
        # Simple direct connection check
        node1_name = node1.get("name", "")
        node2_name = node2.get("name", "")

        if node1_name in connections:
            outputs = connections[node1_name]
            # Check all output connections
            for output_key, connection_list in outputs.items():
                for conn in connection_list:
                    if conn.get("node") == node2_name:
                        return True

        return False
