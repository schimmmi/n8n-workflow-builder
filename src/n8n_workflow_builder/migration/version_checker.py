"""
Node Version Compatibility Checker

Checks if workflow nodes are compatible with current n8n version
and identifies outdated parameters/configurations.
"""
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum
import json
import os
from pathlib import Path


class CompatibilityStatus(Enum):
    """Compatibility status levels"""
    COMPATIBLE = "compatible"
    DEPRECATED = "deprecated"
    BREAKING = "breaking"
    UNKNOWN = "unknown"


@dataclass
class CompatibilityIssue:
    """Represents a compatibility issue"""
    node_name: str
    node_type: str
    issue_type: str  # "deprecated_parameter", "breaking_change", "missing_parameter", "version_mismatch"
    severity: str  # "low", "medium", "high", "critical"
    description: str
    old_value: Optional[str] = None
    suggested_fix: Optional[str] = None
    migration_available: bool = False


@dataclass
class CompatibilityResult:
    """Result of compatibility check"""
    status: CompatibilityStatus
    issues: List[CompatibilityIssue]
    n8n_version: Optional[str] = None
    workflow_version: Optional[str] = None

    @property
    def has_issues(self) -> bool:
        return len(self.issues) > 0

    @property
    def has_breaking_changes(self) -> bool:
        return any(issue.severity == "critical" for issue in self.issues)


