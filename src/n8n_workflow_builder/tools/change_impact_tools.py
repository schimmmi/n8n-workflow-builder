#!/usr/bin/env python3
"""
Change Impact & Node Discovery Tool Handlers
Handles workflow comparison, change impact analysis, and node discovery
"""
from typing import Any, TYPE_CHECKING
import json

from mcp.types import TextContent

from .base import BaseTool, ToolError

if TYPE_CHECKING:
    from ..dependencies import Dependencies


class ChangeImpactTools(BaseTool):
    """Handler for change impact and node discovery tools"""
    
    async def handle(self, name: str, arguments: dict) -> list[TextContent]:
        """Route change impact tool calls to appropriate handler methods
        
        Args:
            name: Tool name
            arguments: Tool arguments
            
        Returns:
            List of TextContent responses
        """
        handlers = {
            "compare_workflows": self.compare_workflows,
            "analyze_change_impact": self.analyze_change_impact,
            "discover_nodes": self.discover_nodes,
            "get_node_schema": self.get_node_schema,
        }
        
        handler = handlers.get(name)
        if not handler:
            raise ToolError("UNKNOWN_TOOL", f"Tool '{name}' not found in change impact tools")
        
        return await handler(arguments)
    
    async def compare_workflows(self, arguments: dict) -> list[TextContent]:
        """Compare two workflows and show differences"""
        workflow_id_1 = arguments["workflow_id_1"]
        workflow_id_2 = arguments["workflow_id_2"]
        
        # Fetch both workflows
        workflow_1 = await self.deps.client.get_workflow(workflow_id_1)
        workflow_2 = await self.deps.client.get_workflow(workflow_id_2)
        
        # Import here to avoid circular dependencies
        from ..changes.diff_engine import WorkflowDiffEngine
        from ..changes.formatter import ChangeFormatter
        
        # Generate diff
        diff = WorkflowDiffEngine.compare_workflows(workflow_1, workflow_2)
        
        # Format comparison
        comparison = ChangeFormatter.format_comparison(workflow_1, workflow_2, diff)
        
        # Add detailed diff
        result = comparison + "\n\n"
        result += "=" * 80 + "\n"
        result += "DETAILED CHANGES\n"
        result += "=" * 80 + "\n\n"
        
        # Nodes
        if diff["nodes"]["added"]:
            result += f"**Added Nodes ({len(diff['nodes']['added'])}):**\n"
            for node in diff["nodes"]["added"][:10]:
                result += f"  + {node['name']} ({node.get('type', 'unknown')})\n"
            result += "\n"
        
        if diff["nodes"]["removed"]:
            result += f"**Removed Nodes ({len(diff['nodes']['removed'])}):**\n"
            for node in diff["nodes"]["removed"][:10]:
                result += f"  - {node['name']} ({node.get('type', 'unknown')})\n"
            result += "\n"
        
        if diff["nodes"]["modified"]:
            result += f"**Modified Nodes ({len(diff['nodes']['modified'])}):**\n"
            for mod in diff["nodes"]["modified"][:10]:
                result += f"  ~ {mod['node_name']}\n"
                for change in mod["changes"][:3]:
                    result += f"      {change['field']}: {change.get('old_value', 'N/A')} → {change.get('new_value', 'N/A')}\n"
            result += "\n"
        
        # Connections
        if diff["connections"]["added"]:
            result += f"**Added Connections ({len(diff['connections']['added'])}):**\n"
            for conn in diff["connections"]["added"][:10]:
                result += f"  + {conn['from']} → {conn['to']}\n"
            result += "\n"
        
        if diff["connections"]["removed"]:
            result += f"**Removed Connections ({len(diff['connections']['removed'])}):**\n"
            for conn in diff["connections"]["removed"][:10]:
                result += f"  - {conn['from']} → {conn['to']}\n"
            result += "\n"
        
        # Breaking changes
        if diff["breaking_changes"]:
            result += f"**⚠️ Breaking Changes ({len(diff['breaking_changes'])}):**\n"
            for bc in diff["breaking_changes"]:
                result += f"  - [{bc['severity'].upper()}] {bc['description']}\n"
        
        return [TextContent(type="text", text=result)]
    
    async def analyze_change_impact(self, arguments: dict) -> list[TextContent]:
        """Analyze impact of changes to a workflow"""
        workflow_id = arguments["workflow_id"]
        new_workflow = arguments["new_workflow"]
        include_downstream = arguments.get("include_downstream", True)
        
        # Fetch old workflow
        old_workflow = await self.deps.client.get_workflow(workflow_id)
        
        # Import here to avoid circular dependencies
        from ..changes.diff_engine import WorkflowDiffEngine
        from ..changes.impact_analyzer import ChangeImpactAnalyzer
        
        # Generate diff
        diff = WorkflowDiffEngine.compare_workflows(old_workflow, new_workflow)
        
        # Analyze impact
        all_workflows = []
        if include_downstream:
            all_workflows = await self.deps.client.list_workflows()
        
        impact = ChangeImpactAnalyzer.analyze_impact(
            diff, old_workflow, new_workflow, all_workflows
        )
        
        # Format result
        result = "# Change Impact Analysis\n\n"
        result += f"**Overall Risk Score**: {impact['overall_risk_score']}/10\n"
        result += f"**Risk Level**: {impact['risk_level'].upper()}\n\n"
        
        # Impact dimensions
        dimensions = [
            ("🔄 Data Flow Impact", "data_flow_impact"),
            ("⚡ Execution Impact", "execution_impact"),
            ("🔗 Dependency Impact", "dependency_impact"),
            ("🔔 Trigger Impact", "trigger_impact"),
            ("⚙️ Downstream Impact", "downstream_impact"),
        ]
        
        for dim_name, dim_key in dimensions:
            dim_impact = impact[dim_key]
            if dim_impact["impacts"]:
                result += f"## {dim_name}\n\n"
                result += f"**Summary**: {dim_impact['summary']}\n"
                result += f"**Breaking Changes**: {'Yes' if dim_impact['has_breaking_changes'] else 'No'}\n\n"
                
                for imp in dim_impact["impacts"][:5]:
                    severity = imp.get("severity", "unknown")
                    result += f"- **[{severity.upper()}]** {imp['description']}\n"
                    if imp.get("node"):
                        result += f"  - Node: `{imp['node']}`\n"
                    if imp.get("affected_paths"):
                        result += f"  - Affected: {len(imp['affected_paths'])} path(s)\n"
                result += "\n"
        
        # Recommendations
        if impact["recommendations"]:
            result += "## 💡 Recommendations\n\n"
            for rec in impact["recommendations"]:
                result += f"- {rec}\n"
        
        return [TextContent(type="text", text=result)]
    
    async def discover_nodes(self, arguments: dict) -> list[TextContent]:
        """Analyze workflows to discover node types"""
        import logging
        logger = logging.getLogger(__name__)
        
        # Access node discovery from deps
        node_discovery = self.deps.node_discovery
        
        # Analyze all workflows to discover node types
        workflows = await self.deps.client.list_workflows()
        
        # Get full workflow details for analysis
        full_workflows = []
        for workflow in workflows:
            workflow_id = workflow.get('id')
            if workflow_id:
                try:
                    full_workflow = await self.deps.client.get_workflow(workflow_id)
                    full_workflows.append(full_workflow)
                except Exception as e:
                    logger.warning(f"Could not load workflow {workflow_id}: {e}")
        
        # Analyze workflows and discover nodes
        summary = node_discovery.analyze_workflows(full_workflows)
        
        result = f"# 📦 Node Discovery Complete\n\n"
        result += f"**Analyzed:** {len(full_workflows)} workflows\n"
        result += f"**Discovered:** {summary['total_node_types']} unique node types\n"
        result += f"**Total Usage:** {summary['total_usage']} node instances\n\n"
        
        result += f"## 🔥 Most Popular Nodes\n\n"
        for node_type, count in summary['most_used'][:10]:
            result += f"- **{node_type}**: {count} uses\n"
        
        result += f"\n## 📋 All Discovered Node Types\n\n"
        for i, node_type in enumerate(sorted(summary['node_types']), 1):
            result += f"{i}. `{node_type}`\n"
        
        result += f"\n💡 **Next Steps:**\n"
        result += f"- Use `get_node_schema(node_type)` to see parameters for a specific node\n"
        result += f"- Use `search_nodes(keyword)` to find nodes by keyword\n"
        result += f"- Use `recommend_nodes_for_task(task)` to get recommendations\n"
        result += f"\n✅ Knowledge saved to: `{node_discovery.db_path}`\n"
        
        return [TextContent(type="text", text=result)]
    
    async def get_node_schema(self, arguments: dict) -> list[TextContent]:
        """Get schema information for a discovered node type"""
        node_type = arguments["node_type"]
        
        # Get discovered schema
        node_discovery = self.deps.node_discovery
        schema = node_discovery.get_node_schema(node_type)
        
        if not schema:
            return [TextContent(
                type="text",
                text=f"❌ Node type `{node_type}` not found in discovered nodes.\n\n"
                     f"💡 Run `discover_nodes` first to analyze workflows and learn about nodes."
            )]
        
        result = f"# 🔍 Node Schema: {schema.get('name', node_type)}\n\n"
        result += f"**Type:** `{node_type}`\n"
        result += f"**Version:** {schema.get('typeVersion', 1)}\n"
        result += f"**Usage Count:** {schema['usage_count']} times in workflows\n\n"
        
        # Parameters
        seen_params = schema.get('seen_parameters', [])
        param_types = schema.get('parameter_types', {})
        
        if seen_params:
            result += f"## Parameters ({len(seen_params)})\n\n"
            result += f"Discovered from real workflow usage:\n\n"
            
            for param in sorted(seen_params):
                param_type = param_types.get(param, 'unknown')
                result += f"- **{param}** (type: `{param_type}`)\n"
            
            result += "\n"
        else:
            result += "## Parameters\n\nNo parameters discovered yet.\n\n"
        
        # Credentials
        credentials = schema.get('credentials')
        if credentials:
            result += "## Credentials\n\n"
            if isinstance(credentials, list):
                for cred in credentials:
                    result += f"- {cred}\n"
            else:
                result += f"- {credentials}\n"
            result += "\n"
        
        # Example usage
        example_usage = schema.get('example_usage', {})
        if example_usage:
            result += "## Example Usage\n\n"
            result += f"```json\n{json.dumps(example_usage, indent=2)}\n```\n"
        
        return [TextContent(type="text", text=result)]
