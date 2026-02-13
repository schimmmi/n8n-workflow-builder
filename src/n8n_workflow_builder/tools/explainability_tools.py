#!/usr/bin/env python3
"""
Explainability Tool Handlers  
Handles workflow explanations, node explanations, purpose analysis, and template match explanations
"""
from typing import Any, TYPE_CHECKING
import logging

from mcp.types import TextContent

from .base import BaseTool, ToolError
from ..builders.workflow_builder import NODE_KNOWLEDGE
from ..explainability import WorkflowExplainer, WorkflowPurposeAnalyzer, ExplainabilityFormatter
from ..drift.detector import DriftDetector

if TYPE_CHECKING:
    from ..dependencies import Dependencies

logger = logging.getLogger(__name__)


class ExplainabilityTools(BaseTool):
    """Handler for workflow and node explanation tools"""
    
    async def handle(self, name: str, arguments: dict) -> list[TextContent]:
        """Route explainability tool calls to appropriate handler methods
        
        Args:
            name: Tool name
            arguments: Tool arguments
            
        Returns:
            List of TextContent responses
        """
        handlers = {
            "explain_node": self.explain_node,
            "explain_workflow": self.explain_workflow,
            "get_workflow_purpose": self.get_workflow_purpose,
            "explain_template_match": self.explain_template_match,
        }
        
        handler = handlers.get(name)
        if not handler:
            raise ToolError("UNKNOWN_TOOL", f"Tool '{name}' not found in explainability tools")
        
        return await handler(arguments)
    
    async def explain_node(self, arguments: dict) -> list[TextContent]:
        """Explain a specific node type from knowledge base"""
        node_type = arguments["node_type"].lower()
        
        # Search in knowledge base
        explanation = None
        for category in NODE_KNOWLEDGE.values():
            if node_type in category:
                explanation = category[node_type]
                break
        
        if not explanation:
            available_nodes = []
            for category in NODE_KNOWLEDGE.values():
                available_nodes.extend(category.keys())
            
            return [TextContent(
                type="text",
                text=f"Node type '{node_type}' not found in knowledge base. "
                     f"Try: {', '.join(available_nodes[:10])}"
            )]
        
        result = f"# {explanation['name']} Node\n\n"
        result += f"**Description:** {explanation['desc']}\n\n"
        result += "## Use Cases:\n\n"
        for use_case in explanation['use_cases']:
            result += f"- {use_case}\n"
        result += "\n## Best Practices:\n\n"
        for practice in explanation['best_practices']:
            result += f"- {practice}\n"
        
        return [TextContent(type="text", text=result)]
    
    async def explain_workflow(self, arguments: dict) -> list[TextContent]:
        """Generate comprehensive explanation of a workflow"""
        workflow_id = arguments["workflow_id"]
        format_type = arguments.get("format", "markdown")
        include_analysis = arguments.get("include_analysis", True)
        
        # Fetch workflow
        workflow = await self.deps.client.get_workflow(workflow_id)
        # Handle if API returns list instead of dict
        if isinstance(workflow, list):
            workflow = workflow[0] if workflow else {}
        
        all_workflows = await self.deps.client.list_workflows()
        
        # Optional: Fetch semantic analysis and execution history
        semantic_analysis = None
        drift_analysis = None
        execution_history = None
        
        if include_analysis:
            # Import here to avoid circular dependencies
            from ..validators.semantic_analyzer import SemanticWorkflowAnalyzer
            
            try:
                semantic_analysis = SemanticWorkflowAnalyzer.analyze_workflow_semantics(workflow)
            except Exception as e:
                logger.warning(f"Could not get semantic analysis: {e}")
            
            try:
                execution_history = await self.deps.client.get_executions(workflow_id, limit=100)
                if execution_history:
                    drift_analysis = DriftDetector.analyze_execution_history(execution_history)
            except Exception as e:
                logger.warning(f"Could not get execution history: {e}")
        
        # Fetch intent metadata for documentation coverage
        intent_metadata = None
        try:
            workflow_intents = self.deps.intent_manager.get_workflow_intents(workflow)
            if workflow_intents:
                intent_metadata = {"nodes": workflow_intents}
        except Exception as e:
            logger.debug(f"Could not get intent metadata: {e}")
        
        # Generate explanation
        explanation = WorkflowExplainer.explain_workflow(
            workflow,
            all_workflows=all_workflows,
            semantic_analysis=semantic_analysis,
            drift_analysis=drift_analysis,
            execution_history=execution_history,
            intent_metadata=intent_metadata
        )
        
        # Format output
        formatted = ExplainabilityFormatter.format(explanation, format_type)
        
        return [TextContent(type="text", text=formatted)]
    
    async def get_workflow_purpose(self, arguments: dict) -> list[TextContent]:
        """Analyze and explain the purpose of a workflow"""
        workflow_id = arguments["workflow_id"]
        
        # Fetch workflow
        workflow = await self.deps.client.get_workflow(workflow_id)
        
        # Analyze purpose
        purpose_analysis = WorkflowPurposeAnalyzer.analyze_purpose(workflow)
        
        # Format result
        result = f"# Workflow Purpose: {workflow['name']}\n\n"
        result += f"**Primary Purpose**: {purpose_analysis.get('primary_purpose')}\n\n"
        result += f"**Business Domain**: {purpose_analysis.get('business_domain')}\n"
        result += f"**Workflow Type**: {purpose_analysis.get('workflow_type')}\n"
        result += f"**Confidence**: {purpose_analysis.get('confidence', 0)*100:.0f}%\n\n"
        result += f"**Description**: {purpose_analysis.get('description')}\n\n"
        
        # Trigger
        result += "## Trigger\n\n"
        result += f"{purpose_analysis.get('trigger_description')}\n\n"
        
        # Expected Outcomes
        outcomes = purpose_analysis.get('expected_outcomes', [])
        if outcomes:
            result += "## Expected Outcomes\n\n"
            for outcome in outcomes:
                result += f"- {outcome}\n"
            result += "\n"
        
        # Key Components
        components = purpose_analysis.get('key_components', [])
        if components:
            result += "## Key Components\n\n"
            for component in components:
                result += f"- **{component.get('name')}**: {component.get('purpose')}\n"
            result += "\n"
        
        # Similar  Patterns
        similar = purpose_analysis.get('similar_patterns', [])
        if similar:
            result += "## Similar Usage Patterns\n\n"
            for pattern in similar:
                result += f"- {pattern}\n"
        
        return [TextContent(type="text", text=result)]
    
    async def explain_template_match(self, arguments: dict) -> list[TextContent]:
        """Explain why a template was matched to a query"""
        query = arguments["query"]
        template_id = arguments["template_id"]
        
        explanation = self.deps.template_manager.explain_template_match(query, template_id)
        
        if explanation.get('error'):
            return [TextContent(type="text", text=f"❌ {explanation['error']}")]
        
        result = f"# 📊 Template Match Explanation\n\n"
        result += f"**Query:** {query}\n"
        result += f"**Template:** {explanation['template_name']}\n"
        result += f"**Total Score:** {explanation['total_score']:.2%}\n\n"
        
        result += "## Score Breakdown:\n\n"
        breakdown = explanation.get('breakdown', {})
        result += f"- **Goal Similarity:** {breakdown.get('goal_similarity', 0):.2%} (weight: 30%)\n"
        result += f"- **Node Overlap:** {breakdown.get('node_overlap', 0):.2%} (weight: 25%)\n"
        result += f"- **Trigger Match:** {breakdown.get('trigger_match', 0):.2%} (weight: 15%)\n"
        result += f"- **Action Match:** {breakdown.get('action_match', 0):.2%} (weight: 15%)\n"
        result += f"- **Domain Match:** {breakdown.get('domain_match', 0):.2%} (weight: 10%)\n"
        result += f"- **Complexity Match:** {breakdown.get('complexity_match', 0):.2%} (weight: 5%)\n\n"
        
        result += "## Extracted Intent:\n\n"
        intent = explanation.get('intent', {})
        result += f"- **Goal:** {intent.get('goal', 'unknown')}\n"
        if intent.get('trigger_type'):
            result += f"- **Trigger Type:** {intent['trigger_type']}\n"
        if intent.get('required_nodes'):
            result += f"- **Required Nodes:** {', '.join(intent['required_nodes'])}\n"
        if intent.get('preferred_nodes'):
            result += f"- **Preferred Nodes:** {', '.join(intent['preferred_nodes'])}\n"
        if intent.get('action_types'):
            result += f"- **Action Types:** {', '.join(intent['action_types'])}\n"
        if intent.get('domain'):
            result += f"- **Domain:** {intent['domain']}\n"
        
        return [TextContent(type="text", text=result)]
