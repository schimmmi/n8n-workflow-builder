"""
Migration Engine

Core engine for applying migrations to workflows based on rules.
"""
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
import copy
import logging

logger = logging.getLogger("n8n-workflow-builder")


@dataclass
class MigrationRule:
    """
    Defines a migration rule for transforming workflows
    """
    rule_id: str
    name: str
    description: str
    node_type: str
    from_version: int
    to_version: int
    transform: Callable[[Dict], Dict]  # Function to transform node
    severity: str = "medium"  # "low", "medium", "high", "critical"

    def apply(self, node: Dict) -> Dict:
        """Apply transformation to node"""
        try:
            return self.transform(copy.deepcopy(node))
        except Exception as e:
            logger.error(f"Failed to apply migration rule {self.rule_id}: {e}")
            return node


class MigrationEngine:
    """
    Engine for applying migrations to workflows
    """

    def __init__(self, rules: Optional[List[MigrationRule]] = None):
        """
        Initialize migration engine

        Args:
            rules: List of migration rules to use
        """
        self.rules = rules or []
        self._rules_by_node_type = self._index_rules()

    def _index_rules(self) -> Dict[str, List[MigrationRule]]:
        """Index rules by node type for faster lookup"""
        indexed = {}
        for rule in self.rules:
            if rule.node_type not in indexed:
                indexed[rule.node_type] = []
            indexed[rule.node_type].append(rule)
        return indexed

    def add_rule(self, rule: MigrationRule):
        """Add a migration rule"""
        self.rules.append(rule)
        if rule.node_type not in self._rules_by_node_type:
            self._rules_by_node_type[rule.node_type] = []
        self._rules_by_node_type[rule.node_type].append(rule)

    def migrate_workflow(
        self,
        workflow: Dict,
        target_version: Optional[int] = None,
        dry_run: bool = False
    ) -> tuple[Dict, List[Dict]]:
        """
        Migrate entire workflow to target version

        Args:
            workflow: Workflow JSON
            target_version: Target n8n version (optional)
            dry_run: If True, don't modify original workflow

        Returns:
            Tuple of (migrated_workflow, migration_log)
        """
        if dry_run:
            workflow = copy.deepcopy(workflow)

        migrated_nodes = []
        migration_log = []

        for node in workflow.get("nodes", []):
            # Skip None or invalid nodes
            if node is None or not isinstance(node, dict):
                logger.warning(f"Skipping invalid node: {node}")
                continue

            migrated_node, log = self.migrate_node(node, target_version)
            migrated_nodes.append(migrated_node)
            if log:
                migration_log.extend(log)

        workflow["nodes"] = migrated_nodes

        # Add migration metadata
        if not dry_run and migration_log:
            if "meta" not in workflow:
                workflow["meta"] = {}
            workflow["meta"]["lastMigration"] = {
                "timestamp": self._get_timestamp(),
                "appliedRules": [log["rule_id"] for log in migration_log],
                "changes": len(migration_log)
            }

        return workflow, migration_log

    def migrate_node(
        self,
        node: Dict,
        target_version: Optional[int] = None
    ) -> tuple[Dict, List[Dict]]:
        """
        Migrate a single node

        Args:
            node: Node object
            target_version: Target version

        Returns:
            Tuple of (migrated_node, migration_log)
        """
        # Defensive check
        if not node or not isinstance(node, dict):
            logger.warning(f"Invalid node passed to migrate_node: {node}")
            return node, []

        node_type = node.get("type", "")
        current_version = node.get("typeVersion", 1)

        # No rules for this node type
        if node_type not in self._rules_by_node_type:
            return node, []

        applicable_rules = self._find_applicable_rules(
            node_type,
            current_version,
            target_version
        )

        if not applicable_rules:
            return node, []

        # Apply rules in order
        migrated_node = copy.deepcopy(node)
        migration_log = []

        for rule in applicable_rules:
            logger.info(f"Applying migration rule: {rule.rule_id} to node {node.get('name')}")
            migrated_node = rule.apply(migrated_node)

            migration_log.append({
                "rule_id": rule.rule_id,
                "rule_name": rule.name,
                "node_name": node.get("name"),
                "from_version": rule.from_version,
                "to_version": rule.to_version,
            })

            # Update node version
            migrated_node["typeVersion"] = rule.to_version

        return migrated_node, migration_log

    def _find_applicable_rules(
        self,
        node_type: str,
        current_version: int,
        target_version: Optional[int]
    ) -> List[MigrationRule]:
        """
        Find rules that should be applied for this migration
        Builds a chain of rules to go from current_version to target_version

        Args:
            node_type: Node type
            current_version: Current node version
            target_version: Target version (or latest if None)

        Returns:
            List of applicable rules in order
        """
        rules = self._rules_by_node_type.get(node_type, [])

        if not rules:
            return []

        # If no target version specified, migrate to latest
        if target_version is None:
            target_version = max((r.to_version for r in rules), default=current_version)

        # Already at or past target version
        if current_version >= target_version:
            return []

        # Build migration chain using BFS
        path = []
        current = current_version

        # Try to find a path from current to target
        while current < target_version:
            # Find the next rule that upgrades from current version
            next_rule = None

            for rule in rules:
                if rule.from_version == current and rule.to_version <= target_version:
                    # Found a valid next step
                    if next_rule is None or rule.to_version < next_rule.to_version:
                        # Prefer smaller steps for more granular control
                        next_rule = rule

            if next_rule is None:
                # No path found - return what we have so far
                break

            path.append(next_rule)
            current = next_rule.to_version

        return path

    def get_migration_path(
        self,
        node_type: str,
        from_version: int,
        to_version: int
    ) -> List[MigrationRule]:
        """
        Get the migration path from one version to another

        Args:
            node_type: Node type
            from_version: Starting version
            to_version: Target version

        Returns:
            Ordered list of rules to apply
        """
        if node_type not in self._rules_by_node_type:
            return []

        # Build path using BFS
        path = []
        current = from_version

        while current < to_version:
            # Find rule that upgrades from current version
            next_rule = None
            for rule in self._rules_by_node_type[node_type]:
                if rule.from_version == current and rule.to_version <= to_version:
                    if next_rule is None or rule.to_version > next_rule.to_version:
                        next_rule = rule

            if next_rule is None:
                # No path found
                logger.warning(f"No migration path from v{current} to v{to_version} for {node_type}")
                break

            path.append(next_rule)
            current = next_rule.to_version

        return path

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

    def can_migrate(self, node_type: str, from_version: int, to_version: int) -> bool:
        """
        Check if migration is possible

        Args:
            node_type: Node type
            from_version: Starting version
            to_version: Target version

        Returns:
            True if migration path exists
        """
        path = self.get_migration_path(node_type, from_version, to_version)
        return len(path) > 0 and path[-1].to_version == to_version
