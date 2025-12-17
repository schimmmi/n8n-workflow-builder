"""
Secret Detection Engine

Detects hardcoded secrets, API keys, passwords, and credentials in workflows.
"""

import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class SecretType(Enum):
    """Types of secrets that can be detected"""
    API_KEY = "api_key"
    AWS_KEY = "aws_key"
    PRIVATE_KEY = "private_key"
    PASSWORD = "password"
    TOKEN = "token"
    OAUTH_SECRET = "oauth_secret"
    DATABASE_URL = "database_url"
    JWT = "jwt"
    GENERIC_SECRET = "generic_secret"
    ENCRYPTION_KEY = "encryption_key"
    WEBHOOK_SECRET = "webhook_secret"


class SecretSeverity(Enum):
    """Severity levels for detected secrets"""
    CRITICAL = "critical"  # Confirmed secret with high confidence
    HIGH = "high"          # Likely secret
    MEDIUM = "medium"      # Possible secret
    LOW = "low"            # Suspicious pattern


@dataclass
class SecretFinding:
    """Represents a detected secret"""
    secret_type: SecretType
    severity: SecretSeverity
    node_id: str
    node_name: str
    field_path: str  # e.g., "parameters.authentication.apiKey"
    value_preview: str  # First/last few chars for identification
    confidence: float  # 0.0 - 1.0
    line_number: Optional[int] = None
    recommendation: str = ""

    def to_dict(self) -> Dict:
        return {
            "secret_type": self.secret_type.value,
            "severity": self.severity.value,
            "node_id": self.node_id,
            "node_name": self.node_name,
            "field_path": self.field_path,
            "value_preview": self.value_preview,
            "confidence": self.confidence,
            "line_number": self.line_number,
            "recommendation": self.recommendation
        }


