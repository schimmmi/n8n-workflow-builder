#!/usr/bin/env python3
"""
Template & Intent Tool Handlers
Handles template search, recommendations, and intent analysis
"""
from typing import Any, TYPE_CHECKING

from mcp.types import TextContent

from .base import BaseTool, ToolError
from ..templates.recommender import WORKFLOW_TEMPLATES

if TYPE_CHECKING:
    from ..dependencies import Dependencies


class TemplateTools(BaseTool):
    """Handler for template and intent analysis tools"""
    
    async def handle(self, name: str, arguments: dict) -> list[TextContent]:
        """Route template/intent tool calls to appropriate handler methods
        
        Args:
            name: Tool name
            arguments: Tool arguments
            
        Returns:
            List of TextContent responses
        """
        handlers = {
            # Template tools
            "recommend_templates": self.recommend_templates,
            "get_template_library": self.get_template_library,
            "search_templates": self.search_templates,
            "get_templates_by_category": self.get_templates_by_category,
            "get_templates_by_difficulty": self.get_templates_by_difficulty,
            "get_template_details": self.get_template_details,
            
            # Intent tools
            "analyze_intent_coverage": self.analyze_intent_coverage,
            "suggest_node_intent": self.suggest_node_intent,
            "add_node_intent": self.add_node_intent,
            "get_workflow_intents": self.get_workflow_intents,
            "update_node_intent": self.update_node_intent,
        }
        
        handler = handlers.get(name)
        if not handler:
            raise ToolError("UNKNOWN_TOOL", f"Tool '{name}' not found in template tools")
        
        return await handler(arguments)
    
    # Template Tools
    
    async def recommend_templates(self, arguments: dict) -> list[TextContent]:
        """Recommend templates based on description and goal"""
        description = arguments["description"]
        workflow_goal = arguments.get("workflow_goal")
        min_score = arguments.get("min_score", 0.3)
        max_results = arguments.get("max_results", 5)
        
        recommendations = self.deps.template_engine.recommend_templates(
            description, workflow_goal, min_score, max_results
        )
        
        if not recommendations:
            return [TextContent(
                type="text",
                text=f"No templates found matching your criteria (min_score: {min_score}). "
                     f"Try lowering the minimum score or using different keywords."
            )]
        
        result = f"# 🎯 Template Recommendations\n\n"
        result += f"**Query:** {description}\n"
        if workflow_goal:
            result += f"**Goal:** {workflow_goal}\n"
        result += f"**Found:** {len(recommendations)} matching templates\n\n"
        
        for idx, rec in enumerate(recommendations, 1):
            template = rec['template']
            result += f"## {idx}. {template['name']} ({rec['match_percentage']}% match)\n\n"
            result += f"**Template ID:** `{rec['template_id']}`\n"
            result += f"**Category:** {template.get('category', 'N/A')}\n"
            result += f"**Difficulty:** {template.get('difficulty', 'N/A')}\n"
            result += f"**Estimated Time:** {template.get('estimated_time', 'N/A')}\n"
            result += f"**Description:** {template.get('description', 'N/A')}\n\n"
            result += f"**Use Cases:**\n"
            for uc in template.get('use_cases', []):
                result += f"- {uc}\n"
            result += "\n"
        
        result += "\n💡 Use `get_template_details` with the template_id to see full implementation details.\n"
        
        return [TextContent(type="text", text=result)]
    
    async def get_template_library(self, arguments: dict) -> list[TextContent]:
        """Get overview of all available templates"""
        report = self.deps.template_engine.generate_template_report()
        return [TextContent(type="text", text=report)]
    
    async def search_templates(self, arguments: dict) -> list[TextContent]:
        """Search templates by query string"""
        query = arguments["query"]
        results = self.deps.template_engine.search_templates(query)
        
        if not results:
            return [TextContent(
                type="text",
                text=f"No templates found matching '{query}'. Try different keywords or browse by category."
            )]
        
        result = f"# 🔍 Search Results: '{query}'\n\n"
        result += f"**Found:** {len(results)} templates\n\n"
        
        for template in results:
            result += f"### {template['name']}\n"
            result += f"- **ID:** `{template['template_id']}`\n"
            result += f"- **Category:** {template.get('category', 'N/A')}\n"
            result += f"- **Difficulty:** {template.get('difficulty', 'N/A')}\n"
            result += f"- **Description:** {template.get('description', 'N/A')}\n\n"
        
        return [TextContent(type="text", text=result)]
    
    async def get_templates_by_category(self, arguments: dict) -> list[TextContent]:
        """Get all templates in a specific category"""
        category = arguments["category"]
        templates = self.deps.template_engine.get_templates_by_category(category)
        
        if not templates:
            return [TextContent(
                type="text",
                text=f"No templates found in category '{category}'."
            )]
        
        result = f"# 📁 Templates in Category: {category.replace('_', ' ').title()}\n\n"
        result += f"**Total:** {len(templates)} templates\n\n"
        
        for template in templates:
            result += f"### {template['name']}\n"
            result += f"- **ID:** `{template['template_id']}`\n"
            result += f"- **Difficulty:** {template.get('difficulty', 'N/A')}\n"
            result += f"- **Description:** {template.get('description', 'N/A')}\n"
            result += f"- **Use Cases:** {', '.join(template.get('use_cases', []))}\n\n"
        
        return [TextContent(type="text", text=result)]
    
    async def get_templates_by_difficulty(self, arguments: dict) -> list[TextContent]:
        """Get all templates at a specific difficulty level"""
        difficulty = arguments["difficulty"]
        templates = self.deps.template_engine.get_templates_by_difficulty(difficulty)
        
        if not templates:
            return [TextContent(
                type="text",
                text=f"No templates found at difficulty level '{difficulty}'."
            )]
        
        result = f"# 📊 {difficulty.title()} Templates\n\n"
        result += f"**Total:** {len(templates)} templates\n\n"
        
        for template in templates:
            result += f"### {template['name']}\n"
            result += f"- **ID:** `{template['template_id']}`\n"
            result += f"- **Category:** {template.get('category', 'N/A')}\n"
            result += f"- **Estimated Time:** {template.get('estimated_time', 'N/A')}\n"
            result += f"- **Description:** {template.get('description', 'N/A')}\n\n"
        
        return [TextContent(type="text", text=result)]
    
    async def get_template_details(self, arguments: dict) -> list[TextContent]:
        """Get detailed information about a specific template"""
        template_id = arguments["template_id"]
        
        # Try new template registry first
        template = await self.deps.template_registry.get_template(template_id)
        
        if not template:
            # Try old WORKFLOW_TEMPLATES as fallback
            if template_id in WORKFLOW_TEMPLATES:
                template_dict = WORKFLOW_TEMPLATES[template_id]
                
                result = f"# 📄 Template Details: {template_dict['name']}\n\n"
                result += f"**Template ID:** `{template_id}`\n"
                result += f"**Category:** {template_dict.get('category', 'N/A')}\n"
                result += f"**Difficulty:** {template_dict.get('difficulty', 'N/A')}\n"
                result += f"**Estimated Time:** {template_dict.get('estimated_time', 'N/A')}\n\n"
                result += f"## Description\n\n{template_dict.get('description', 'N/A')}\n\n"
                
                result += f"## Use Cases\n\n"
                for uc in template_dict.get('use_cases', []):
                    result += f"- {uc}\n"
                result += "\n"
                
                result += f"## Node Structure\n\n"
                for idx, node in enumerate(template_dict.get('nodes', []), 1):
                    result += f"{idx}. **{node['name']}** (`{node['type']}`)\n"
                result += "\n"
                
                result += f"## Tags\n\n"
                result += ", ".join(f"`{tag}`" for tag in template_dict.get('tags', []))
                result += "\n\n"
                
                result += f"## Implementation Guide\n\n"
                result += f"1. Use this template as a starting point for your workflow\n"
                result += f"2. Customize node names and parameters to match your requirements\n"
                result += f"3. Configure credentials for nodes that require authentication\n"
                result += f"4. Test with sample data before deploying to production\n"
                result += f"5. Add error handling and monitoring as needed\n\n"
                
                result += f"💡 **Tip:** Use `generate_workflow_template` with `template_type='{template_id}'` "
                result += f"to get a detailed outline with this template.\n"
                
                return [TextContent(type="text", text=result)]
            else:
                # Template not found anywhere
                available = ", ".join(WORKFLOW_TEMPLATES.keys())
                return [TextContent(
                    type="text",
                    text=f"❌ Template '{template_id}' not found.\n\n"
                         f"Available templates: {available}"
                )]
        
        # Format new template registry result
        result = template.generate_report()
        return [TextContent(type="text", text=result)]
    
    # Intent Tools
    
    async def analyze_intent_coverage(self, arguments: dict) -> list[TextContent]:
        """Analyze how well workflow nodes document their intent"""
        workflow_id = arguments["workflow_id"]
        
        # Fetch workflow
        workflow = await self.deps.client.get_workflow(workflow_id)
        
        # Analyze coverage
        analysis = self.deps.intent_manager.analyze_intent_coverage(workflow)
        
        # Log action
        self.deps.state_manager.log_action("analyze_intent_coverage", {
            "workflow_id": workflow_id,
            "coverage": analysis["coverage_percentage"]
        })
        
        # Format result
        result = f"# Intent Coverage Analysis: {workflow['name']}\n\n"
        result += f"**Coverage**: {analysis['coverage_percentage']}%\n"
        result += f"**Nodes with Intent**: {analysis['nodes_with_intent']} / {analysis['total_nodes']}\n"
        result += f"**Nodes without Intent**: {analysis['nodes_without_intent']}\n\n"
        
        if analysis['critical_without_intent']:
            result += "## ⚠️ Critical Nodes Missing Intent:\n\n"
            for node_name in analysis['critical_without_intent']:
                result += f"- {node_name}\n"
            result += "\n"
        
        result += "## Node Breakdown:\n\n"
        result += f"- Triggers: {analysis['node_breakdown']['triggers']}\n"
        result += f"- Logic nodes: {analysis['node_breakdown']['logic']}\n"
        result += f"- Action nodes: {analysis['node_breakdown']['actions']}\n\n"
        
        result += f"## 💡 Recommendation\n\n{analysis['recommendation']}"
        
        return [TextContent(type="text", text=result)]
    
    async def suggest_node_intent(self, arguments: dict) -> list[TextContent]:
        """Suggest intent documentation for a specific node"""
        workflow_id = arguments["workflow_id"]
        node_name = arguments["node_name"]
        
        # Fetch workflow
        workflow = await self.deps.client.get_workflow(workflow_id)
        
        # Find node
        node = None
        for n in workflow.get("nodes", []):
            if n["name"] == node_name:
                node = n
                break
        
        if not node:
            return [TextContent(
                type="text",
                text=f"❌ Node '{node_name}' not found in workflow"
            )]
        
        # Generate suggestion
        suggestion = self.deps.intent_manager.suggest_intent_for_node(node, workflow)
        
        # Log action
        self.deps.state_manager.log_action("suggest_node_intent", {
            "workflow_id": workflow_id,
            "node_name": node_name
        })
        
        return [TextContent(type="text", text=suggestion)]
    
    async def add_node_intent(self, arguments: dict) -> list[TextContent]:
        """Add intent documentation to a workflow node
        
        Args:
            arguments: {
                "workflow_id": str,
                "node_name": str,
                "reason": str (required),
                "assumption": str (optional),
                "risk": str (optional),
                "alternative": str (optional),
                "dependency": str (optional)
            }
        
        Returns:
            Success confirmation with created intent
        """
        workflow_id = arguments["workflow_id"]
        node_name = arguments["node_name"]
        reason = arguments["reason"]
        
        # Fetch workflow
        workflow = await self.deps.client.get_workflow(workflow_id)
        
        # Find node
        node = None
        for n in workflow.get("nodes", []):
            if n["name"] == node_name:
                node = n
                break
        
        if not node:
            return [TextContent(
                type="text",
                text=f"❌ Node '{node_name}' not found in workflow"
            )]
        
        # Check if intent already exists
        existing_intent = self.deps.intent_manager.get_node_intent(node)
        if existing_intent:
            return [TextContent(
                type="text",
                text=f"❌ Node '{node_name}' already has intent metadata. Use 'update_node_intent' to modify it."
            )]
        
        # Create intent
        intent = self.deps.intent_manager.create_intent(
            reason=reason,
            assumption=arguments.get("assumption"),
            risk=arguments.get("risk"),
            alternative=arguments.get("alternative"),
            dependency=arguments.get("dependency")
        )
        
        # Add to node
        self.deps.intent_manager.add_intent_to_node(node, intent)
        
        # Save workflow
        await self.deps.client.update_workflow(workflow_id, workflow)
        
        # Log action
        self.deps.state_manager.log_action("add_node_intent", {
            "workflow_id": workflow_id,
            "node_name": node_name
        })
        
        result = f"✅ Intent added to node '{node_name}'\n\n"
        result += "**Intent Metadata:**\n"
        result += f"- **Why**: {reason}\n"
        
        if arguments.get("assumption"):
            result += f"- **Assumption**: {arguments['assumption']}\n"
        if arguments.get("risk"):
            result += f"- **Risk**: {arguments['risk']}\n"
        if arguments.get("alternative"):
            result += f"- **Alternative**: {arguments['alternative']}\n"
        if arguments.get("dependency"):
            result += f"- **Dependency**: {arguments['dependency']}\n"
        
        result += f"\n*Created: {intent['created_at']}*\n"
        
        return [TextContent(type="text", text=result)]
    
    async def get_workflow_intents(self, arguments: dict) -> list[TextContent]:
        """Get all intent metadata for a workflow
        
        Args:
            arguments: {
                "workflow_id": str,
                "format": str (optional) - "report" (default) or "json"
            }
        
        Returns:
            Formatted report or JSON of all workflow intents
        """
        workflow_id = arguments["workflow_id"]
        format_type = arguments.get("format", "report")
        
        # Fetch workflow
        workflow = await self.deps.client.get_workflow(workflow_id)
        
        # Get all intents
        intents = self.deps.intent_manager.get_workflow_intents(workflow)
        
        if format_type == "json":
            import json
            result = f"# Intent Metadata for Workflow: {workflow.get('name', 'Unnamed')}\n\n"
            result += f"```json\n{json.dumps(intents, indent=2)}\n```\n"
            return [TextContent(type="text", text=result)]
        
        # Generate report format
        report = self.deps.intent_manager.generate_intent_report(workflow)
        return [TextContent(type="text", text=report)]
    
    async def update_node_intent(self, arguments: dict) -> list[TextContent]:
        """Update intent documentation for a node"""
        workflow_id = arguments["workflow_id"]
        node_name = arguments["node_name"]
        
        # Fetch workflow
        workflow = await self.deps.client.get_workflow(workflow_id)
        
        # Find node
        node = None
        for n in workflow.get("nodes", []):
            if n["name"] == node_name:
                node = n
                break
        
        if not node:
            return [TextContent(
                type="text",
                text=f"❌ Node '{node_name}' not found in workflow"
            )]
        
        # Build updates
        updates = {}
        if "reason" in arguments:
            updates["reason"] = arguments["reason"]
        if "assumption" in arguments:
            updates["assumption"] = arguments["assumption"]
        if "risk" in arguments:
            updates["risk"] = arguments["risk"]
        if "alternative" in arguments:
            updates["alternative"] = arguments["alternative"]
        if "dependency" in arguments:
            updates["dependency"] = arguments["dependency"]
        
        if not updates:
            return [TextContent(
                type="text",
                text="No updates provided. Specify at least one field to update."
            )]
        
        # Update intent
        self.deps.intent_manager.update_node_intent(node, updates)
        
        # Save workflow
        await self.deps.client.update_workflow(workflow_id, workflow)
        
        # Log action
        self.deps.state_manager.log_action("update_node_intent", {
            "workflow_id": workflow_id,
            "node_name": node_name,
            "fields_updated": list(updates.keys())
        })
        
        result = f"✅ Intent updated for node '{node_name}'\n\n"
        result += "**Updated fields:**\n"
        for key in updates.keys():
            result += f"- {key.capitalize()}\n"
        
        return [TextContent(type="text", text=result)]
