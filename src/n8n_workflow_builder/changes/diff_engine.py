"""
Workflow Diff Engine - Compare old vs new workflows

Detects:
- Added nodes
- Removed nodes
- Modified nodes (parameters, position, etc.)
- Connection changes
- Settings changes
- Breaking changes
"""

from typing import Dict, List, Set, Tuple, Optional


class WorkflowDiffEngine:
    """Compares two workflow versions and generates a detailed diff"""

    @staticmethod
    def compare_workflows(old_workflow: Dict, new_workflow: Dict) -> Dict:
        """
        Compare two workflows and generate comprehensive diff

        Returns:
            {
                "nodes": {
                    "added": List[Dict],
                    "removed": List[Dict],
                    "modified": List[Dict]
                },
                "connections": {
                    "added": List[Dict],
                    "removed": List[Dict],
                    "modified": List[Dict]
                },
                "settings": {
                    "modified": List[Dict]
                },
                "breaking_changes": List[Dict],
                "summary": Dict
            }
        """
        old_nodes = old_workflow.get("nodes", [])
        new_nodes = new_workflow.get("nodes", [])
        old_connections = old_workflow.get("connections", {})
        new_connections = new_workflow.get("connections", {})
        old_settings = old_workflow.get("settings", {})
        new_settings = new_workflow.get("settings", {})

        # Compare nodes
        node_diff = WorkflowDiffEngine._compare_nodes(old_nodes, new_nodes)

        # Compare connections
        connection_diff = WorkflowDiffEngine._compare_connections(
            old_connections, new_connections, old_nodes, new_nodes
        )

        # Compare settings
        settings_diff = WorkflowDiffEngine._compare_settings(old_settings, new_settings)

        # Detect breaking changes
        breaking_changes = WorkflowDiffEngine._detect_breaking_changes(
            node_diff, connection_diff, settings_diff, old_workflow, new_workflow
        )

        # Generate summary
        summary = WorkflowDiffEngine._generate_summary(
            node_diff, connection_diff, settings_diff, breaking_changes
        )

        return {
            "nodes": node_diff,
            "connections": connection_diff,
            "settings": settings_diff,
            "breaking_changes": breaking_changes,
            "summary": summary,
        }

    @staticmethod
    def _compare_nodes(old_nodes: List[Dict], new_nodes: List[Dict]) -> Dict:
        """Compare node lists"""
        # Build maps by node name (assuming names are unique identifiers)
        old_map = {node["name"]: node for node in old_nodes}
        new_map = {node["name"]: node for node in new_nodes}

        old_names = set(old_map.keys())
        new_names = set(new_map.keys())

        # Find added, removed, modified
        added_names = new_names - old_names
        removed_names = old_names - new_names
        common_names = old_names & new_names

        added = [new_map[name] for name in added_names]
        removed = [old_map[name] for name in removed_names]

        # Check for modifications in common nodes
        modified = []
        for name in common_names:
            old_node = old_map[name]
            new_node = new_map[name]

            changes = WorkflowDiffEngine._compare_node_details(old_node, new_node)
            if changes:
                modified.append({
                    "node_name": name,
                    "changes": changes,
                    "old": old_node,
                    "new": new_node,
                })

        return {
            "added": added,
            "removed": removed,
            "modified": modified,
        }

    @staticmethod
    def _compare_node_details(old_node: Dict, new_node: Dict) -> List[Dict]:
        """Compare details of a single node"""
        changes = []

        # Check type change
        if old_node.get("type") != new_node.get("type"):
            changes.append({
                "field": "type",
                "old_value": old_node.get("type"),
                "new_value": new_node.get("type"),
                "severity": "critical",
            })

        # Check position change
        old_pos = old_node.get("position", [0, 0])
        new_pos = new_node.get("position", [0, 0])
        if old_pos != new_pos:
            changes.append({
                "field": "position",
                "old_value": old_pos,
                "new_value": new_pos,
                "severity": "low",
            })

        # Check parameters
        old_params = old_node.get("parameters", {})
        new_params = new_node.get("parameters", {})

        param_changes = WorkflowDiffEngine._compare_dicts(old_params, new_params, "parameters")
        changes.extend(param_changes)

        # Check credentials
        old_creds = old_node.get("credentials", {})
        new_creds = new_node.get("credentials", {})

        if old_creds != new_creds:
            changes.append({
                "field": "credentials",
                "old_value": old_creds,
                "new_value": new_creds,
                "severity": "high",
            })

        return changes

    @staticmethod
    def _compare_dicts(old_dict: Dict, new_dict: Dict, prefix: str) -> List[Dict]:
        """Compare two dictionaries recursively"""
        changes = []

        all_keys = set(old_dict.keys()) | set(new_dict.keys())

        for key in all_keys:
            old_val = old_dict.get(key)
            new_val = new_dict.get(key)

            if old_val != new_val:
                # Determine severity based on key
                severity = WorkflowDiffEngine._determine_param_severity(key, old_val, new_val)

                changes.append({
                    "field": f"{prefix}.{key}",
                    "old_value": old_val,
                    "new_value": new_val,
                    "severity": severity,
                })

        return changes

    @staticmethod
    def _determine_param_severity(key: str, old_val, new_val) -> str:
        """Determine severity of parameter change"""
        # Critical parameters
        critical_params = ["url", "method", "authentication", "operation", "database", "table"]
        if key.lower() in critical_params:
            return "high"

        # Important parameters
        important_params = ["query", "body", "headers", "timeout", "retry"]
        if key.lower() in important_params:
            return "medium"

        # If value was removed
        if old_val is not None and new_val is None:
            return "medium"

        # If value was added
        if old_val is None and new_val is not None:
            return "low"

        # Default
        return "low"

    @staticmethod
    def _compare_connections(
        old_connections: Dict,
        new_connections: Dict,
        old_nodes: List[Dict],
        new_nodes: List[Dict]
    ) -> Dict:
        """Compare workflow connections"""
        old_edges = WorkflowDiffEngine._flatten_connections(old_connections)
        new_edges = WorkflowDiffEngine._flatten_connections(new_connections)

        # Convert to sets for comparison
        old_edge_set = set(old_edges)
        new_edge_set = set(new_edges)

        added_edges = new_edge_set - old_edge_set
        removed_edges = old_edge_set - new_edge_set

        # Format as dicts
        added = [{"from": e[0], "to": e[1], "type": e[2]} for e in added_edges]
        removed = [{"from": e[0], "to": e[1], "type": e[2]} for e in removed_edges]

        return {
            "added": added,
            "removed": removed,
            "modified": [],  # Connections are either added or removed, not modified
        }

    @staticmethod
    def _flatten_connections(connections: Dict) -> List[Tuple[str, str, str]]:
        """Flatten connection dict to list of (source, target, type) tuples"""
        edges = []

        for source_node, outputs in connections.items():
            for output_type, output_connections in outputs.items():
                # Handle nested list structure
                for connection_group in output_connections:
                    if isinstance(connection_group, list):
                        for conn in connection_group:
                            target_node = conn.get("node", "")
                            edges.append((source_node, target_node, output_type))
                    else:
                        # Fallback for old format
                        conn = connection_group
                        target_node = conn.get("node", "")
                        edges.append((source_node, target_node, output_type))

        return edges

    @staticmethod
    def _compare_settings(old_settings: Dict, new_settings: Dict) -> Dict:
        """Compare workflow settings"""
        modified = []

        all_keys = set(old_settings.keys()) | set(new_settings.keys())

        for key in all_keys:
            old_val = old_settings.get(key)
            new_val = new_settings.get(key)

            if old_val != new_val:
                severity = "high" if key in ["errorWorkflow", "timezone"] else "medium"

                modified.append({
                    "setting": key,
                    "old_value": old_val,
                    "new_value": new_val,
                    "severity": severity,
                })

        return {"modified": modified}

    @staticmethod
    def _detect_breaking_changes(
        node_diff: Dict,
        connection_diff: Dict,
        settings_diff: Dict,
        old_workflow: Dict,
        new_workflow: Dict
    ) -> List[Dict]:
        """Detect breaking changes that could break production"""
        breaking_changes = []

        # Check for removed trigger nodes
        removed_nodes = node_diff["removed"]
        for node in removed_nodes:
            if "trigger" in node.get("type", "").lower():
                breaking_changes.append({
                    "type": "trigger_removed",
                    "severity": "critical",
                    "description": f"Trigger node '{node['name']}' removed",
                    "impact": "Workflow will no longer be triggered automatically",
                    "recommendation": "Ensure alternative trigger exists or workflow is manually triggered",
                })

        # Check for trigger type changes
        for mod in node_diff["modified"]:
            for change in mod["changes"]:
                if change["field"] == "type" and "trigger" in str(change["old_value"]).lower():
                    breaking_changes.append({
                        "type": "trigger_type_changed",
                        "severity": "critical",
                        "node": mod["node_name"],
                        "description": f"Trigger type changed from {change['old_value']} to {change['new_value']}",
                        "impact": "Workflow trigger behavior will change completely",
                        "recommendation": "Update all systems that depend on this trigger",
                    })

        # Check for removed connections to critical nodes
        removed_connections = connection_diff["removed"]
        if removed_connections:
            breaking_changes.append({
                "type": "connections_removed",
                "severity": "high",
                "count": len(removed_connections),
                "description": f"{len(removed_connections)} connection(s) removed",
                "impact": "Data flow will be interrupted",
                "recommendation": "Verify that removed connections are intentional",
            })

        # Check for removed output nodes
        for node in removed_nodes:
            node_type = node.get("type", "").lower()
            if any(output_type in node_type for output_type in ["email", "slack", "http", "database"]):
                breaking_changes.append({
                    "type": "output_node_removed",
                    "severity": "high",
                    "node": node["name"],
                    "description": f"Output node '{node['name']}' removed",
                    "impact": "Data will no longer be sent to this destination",
                    "recommendation": "Ensure data is sent to alternative destination",
                })

        return breaking_changes

    @staticmethod
    def _generate_summary(
        node_diff: Dict,
        connection_diff: Dict,
        settings_diff: Dict,
        breaking_changes: List[Dict]
    ) -> Dict:
        """Generate change summary"""
        total_changes = (
            len(node_diff["added"]) +
            len(node_diff["removed"]) +
            len(node_diff["modified"]) +
            len(connection_diff["added"]) +
            len(connection_diff["removed"]) +
            len(settings_diff["modified"])
        )

        # Determine risk level
        if breaking_changes:
            risk_level = "critical" if any(bc["severity"] == "critical" for bc in breaking_changes) else "high"
        elif node_diff["removed"] or connection_diff["removed"]:
            risk_level = "medium"
        elif node_diff["added"] or connection_diff["added"]:
            risk_level = "low"
        else:
            risk_level = "minimal"

        return {
            "total_changes": total_changes,
            "nodes_added": len(node_diff["added"]),
            "nodes_removed": len(node_diff["removed"]),
            "nodes_modified": len(node_diff["modified"]),
            "connections_added": len(connection_diff["added"]),
            "connections_removed": len(connection_diff["removed"]),
            "settings_modified": len(settings_diff["modified"]),
            "breaking_changes_count": len(breaking_changes),
            "risk_level": risk_level,
            "has_breaking_changes": len(breaking_changes) > 0,
        }
