"""
Workflow Updater

High-level interface for updating workflows with migrations.
"""
from typing import Dict, List, Optional, Tuple
import copy
import logging

from .version_checker import NodeVersionChecker, CompatibilityResult, CompatibilityStatus
from .migration_engine import MigrationEngine, MigrationRule
from .migration_rules import MIGRATION_RULES

logger = logging.getLogger("n8n-workflow-builder")


class WorkflowUpdater:
    """
    High-level workflow updater with automatic migration
    """

    def __init__(self, migration_rules: Optional[List[MigrationRule]] = None):
        """
        Initialize updater

        Args:
            migration_rules: Custom migration rules (defaults to MIGRATION_RULES)
        """
        self.version_checker = NodeVersionChecker()
        self.migration_engine = MigrationEngine(migration_rules or MIGRATION_RULES)

    def check_and_update(
        self,
        workflow: Dict,
        auto_migrate: bool = True,
        dry_run: bool = False
    ) -> Tuple[Dict, CompatibilityResult, List[Dict]]:
        """
        Check workflow compatibility and optionally auto-migrate

        Args:
            workflow: Workflow JSON
            auto_migrate: If True, automatically apply migrations
            dry_run: If True, don't modify original workflow

        Returns:
            Tuple of (updated_workflow, compatibility_result, migration_log)
        """
        # First check compatibility
        compatibility = self.version_checker.check_workflow_compatibility(workflow)

        if not auto_migrate or compatibility.status == CompatibilityStatus.COMPATIBLE:
            return workflow, compatibility, []

        # Migrate workflow
        logger.info(f"Auto-migrating workflow: {workflow.get('name', 'Unknown')}")
        updated_workflow = self.migration_engine.migrate_workflow(workflow, dry_run=dry_run)

        # Get migration log from metadata
        migration_log = updated_workflow.get("meta", {}).get("lastMigration", {})

        # Re-check compatibility after migration
        new_compatibility = self.version_checker.check_workflow_compatibility(updated_workflow)

        return updated_workflow, new_compatibility, migration_log

    def update_node(
        self,
        node: Dict,
        target_version: Optional[int] = None
    ) -> Tuple[Dict, List[Dict]]:
        """
        Update a single node to target version

        Args:
            node: Node object
            target_version: Target version (or latest if None)

        Returns:
            Tuple of (updated_node, migration_log)
        """
        return self.migration_engine.migrate_node(node, target_version)

    def get_update_preview(self, workflow: Dict) -> Dict:
        """
        Get preview of what would change without applying updates

        Args:
            workflow: Workflow JSON

        Returns:
            Dictionary with preview information
        """
        compatibility = self.version_checker.check_workflow_compatibility(workflow)

        # Dry run migration
        updated_workflow = self.migration_engine.migrate_workflow(workflow, dry_run=True)

        # Calculate changes
        changes = []
        for i, (old_node, new_node) in enumerate(zip(
            workflow.get("nodes", []),
            updated_workflow.get("nodes", [])
        )):
            if old_node != new_node:
                changes.append({
                    "node_name": old_node.get("name"),
                    "node_type": old_node.get("type"),
                    "old_version": old_node.get("typeVersion"),
                    "new_version": new_node.get("typeVersion"),
                    "changes": self._diff_nodes(old_node, new_node)
                })

        return {
            "workflow_name": workflow.get("name"),
            "compatibility_status": compatibility.status.value,
            "issues_found": len(compatibility.issues),
            "nodes_to_update": len(changes),
            "changes": changes,
            "can_auto_migrate": all(issue.migration_available for issue in compatibility.issues)
        }

    def _diff_nodes(self, old_node: Dict, new_node: Dict) -> List[str]:
        """
        Calculate differences between old and new node

        Args:
            old_node: Original node
            new_node: Updated node

        Returns:
            List of change descriptions
        """
        changes = []

        # Check version change
        if old_node.get("typeVersion") != new_node.get("typeVersion"):
            changes.append(
                f"Version: {old_node.get('typeVersion')} → {new_node.get('typeVersion')}"
            )

        # Check parameter changes
        old_params = old_node.get("parameters", {})
        new_params = new_node.get("parameters", {})

        # Parameters removed
        for key in old_params:
            if key not in new_params:
                changes.append(f"Removed parameter: {key}")

        # Parameters added
        for key in new_params:
            if key not in old_params:
                changes.append(f"Added parameter: {key}")

        # Parameters modified
        for key in set(old_params.keys()) & set(new_params.keys()):
            if old_params[key] != new_params[key]:
                changes.append(f"Modified parameter: {key}")

        return changes

    def can_safely_migrate(self, workflow: Dict) -> bool:
        """
        Check if workflow can be safely migrated without manual intervention

        Args:
            workflow: Workflow JSON

        Returns:
            True if safe to auto-migrate
        """
        compatibility = self.version_checker.check_workflow_compatibility(workflow)

        # No issues = already compatible
        if not compatibility.has_issues:
            return True

        # Critical issues need manual review
        if compatibility.has_breaking_changes:
            return False

        # Check if all issues have migrations available
        return all(issue.migration_available for issue in compatibility.issues)

    def get_migration_summary(self, workflow: Dict) -> str:
        """
        Get human-readable migration summary

        Args:
            workflow: Workflow JSON

        Returns:
            Formatted summary text
        """
        preview = self.get_update_preview(workflow)

        summary = f"# Migration Summary for '{preview['workflow_name']}'\n\n"
        summary += f"**Status:** {preview['compatibility_status']}\n"
        summary += f"**Issues Found:** {preview['issues_found']}\n"
        summary += f"**Nodes to Update:** {preview['nodes_to_update']}\n"
        summary += f"**Auto-Migration Available:** {'✅ Yes' if preview['can_auto_migrate'] else '❌ No'}\n\n"

        if preview['nodes_to_update'] > 0:
            summary += "## Changes Preview\n\n"
            for change in preview['changes']:
                summary += f"### {change['node_name']} ({change['node_type']})\n"
                summary += f"- Version: {change['old_version']} → {change['new_version']}\n"
                summary += "- Changes:\n"
                for detail in change['changes']:
                    summary += f"  - {detail}\n"
                summary += "\n"

        return summary

    def batch_update_workflows(
        self,
        workflows: List[Dict],
        auto_migrate: bool = True
    ) -> List[Tuple[Dict, CompatibilityResult, List[Dict]]]:
        """
        Update multiple workflows at once

        Args:
            workflows: List of workflow JSONs
            auto_migrate: If True, automatically apply migrations

        Returns:
            List of (updated_workflow, compatibility_result, migration_log) tuples
        """
        results = []

        for workflow in workflows:
            try:
                result = self.check_and_update(workflow, auto_migrate=auto_migrate)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to update workflow {workflow.get('name')}: {e}")
                # Add failed result
                compatibility = self.version_checker.check_workflow_compatibility(workflow)
                results.append((workflow, compatibility, []))

        return results

    def validate_migration(
        self,
        original_workflow: Dict,
        migrated_workflow: Dict
    ) -> Dict:
        """
        Validate that migration preserved workflow functionality

        Args:
            original_workflow: Original workflow
            migrated_workflow: Migrated workflow

        Returns:
            Validation report
        """
        issues = []

        # Check node count
        orig_nodes = original_workflow.get("nodes", [])
        migr_nodes = migrated_workflow.get("nodes", [])

        if len(orig_nodes) != len(migr_nodes):
            issues.append({
                "severity": "critical",
                "message": f"Node count changed: {len(orig_nodes)} → {len(migr_nodes)}"
            })

        # Check connections preserved
        orig_conn = original_workflow.get("connections", {})
        migr_conn = migrated_workflow.get("connections", {})

        if orig_conn != migr_conn:
            issues.append({
                "severity": "high",
                "message": "Workflow connections may have changed"
            })

        # Check node names preserved
        orig_names = {n.get("name") for n in orig_nodes}
        migr_names = {n.get("name") for n in migr_nodes}

        if orig_names != migr_names:
            issues.append({
                "severity": "medium",
                "message": "Node names may have changed"
            })

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "nodes_migrated": len(migr_nodes),
            "connections_preserved": orig_conn == migr_conn
        }
