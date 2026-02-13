#!/usr/bin/env python3
"""
Change Simulator
Simulates workflow changes with Terraform-style diff output
"""
from typing import Dict, List, Any, Tuple
import json


class ChangeSimulator:
    """Simulates workflow changes and generates Terraform-style diffs"""
    
    def __init__(self, n8n_client):
        """Initialize with n8n client
        
        Args:
            n8n_client: N8nClient instance for fetching workflows
        """
        self.client = n8n_client
    
    async def simulate(self, workflow_id: str, new_workflow: Dict) -> Dict[str, Any]:
        """Simulate workflow changes
        
        Args:
            workflow_id: ID of existing workflow
            new_workflow: New workflow configuration to simulate
            
        Returns:
            Dictionary with simulation results including:
            - additions: List of nodes/connections being added
            - deletions: List of nodes/connections being removed
            - modifications: List of nodes/connections being modified
            - breaking_changes: List of detected breaking changes
            - summary: Human-readable summary
        """
        # Fetch current workflow
        current_workflow = await self.client.get_workflow(workflow_id)
        
        # Analyze differences
        additions, deletions, modifications = self._diff_workflows(current_workflow, new_workflow)
        
        # Detect breaking changes
        breaking_changes = self._detect_breaking_changes(current_workflow, new_workflow, 
                                                         additions, deletions, modifications)
        
        # Generate summary
        summary = self._generate_summary(additions, deletions, modifications, breaking_changes)
        
        return {
            'current_workflow_name': current_workflow.get('name', 'Unnamed'),
            'new_workflow_name': new_workflow.get('name', 'Unnamed'),
            'additions': additions,
            'deletions': deletions,
            'modifications': modifications,
            'breaking_changes': breaking_changes,
            'summary': summary,
            'total_changes': len(additions) + len(deletions) + len(modifications)
        }
    
    def _diff_workflows(self, current: Dict, new: Dict) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """Generate diff between two workflows
        
        Returns:
            (additions, deletions, modifications) tuple
        """
        additions = []
        deletions = []
        modifications = []
        
        # 1. Diff nodes
        current_nodes = {n['name']: n for n in current.get('nodes', [])}
        new_nodes = {n['name']: n for n in new.get('nodes', [])}
        
        # Added nodes
        for name, node in new_nodes.items():
            if name not in current_nodes:
                additions.append({
                    'type': 'node',
                    'action': 'add',
                    'name': name,
                    'node_type': node.get('type'),
                    'details': f"+ Node '{name}' ({node.get('type')})"
                })
        
        # Deleted nodes
        for name, node in current_nodes.items():
            if name not in new_nodes:
                deletions.append({
                    'type': 'node',
                    'action': 'delete',
                    'name': name,
                    'node_type': node.get('type'),
                    'details': f"- Node '{name}' ({node.get('type')})"
                })
        
        # Modified nodes
        for name in current_nodes.keys() & new_nodes.keys():
            changes = self._diff_nodes(current_nodes[name], new_nodes[name])
            if changes:
                modifications.append({
                    'type': 'node',
                    'action': 'modify',
                    'name': name,
                    'node_type': current_nodes[name].get('type'),
                    'changes': changes,
                    'details': f"~ Node '{name}': {', '.join(changes)}"
                })
        
        # 2. Diff connections
        current_connections = current.get('connections', {})
        new_connections = new.get('connections', {})
        
        conn_additions, conn_deletions, conn_modifications = self._diff_connections(
            current_connections, new_connections
        )
        
        additions.extend(conn_additions)
        deletions.extend(conn_deletions)
        modifications.extend(conn_modifications)
        
        # 3. Diff workflow settings
        if current.get('settings') != new.get('settings'):
            setting_changes = self._diff_settings(
                current.get('settings', {}),
                new.get('settings', {})
            )
            if setting_changes:
                modifications.append({
                    'type': 'settings',
                    'action': 'modify',
                    'changes': setting_changes,
                    'details': f"~ Settings: {', '.join(setting_changes)}"
                })
        
        return additions, deletions, modifications
    
    def _diff_nodes(self, current_node: Dict, new_node: Dict) -> List[str]:
        """Diff two nodes and return list of changes
        
        Returns:
            List of change descriptions
        """
        changes = []
        
        # Check type change
        if current_node.get('type') != new_node.get('type'):
            changes.append(f"type changed from '{current_node.get('type')}' to '{new_node.get('type')}'")
        
        # Check disabled status
        if current_node.get('disabled') != new_node.get('disabled'):
            status = 'disabled' if new_node.get('disabled') else 'enabled'
            changes.append(f"node {status}")
        
        # Check parameter changes (shallow comparison)
        current_params = current_node.get('parameters', {})
        new_params = new_node.get('parameters', {})
        
        if current_params != new_params:
            # Find changed keys
            all_keys = set(current_params.keys()) | set(new_params.keys())
            param_changes = []
            
            for key in all_keys:
                if key not in current_params:
                    param_changes.append(f"added {key}")
                elif key not in new_params:
                    param_changes.append(f"removed {key}")
                elif current_params[key] != new_params[key]:
                    param_changes.append(f"changed {key}")
            
            if param_changes:
                changes.append(f"parameters: {', '.join(param_changes[:3])}")
                if len(param_changes) > 3:
                    changes.append(f"... and {len(param_changes) - 3} more parameter changes")
        
        return changes
    
    def _diff_connections(self, current: Dict, new: Dict) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """Diff workflow connections
        
        Returns:
            (additions, deletions, modifications) tuple
        """
        additions = []
        deletions = []
        modifications = []
        
        # Convert connections to comparable format
        current_flat = self._flatten_connections(current)
        new_flat = self._flatten_connections(new)
        
        # Added connections
        for conn_str in new_flat - current_flat:
            additions.append({
                'type': 'connection',
                'action': 'add',
                'details': f"+ Connection: {conn_str}"
            })
        
        # Deleted connections
        for conn_str in current_flat - new_flat:
            deletions.append({
                'type': 'connection',
                'action': 'delete',
                'details': f"- Connection: {conn_str}"
            })
        
        return additions, deletions, modifications
    
    def _flatten_connections(self, connections: Dict) -> set:
        """Flatten connections dict to set of strings for comparison"""
        flat = set()
        
        for source_node, outputs in connections.items():
            for output_type, output_list in outputs.items():
                for idx, conn_group in enumerate(output_list):
                    if isinstance(conn_group, list):
                        for conn in conn_group:
                            target = conn.get('node', 'unknown')
                            target_input = conn.get('type', 'main')
                            target_idx = conn.get('index', 0)
                            flat.add(f"{source_node}[{output_type}:{idx}] → {target}[{target_input}:{target_idx}]")
        
        return flat
    
    def _diff_settings(self, current: Dict, new: Dict) -> List[str]:
        """Diff workflow settings
        
        Returns:
            List of setting changes
        """
        changes = []
        
        all_keys = set(current.keys()) | set(new.keys())
        
        for key in all_keys:
            if key not in current:
                changes.append(f"added {key}={new[key]}")
            elif key not in new:
                changes.append(f"removed {key}")
            elif current[key] != new[key]:
                changes.append(f"{key}: {current[key]} → {new[key]}")
        
        return changes
    
    def _detect_breaking_changes(self, current: Dict, new: Dict, 
                                 additions: List, deletions: List, modifications: List) -> List[Dict]:
        """Detect breaking changes
        
        Returns:
            List of breaking change descriptions
        """
        breaking_changes = []
        
        # 1. Deleted nodes that have outgoing connections
        current_connections = current.get('connections', {})
        for deletion in deletions:
            if deletion['type'] == 'node':
                node_name = deletion['name']
                if node_name in current_connections:
                    breaking_changes.append({
                        'severity': 'high',
                        'type': 'deleted_connected_node',
                        'description': f"Node '{node_name}' has connections and is being deleted",
                        'impact': 'Workflows depending on this node will fail'
                    })
        
        # 2. Type changes (node type switched)
        for modification in modifications:
            if modification['type'] == 'node':
                for change in modification.get('changes', []):
                    if 'type changed' in change:
                        breaking_changes.append({
                            'severity': 'high',
                            'type': 'node_type_change',
                            'description': f"Node '{modification['name']}': {change}",
                            'impact': 'Node behavior will change completely'
                        })
        
        # 3. Deleted connections
        for deletion in deletions:
            if deletion['type'] == 'connection':
                breaking_changes.append({
                    'severity': 'medium',
                    'type': 'deleted_connection',
                    'description': deletion['details'],
                    'impact': 'Data flow will be interrupted'
                })
        
        # 4. Workflow activation status change
        if current.get('active') != new.get('active'):
            if not new.get('active'):
                breaking_changes.append({
                    'severity': 'medium',
                    'type': 'workflow_deactivation',
                    'description': 'Workflow will be deactivated',
                    'impact': 'Triggers will stop firing'
                })
        
        return breaking_changes
    
    def _generate_summary(self, additions: List, deletions: List, 
                         modifications: List, breaking_changes: List) -> str:
        """Generate Terraform-style summary
        
        Returns:
            Formatted summary string
        """
        summary = "# Workflow Change Simulation\n\n"
        
        # Stats
        total = len(additions) + len(deletions) + len(modifications)
        
        summary += f"**Plan:** {len(additions)} to add, {len(modifications)} to change, {len(deletions)} to destroy\n\n"
        
        # Breaking changes warning
        if breaking_changes:
            summary += f"⚠️  **{len(breaking_changes)} Breaking Changes Detected**\n\n"
            for bc in breaking_changes:
                summary += f"- **[{bc['severity'].upper()}]** {bc['description']}\n"
                summary += f"  Impact: {bc['impact']}\n"
            summary += "\n"
        
        # Additions
        if additions:
            summary += "## ➕ Additions\n\n"
            for add in additions:
                summary += f"  {add['details']}\n"
            summary += "\n"
        
        # Deletions
        if deletions:
            summary += "## ➖ Deletions\n\n"
            for delete in deletions:
                summary += f"  {delete['details']}\n"
            summary += "\n"
        
        # Modifications
        if modifications:
            summary += "## ~ Modifications\n\n"
            for mod in modifications:
                summary += f"  {mod['details']}\n"
            summary += "\n"
        
        # No changes
        if total == 0:
            summary += "✅ **No changes detected** - workflows are identical\n"
        
        return summary
    
    def format_terraform_style(self, simulation_result: Dict) -> str:
        """Format simulation result as Terraform-style output
        
        Args:
            simulation_result: Result from simulate()
            
        Returns:
            Formatted string
        """
        return simulation_result['summary']
