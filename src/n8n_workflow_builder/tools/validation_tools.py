#!/usr/bin/env python3
"""
Workflow Validation Tools
Provides validation for workflow structure, connections, and best practices
"""
from mcp.types import TextContent
from .base import BaseTool, ToolError


class ValidationTools(BaseTool):
    """Handler for workflow validation operations"""
    
    async def handle(self, name: str, arguments: dict) -> list[TextContent]:
        """Route validation tool calls to appropriate handler methods
        
        Args:
            name: Tool name
            arguments: Tool arguments
            
        Returns:
            List of TextContent responses
        """
        handlers = {
            "validate_workflow": self.validate_workflow,
            "validate_workflow_json": self.validate_workflow_json,
        }
        
        handler = handlers.get(name)
        if not handler:
            raise ToolError("UNKNOWN_TOOL", f"Tool '{name}' not found in validation tools")
        
        return await handler(arguments)
    
    async def validate_workflow(self, arguments: dict) -> list[TextContent]:
        """Validate an existing workflow against schema and best practices
        
        Args:
            arguments: {"workflow_id": str}
            
        Returns:
            Validation report with errors and warnings
        """
        workflow_id = arguments["workflow_id"]
        
        # Fetch workflow
        workflow = await self.deps.client.get_workflow(workflow_id)
        
        # Run validation
        errors = []
        warnings = []
        info = []
        
        # 1. Schema Validation
        if not workflow.get("nodes"):
            errors.append("Workflow has no nodes")
        
        if not workflow.get("name"):
            warnings.append("Workflow has no name")
        
        # 2. Node Validation
        nodes = workflow.get("nodes", [])
        node_names = set()
        
        for i, node in enumerate(nodes):
            # Check required fields
            if not node.get("name"):
                errors.append(f"Node at index {i} is missing a name")
            else:
                # Check for duplicate names
                if node["name"] in node_names:
                    errors.append(f"Duplicate node name: '{node['name']}'")
                node_names.add(node["name"])
            
            if not node.get("type"):
                errors.append(f"Node '{node.get('name', f'at index {i}')}' is missing a type")
            
            if not node.get("position"):
                warnings.append(f"Node '{node.get('name', f'at index {i}')}' is missing position")
            
            # Check for disabled nodes
            if node.get("disabled"):
                info.append(f"Node '{node['name']}' is disabled")
        
        # 3. Connection Validation
        connections = workflow.get("connections", {})
        
        for source_node, outputs in connections.items():
            # Check if source node exists
            if source_node not in node_names:
                errors.append(f"Connection references non-existent source node: '{source_node}'")
                continue
            
            # Validate connections structure
            if not isinstance(outputs, dict):
                errors.append(f"Invalid connections structure for node '{source_node}'")
                continue
            
            for output_type, output_list in outputs.items():
                if not isinstance(output_list, list):
                    errors.append(f"Invalid output connections for '{source_node}.{output_type}'")
                    continue
                
                for conn_group in output_list:
                    if not isinstance(conn_group, list):
                        continue
                    
                    for conn in conn_group:
                        target_node = conn.get("node")
                        if target_node and target_node not in node_names:
                            errors.append(f"Connection from '{source_node}' references non-existent target node: '{target_node}'")
        
        # 4. Disconnected Nodes Check
        connected_nodes = set()
        for source_node, outputs in connections.items():
            connected_nodes.add(source_node)
            for output_type, output_list in outputs.items():
                for conn_group in output_list:
                    if isinstance(conn_group, list):
                        for conn in conn_group:
                            if conn.get("node"):
                                connected_nodes.add(conn["node"])
        
        disconnected = node_names - connected_nodes
        if disconnected:
            warnings.append(f"Disconnected nodes (not connected to any other nodes): {', '.join(disconnected)}")
        
        # 5. Best Practices
        if len(nodes) > 50:
            warnings.append(f"Large workflow ({len(nodes)} nodes) - consider splitting into sub-workflows")
        
        # Check for error handling
        has_error_handler = any("error" in node.get("type", "").lower() for node in nodes)
        if not has_error_handler and len(nodes) > 5:
            info.append("No error handling nodes detected - consider adding error workflows")
        
        # Check for execution order
        if not workflow.get("settings", {}).get("executionOrder"):
            info.append("Execution order not explicitly set - using default 'v1' order")
        
        # Format result
        result = f"# Validation Report: {workflow.get('name', 'Unnamed Workflow')}\\n\\n"
        
        # Summary
        total_issues = len(errors) + len(warnings) + len(info)
        if total_issues == 0:
            result += "✅ **Validation Passed** - No issues found!\\n\\n"
        else:
            result += f"**Summary**: {len(errors)} errors, {len(warnings)} warnings, {len(info)} info\\n\\n"
        
        # Errors (critical)
        if errors:
            result += "## ❌ Errors (Must Fix)\\n\\n"
            for error in errors:
                result += f"- {error}\\n"
            result += "\\n"
        
        # Warnings (should fix)
        if warnings:
            result += "## ⚠️ Warnings (Should Fix)\\n\\n"
            for warning in warnings:
                result += f"- {warning}\\n"
            result += "\\n"
        
        # Info (nice to have)
        if info:
            result += "## ℹ️ Info (Recommendations)\\n\\n"
            for item in info:
                result += f"- {item}\\n"
            result += "\\n"
        
        # Stats
        result += "## 📊 Statistics\\n\\n"
        result += f"- **Total Nodes**: {len(nodes)}\\n"
        result += f"- **Active Nodes**: {len([n for n in nodes if not n.get('disabled')])}\\n"
        result += f"- **Disabled Nodes**: {len([n for n in nodes if n.get('disabled')])}\\n"
        result += f"- **Connections**: {sum(len(out_list) for outputs in connections.values() for out_list in outputs.values())}\\n"
        result += f"- **Disconnected Nodes**: {len(disconnected)}\\n"
        
        return [TextContent(type="text", text=result)]
    
    async def validate_workflow_json(self, arguments: dict) -> list[TextContent]:
        """Validate workflow JSON structure before creation
        
        Args:
            arguments: {"workflow": dict}
            
        Returns:
            Validation report
        """
        workflow = arguments["workflow"]
        
        errors = []
        warnings = []
        
        # 1. Required Fields
        if not isinstance(workflow, dict):
            errors.append("Workflow must be a dictionary/object")
            return [TextContent(type="text", text=f"❌ **Invalid Workflow**\\n\\n{errors[0]}")]
        
        if "nodes" not in workflow:
            errors.append("Missing required field: 'nodes'")
        
        if "connections" not in workflow:
            warnings.append("Missing 'connections' field - workflow will have no connections")
        
        # 2. Nodes Validation
        if "nodes" in workflow:
            if not isinstance(workflow["nodes"], list):
                errors.append("'nodes' must be an array")
            else:
                for i, node in enumerate(workflow["nodes"]):
                    if not isinstance(node, dict):
                        errors.append(f"Node at index {i} must be an object")
                        continue
                    
                    # Required node fields
                    if "name" not in node:
                        errors.append(f"Node at index {i} missing required field 'name'")
                    if "type" not in node:
                        errors.append(f"Node at index {i} missing required field 'type'")
                    if "position" not in node:
                        warnings.append(f"Node '{node.get('name', f'at index {i}')}' missing 'position'")
                    if "parameters" not in node:
                        node["parameters"] = {}
        
        # 3. Connections Validation
        if "connections" in workflow and workflow["connections"]:
            if not isinstance(workflow["connections"], dict):
                errors.append("'connections' must be an object")
        
        # 4. Name
        if "name" not in workflow:
            warnings.append("Workflow has no 'name' field")
        
        # Format result
        if errors:
            result = "# ❌ Validation Failed\\n\\n"
            result += "**Errors:**\\n"
            for error in errors:
                result += f"- {error}\\n"
            result += "\\n"
        else:
            result = "# ✅ Validation Passed\\n\\n"
            result += "Workflow JSON structure is valid!\\n\\n"
        
        if warnings:
            result += "**Warnings:**\\n"
            for warning in warnings:
                result += f"- {warning}\\n"
            result += "\\n"
        
        if not errors:
            result += "## ✅ Ready to Create\\n\\n"
            result += "This workflow can be created via `create_workflow` tool.\\n"
        
        return [TextContent(type="text", text=result)]