class SecretDetector:
    """
    Detects hardcoded secrets in n8n workflows using pattern matching
    and entropy analysis.
    """

    # High-confidence patterns for specific services
    PATTERNS = {
        SecretType.AWS_KEY: [
            (r'AKIA[0-9A-Z]{16}', 0.95),  # AWS Access Key
            (r'aws_access_key_id\s*[=:]\s*["\']?([A-Z0-9]{20})["\']?', 0.90),
            (r'aws_secret_access_key\s*[=:]\s*["\']?([A-Za-z0-9/+=]{40})["\']?', 0.95),
        ],
        SecretType.PRIVATE_KEY: [
            (r'-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----', 0.99),
            (r'-----BEGIN PGP PRIVATE KEY BLOCK-----', 0.99),
        ],
        SecretType.TOKEN: [
            (r'ghp_[a-zA-Z0-9]{36}', 0.95),  # GitHub Personal Access Token
            (r'gho_[a-zA-Z0-9]{36}', 0.95),  # GitHub OAuth Token
            (r'github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}', 0.95),  # GitHub Fine-grained PAT
            (r'glpat-[a-zA-Z0-9\-_]{20,}', 0.95),  # GitLab PAT
            (r'sk-[a-zA-Z0-9]{48}', 0.90),  # OpenAI API Key
            (r'xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24,}', 0.95),  # Slack Token
        ],
        SecretType.JWT: [
            (r'eyJ[A-Za-z0-9-_=]+\.eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_.+/=]*', 0.85),
        ],
        SecretType.DATABASE_URL: [
            (r'(?:postgres|postgresql|mysql|mongodb|redis)://[^:]+:[^@]+@[^/]+', 0.90),
            (r'(?:postgres|postgresql|mysql|mongodb|redis)://[^:]+:[^@]+@', 0.85),
        ],
        SecretType.API_KEY: [
            (r'api[_-]?key\s*[=:]\s*["\']([a-zA-Z0-9]{32,})["\']', 0.85),
            (r'apikey\s*[=:]\s*["\']([a-zA-Z0-9]{32,})["\']', 0.85),
            (r'api[_-]?secret\s*[=:]\s*["\']([a-zA-Z0-9]{32,})["\']', 0.90),
        ],
        SecretType.PASSWORD: [
            (r'password\s*[=:]\s*["\']([^"\']{8,})["\']', 0.70),
            (r'passwd\s*[=:]\s*["\']([^"\']{8,})["\']', 0.70),
            (r'pwd\s*[=:]\s*["\']([^"\']{8,})["\']', 0.65),
        ],
        SecretType.OAUTH_SECRET: [
            (r'client[_-]?secret\s*[=:]\s*["\']([a-zA-Z0-9]{32,})["\']', 0.90),
            (r'oauth[_-]?secret\s*[=:]\s*["\']([a-zA-Z0-9]{32,})["\']', 0.90),
        ],
        SecretType.WEBHOOK_SECRET: [
            (r'webhook[_-]?secret\s*[=:]\s*["\']([a-zA-Z0-9]{20,})["\']', 0.85),
            (r'signing[_-]?secret\s*[=:]\s*["\']([a-zA-Z0-9]{20,})["\']', 0.85),
        ],
        SecretType.ENCRYPTION_KEY: [
            (r'encryption[_-]?key\s*[=:]\s*["\']([a-zA-Z0-9+/=]{32,})["\']', 0.90),
            (r'secret[_-]?key\s*[=:]\s*["\']([a-zA-Z0-9+/=]{32,})["\']', 0.80),
        ],
    }

    # Patterns to ignore (false positives)
    WHITELIST_PATTERNS = [
        r'\{\{.*\}\}',  # n8n expressions
        r'\$\{.*\}',    # Environment variables
        r'\$.*\$',      # Variables
        r'{{.*}}',      # Template variables
        r'<.*>',        # Placeholders
        r'example\.com',
        r'localhost',
        r'127\.0\.0\.1',
        r'0\.0\.0\.0',
        r'xxx+',
        r'\*{3,}',
        r'test',
        r'dummy',
        r'placeholder',
        r'your[_-]?',
    ]

    # High-entropy strings are suspicious
    MIN_ENTROPY = 4.0  # Shannon entropy threshold

    def __init__(self):
        self.compiled_patterns = {}
        self.compiled_whitelist = [re.compile(p, re.IGNORECASE) for p in self.WHITELIST_PATTERNS]

        # Compile all detection patterns
        for secret_type, patterns in self.PATTERNS.items():
            self.compiled_patterns[secret_type] = [
                (re.compile(pattern, re.IGNORECASE | re.MULTILINE), confidence)
                for pattern, confidence in patterns
            ]

    def scan_workflow(self, workflow: Dict) -> List[SecretFinding]:
        """
        Scan entire workflow for hardcoded secrets

        Args:
            workflow: Workflow data dict with nodes

        Returns:
            List of SecretFinding objects
        """
        findings = []

        nodes = workflow.get("nodes", [])
        for node in nodes:
            node_findings = self.scan_node(node)
            findings.extend(node_findings)

        return findings

    def scan_node(self, node: Dict) -> List[SecretFinding]:
        """
        Scan a single node for secrets

        Args:
            node: Node data dict

        Returns:
            List of SecretFinding objects
        """
        findings = []
        node_id = node.get("id", "unknown")
        node_name = node.get("name", "Unknown")

        # Scan parameters
        parameters = node.get("parameters", {})
        findings.extend(self._scan_dict(parameters, node_id, node_name, "parameters"))

        # Scan credentials (shouldn't have hardcoded values, but check anyway)
        credentials = node.get("credentials", {})
        if isinstance(credentials, dict):
            findings.extend(self._scan_dict(credentials, node_id, node_name, "credentials"))

        return findings

    def _scan_dict(
        self,
        data: Dict,
        node_id: str,
        node_name: str,
        base_path: str = ""
    ) -> List[SecretFinding]:
        """Recursively scan dictionary for secrets"""
        findings = []

        for key, value in data.items():
            current_path = f"{base_path}.{key}" if base_path else key

            if isinstance(value, str):
                # Scan string values
                findings.extend(
                    self._scan_string(value, node_id, node_name, current_path)
                )
            elif isinstance(value, dict):
                # Recurse into nested dicts
                findings.extend(
                    self._scan_dict(value, node_id, node_name, current_path)
                )
            elif isinstance(value, list):
                # Scan list items
                for i, item in enumerate(value):
                    if isinstance(item, str):
                        findings.extend(
                            self._scan_string(item, node_id, node_name, f"{current_path}[{i}]")
                        )
                    elif isinstance(item, dict):
                        findings.extend(
                            self._scan_dict(item, node_id, node_name, f"{current_path}[{i}]")
                        )

        return findings

    def _scan_string(
        self,
        value: str,
        node_id: str,
        node_name: str,
        field_path: str
    ) -> List[SecretFinding]:
        """Scan individual string value for secrets"""
        findings = []

        # Skip empty or very short strings
        if not value or len(value) < 8:
            return findings

        # Check if whitelisted (false positive)
        if self._is_whitelisted(value):
            return findings

        # Pattern-based detection
        for secret_type, patterns in self.compiled_patterns.items():
            for pattern, confidence in patterns:
                matches = pattern.finditer(value)
                for match in matches:
                    finding = SecretFinding(
                        secret_type=secret_type,
                        severity=self._determine_severity(confidence),
                        node_id=node_id,
                        node_name=node_name,
                        field_path=field_path,
                        value_preview=self._create_preview(value),
                        confidence=confidence,
                        recommendation=self._get_recommendation(secret_type)
                    )
                    findings.append(finding)

        # Entropy-based detection for generic secrets
        if not findings and len(value) >= 20:
            entropy = self._calculate_entropy(value)
            if entropy >= self.MIN_ENTROPY:
                # High entropy string without spaces - likely encoded/encrypted
                if ' ' not in value and self._looks_like_secret(value):
                    finding = SecretFinding(
                        secret_type=SecretType.GENERIC_SECRET,
                        severity=SecretSeverity.MEDIUM,
                        node_id=node_id,
                        node_name=node_name,
                        field_path=field_path,
                        value_preview=self._create_preview(value),
                        confidence=min(0.7, entropy / 6.0),  # Scale entropy to confidence
                        recommendation="High-entropy string detected. If this is a secret, use n8n credentials instead."
                    )
                    findings.append(finding)

        return findings

    def _is_whitelisted(self, value: str) -> bool:
        """Check if value matches whitelist patterns"""
        for pattern in self.compiled_whitelist:
            if pattern.search(value):
                return True
        return False

    def _calculate_entropy(self, value: str) -> float:
        """Calculate Shannon entropy of string"""
        if not value:
            return 0.0

        # Count character frequencies
        char_counts = {}
        for char in value:
            char_counts[char] = char_counts.get(char, 0) + 1

        # Calculate entropy
        length = len(value)
        entropy = 0.0
        for count in char_counts.values():
            probability = count / length
            if probability > 0:
                entropy -= probability * (probability ** 0.5)  # Shannon entropy formula

        return entropy * 10  # Scale for readability

    def _looks_like_secret(self, value: str) -> bool:
        """Heuristic check if string looks like a secret"""
        # Check for mix of character types
        has_upper = any(c.isupper() for c in value)
        has_lower = any(c.islower() for c in value)
        has_digit = any(c.isdigit() for c in value)
        has_special = any(not c.isalnum() for c in value)

        # Secrets usually have multiple character types
        char_type_count = sum([has_upper, has_lower, has_digit, has_special])

        return char_type_count >= 2

    def _determine_severity(self, confidence: float) -> SecretSeverity:
        """Map confidence to severity"""
        if confidence >= 0.90:
            return SecretSeverity.CRITICAL
        elif confidence >= 0.75:
            return SecretSeverity.HIGH
        elif confidence >= 0.60:
            return SecretSeverity.MEDIUM
        else:
            return SecretSeverity.LOW

    def _create_preview(self, value: str) -> str:
        """Create safe preview of secret value"""
        if len(value) <= 16:
            # Short value - show first 4 chars
            return f"{value[:4]}{'*' * (len(value) - 4)}"
        else:
            # Long value - show first 4 and last 4
            return f"{value[:4]}...{'*' * 8}...{value[-4:]}"

    def _get_recommendation(self, secret_type: SecretType) -> str:
        """Get remediation recommendation for secret type"""
        recommendations = {
            SecretType.API_KEY: "Use n8n credentials instead of hardcoding API keys. Create a credential of type 'API Key' and reference it.",
            SecretType.AWS_KEY: "Use n8n AWS credentials. Never hardcode AWS access keys.",
            SecretType.PRIVATE_KEY: "Store private keys in n8n credentials with type 'Private Key'. Never commit private keys.",
            SecretType.PASSWORD: "Use n8n credentials to store passwords securely. Enable 'Password' credential type.",
            SecretType.TOKEN: "Store tokens in n8n credentials. Use OAuth credentials where possible.",
            SecretType.OAUTH_SECRET: "Use n8n OAuth2 credentials. Never hardcode client secrets.",
            SecretType.DATABASE_URL: "Use n8n database credentials. Split connection details into separate credential fields.",
            SecretType.JWT: "Store JWT tokens in credentials or environment variables. Never hardcode JWTs.",
            SecretType.GENERIC_SECRET: "This appears to be a secret. Use n8n credentials or environment variables.",
            SecretType.ENCRYPTION_KEY: "Store encryption keys in n8n credentials. Use secure key management.",
            SecretType.WEBHOOK_SECRET: "Use n8n webhook authentication settings. Store secrets in credentials.",
        }
        return recommendations.get(secret_type, "Use n8n credentials instead of hardcoding secrets.")
