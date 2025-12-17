"""
Node Version Compatibility Checker

Checks if workflow nodes are compatible with current n8n version
and identifies outdated parameters/configurations.
"""
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum


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

    def __init__(self):
        # Known node versions and their breaking changes
        self.node_versions = {
            "n8n-nodes-base.httpRequest": {
                "1": {"deprecated": False},
                "2": {"deprecated": False},
                "3": {"deprecated": False, "changes": ["authentication moved to credentials"]},
                "4": {"deprecated": False, "changes": ["new authentication options"]},
            },
            "n8n-nodes-base.postgres": {
                "1": {"deprecated": False},
                "2": {"deprecated": False, "changes": ["query parameters changed"]},
            },
            "n8n-nodes-base.slack": {
                "1": {"deprecated": True, "replacement": "n8n-nodes-base.slack"},
                "2": {"deprecated": False, "changes": ["new message formatting"]},
            },
            "n8n-nodes-base.webhook": {
                "1": {"deprecated": False},
                "2": {"deprecated": False, "changes": ["new response options"]},
            },
        }

        # Known deprecated parameters
        self.deprecated_parameters = {
            "n8n-nodes-base.httpRequest": {
                "url": {"since": "v3", "replacement": "requestUrl"},
                "method": {"since": "v3", "replacement": "requestMethod"},
            },
            "n8n-nodes-base.postgres": {
                "operation": {"values": {"executeQuery": {"since": "v2", "replacement": "query"}}},
            },
        }

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

        # Check if node type exists in our knowledge base
        if node_type not in self.node_versions:
            issues.append(CompatibilityIssue(
                node_name=node_name,
                node_type=node_type,
                issue_type="unknown_node",
                severity="low",
                description=f"Node type '{node_type}' is not in compatibility database",
                migration_available=False,
            ))
            return issues

        # Check node version
        version_info = self.node_versions[node_type].get(str(type_version))
        if not version_info:
            issues.append(CompatibilityIssue(
                node_name=node_name,
                node_type=node_type,
                issue_type="version_mismatch",
                severity="medium",
                description=f"Node version {type_version} is unknown. Latest might be available.",
                suggested_fix=f"Consider updating to latest version",
                migration_available=True,
            ))
        elif version_info.get("deprecated"):
            replacement = version_info.get("replacement", "unknown")
            issues.append(CompatibilityIssue(
                node_name=node_name,
                node_type=node_type,
                issue_type="deprecated_node",
                severity="high",
                description=f"Node type is deprecated",
                suggested_fix=f"Migrate to: {replacement}",
                migration_available=True,
            ))

        # Check for deprecated parameters
        if node_type in self.deprecated_parameters:
            deprecated_params = self.deprecated_parameters[node_type]

            for param_name, param_info in deprecated_params.items():
                if param_name in parameters:
                    # Check if specific value is deprecated
                    if "values" in param_info:
                        param_value = parameters[param_name]
                        if param_value in param_info["values"]:
                            value_info = param_info["values"][param_value]
                            issues.append(CompatibilityIssue(
                                node_name=node_name,
                                node_type=node_type,
                                issue_type="deprecated_parameter",
                                severity="medium",
                                description=f"Parameter value '{param_name}={param_value}' is deprecated since {value_info['since']}",
                                old_value=str(param_value),
                                suggested_fix=f"Use '{value_info['replacement']}' instead",
                                migration_available=True,
                            ))
                    else:
                        issues.append(CompatibilityIssue(
                            node_name=node_name,
                            node_type=node_type,
                            issue_type="deprecated_parameter",
                            severity="medium",
                            description=f"Parameter '{param_name}' is deprecated since {param_info['since']}",
                            old_value=str(parameters[param_name]),
                            suggested_fix=f"Use '{param_info['replacement']}' instead",
                            migration_available=True,
                        ))

        # Check for missing required parameters (if we have schema info)
        # This could be extended with actual n8n node schemas

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