class NodeVersionChecker:
    """
    Checks node compatibility with current n8n version
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize checker with compatibility database

        Args:
            db_path: Path to compatibility_db.json (defaults to package directory)
        """
        if db_path is None:
            # Default to compatibility_db.json in same directory
            current_dir = Path(__file__).parent
            db_path = current_dir / "compatibility_db.json"

        self.db_path = db_path
        self.compatibility_db = self._load_compatibility_db()

        # Legacy format for backward compatibility
        self.node_versions = self._build_node_versions()
        self.deprecated_parameters = self._build_deprecated_parameters()

    def _load_compatibility_db(self) -> Dict:
        """Load compatibility database from JSON file"""
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Fallback to empty database if file doesn't exist
            return {
                "nodes": {},
                "n8n_versions": {},
                "metadata": {"version": "1.0.0", "total_nodes": 0}
            }
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid compatibility database JSON: {e}")

    def _build_node_versions(self) -> Dict:
        """Build legacy node_versions format from database"""
        node_versions = {}
        for node_type, node_data in self.compatibility_db.get("nodes", {}).items():
            versions = {}
            for version, version_data in node_data.get("versions", {}).items():
                status = version_data.get("status", "unknown")
                versions[version] = {
                    "deprecated": status == "deprecated",
                    "changes": [issue["message"] for issue in version_data.get("issues", [])]
                }
            node_versions[node_type] = versions
        return node_versions

    def _build_deprecated_parameters(self) -> Dict:
        """Build legacy deprecated_parameters format from database"""
        deprecated_params = {}
        for node_type, node_data in self.compatibility_db.get("nodes", {}).items():
            params = {}
            for version, version_data in node_data.get("versions", {}).items():
                for issue in version_data.get("issues", []):
                    if issue["type"] == "deprecated_parameter":
                        param_name = issue.get("parameter")
                        if param_name:
                            # Extract replacement from fix message if available
                            fix = issue.get("fix", "")
                            replacement = None
                            if "Rename" in fix and "to" in fix:
                                # Extract: "Rename 'url' to 'requestUrl'" -> "requestUrl"
                                parts = fix.split("to")
                                if len(parts) > 1:
                                    replacement = parts[1].strip().strip("'\"")

                            params[param_name] = {
                                "since": f"v{version}",
                                "replacement": replacement
                            }
            if params:
                deprecated_params[node_type] = params
        return deprecated_params

    def check_workflow_compatibility(self, workflow: Dict) -> CompatibilityResult:
        """
        Check entire workflow for compatibility issues

        Args:
            workflow: Workflow JSON object

        Returns:
            CompatibilityResult with all issues found
        """
        issues = []
        nodes = workflow.get("nodes", [])

        for node in nodes:
            node_issues = self.check_node_compatibility(node)
            issues.extend(node_issues)

        # Determine overall status
        if not issues:
            status = CompatibilityStatus.COMPATIBLE
        elif any(issue.severity == "critical" for issue in issues):
            status = CompatibilityStatus.BREAKING
        elif any(issue.severity in ["high", "medium"] for issue in issues):
            status = CompatibilityStatus.DEPRECATED
        else:
            status = CompatibilityStatus.COMPATIBLE

        return CompatibilityResult(
            status=status,
            issues=issues,
            workflow_version=workflow.get("version"),
        )

    def check_node_compatibility(self, node: Dict) -> List[CompatibilityIssue]:
        """
        Check a single node for compatibility issues

        Args:
            node: Node object

        Returns:
            List of compatibility issues
        """
        issues = []
        node_type = node.get("type", "")
        node_name = node.get("name", "")
        type_version = node.get("typeVersion", 1)
        parameters = node.get("parameters", {})

        # Check if node type exists in compatibility database
        node_data = self.compatibility_db.get("nodes", {}).get(node_type)

        if not node_data:
            # Node not in database
            issues.append(CompatibilityIssue(
                node_name=node_name,
                node_type=node_type,
                issue_type="unknown_node",
                severity="low",
                description=f"Node type '{node_type}' is not in compatibility database",
                migration_available=False,
            ))
            return issues

        # Get current version from database
        current_version = node_data.get("current_version")
        versions = node_data.get("versions", {})

        # Check if node's version exists in database
        version_str = str(type_version)
        if version_str not in versions:
            # Try with float format (e.g., "4.2")
            version_float = float(type_version)
            version_str = str(version_float)

        version_data = versions.get(version_str)

        if not version_data:
            issues.append(CompatibilityIssue(
                node_name=node_name,
                node_type=node_type,
                issue_type="version_mismatch",
                severity="medium",
                description=f"Version {type_version} is unknown. Current version: {current_version}",
                suggested_fix=f"Consider updating to version {current_version}",
                migration_available=True,
            ))
            return issues

        # Check version status
        status = version_data.get("status", "unknown")

        if status == "deprecated":
            deprecated_since = version_data.get("deprecated_since", "unknown")
            issues.append(CompatibilityIssue(
                node_name=node_name,
                node_type=node_type,
                issue_type="deprecated_node",
                severity="high",
                description=f"Node version {type_version} is deprecated since n8n {deprecated_since}",
                suggested_fix=f"Update to version {current_version}",
                migration_available=True,
            ))

        # Add all issues from database for this version
        for issue_data in version_data.get("issues", []):
            issue_type = issue_data.get("type", "unknown")
            severity = issue_data.get("severity", "low")
            message = issue_data.get("message", "No description")
            fix = issue_data.get("fix", None)
            parameter = issue_data.get("parameter", None)

            # Check if deprecated parameter actually exists in node
            if issue_type == "deprecated_parameter" and parameter:
                if parameter not in parameters:
                    # Parameter not used, skip this issue
                    continue

            issues.append(CompatibilityIssue(
                node_name=node_name,
                node_type=node_type,
                issue_type=issue_type,
                severity=severity,
                description=message,
                old_value=parameter,
                suggested_fix=fix,
                migration_available=True,
            ))

        return issues

    def get_latest_node_version(self, node_type: str) -> Optional[int]:
        """
        Get the latest known version for a node type

        Args:
            node_type: Node type name

        Returns:
            Latest version number or None
        """
        if node_type not in self.node_versions:
            return None

        versions = [int(v) for v in self.node_versions[node_type].keys()]
        return max(versions) if versions else None

    def is_parameter_deprecated(self, node_type: str, parameter: str, value: Optional[str] = None) -> bool:
        """
        Check if a parameter is deprecated

        Args:
            node_type: Node type name
            parameter: Parameter name
            value: Optional parameter value to check

        Returns:
            True if deprecated
        """
        if node_type not in self.deprecated_parameters:
            return False

        deprecated_params = self.deprecated_parameters[node_type]
        if parameter not in deprecated_params:
            return False

        param_info = deprecated_params[parameter]

        # Check if specific value is deprecated
        if value and "values" in param_info:
            return value in param_info["values"]

        return True
