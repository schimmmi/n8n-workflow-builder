#!/usr/bin/env python3
"""
Intent Metadata Module
Manages "why" metadata for workflow nodes to maintain AI context across iterations
"""
from typing import Dict, List, Optional
from datetime import datetime


class IntentManager:
    """Manages intent metadata for workflow nodes

    Intent metadata helps LLMs remember WHY they built something,
    maintaining context and decision rationale across multiple iterations.
    """

    @staticmethod
    def create_intent(
        reason: str,
        assumption: Optional[str] = None,
        risk: Optional[str] = None,
        alternative: Optional[str] = None,
        dependency: Optional[str] = None
    ) -> Dict:
        """Create an intent metadata object

        Args:
            reason: Why this node exists / what problem it solves
            assumption: What assumptions were made when building this
            risk: Known risks or limitations
            alternative: Alternative approaches that were considered
            dependency: Dependencies on other nodes or external systems

        Returns:
            Intent metadata dictionary
        """
        intent = {
            "reason": reason,
            "created_at": datetime.now().isoformat(),
            "version": "1.0"
        }

        if assumption:
            intent["assumption"] = assumption
        if risk:
            intent["risk"] = risk
        if alternative:
            intent["alternative"] = alternative
        if dependency:
            intent["dependency"] = dependency

        return intent

    @staticmethod
    def add_intent_to_node(node: Dict, intent: Dict) -> Dict:
        """Add intent metadata to a node

        Args:
            node: n8n node object
            intent: Intent metadata object

        Returns:
            Node with intent metadata added
        """
        node["_intent"] = intent
        return node

    @staticmethod
    def get_node_intent(node: Dict) -> Optional[Dict]:
        """Get intent metadata from a node

        Args:
            node: n8n node object

        Returns:
            Intent metadata if present, None otherwise
        """
        return node.get("_intent")

    @staticmethod
    def update_node_intent(node: Dict, updates: Dict) -> Dict:
        """Update intent metadata for a node

        Args:
            node: n8n node object
            updates: Fields to update in intent

        Returns:
            Node with updated intent metadata
        """
        if "_intent" not in node:
            node["_intent"] = {}

        node["_intent"].update(updates)
        node["_intent"]["updated_at"] = datetime.now().isoformat()

        return node

    @staticmethod
    def remove_intent_from_node(node: Dict) -> Dict:
        """Remove intent metadata from a node

        Args:
            node: n8n node object

        Returns:
            Node without intent metadata
        """
        if "_intent" in node:
            del node["_intent"]
        return node

    @staticmethod
    def get_workflow_intents(workflow: Dict) -> Dict[str, Dict]:
        """Get all intent metadata from a workflow

        Args:
            workflow: Workflow object

        Returns:
            Dictionary mapping node names to their intent metadata
        """
        intents = {}

        for node in workflow.get("nodes", []):
            intent = IntentManager.get_node_intent(node)
            if intent:
                intents[node["name"]] = intent

        return intents

    @staticmethod
    def generate_intent_report(workflow: Dict) -> str:
        """Generate a human-readable report of all intents in a workflow

        Args:
            workflow: Workflow object

        Returns:
            Markdown formatted report
        """
        intents = IntentManager.get_workflow_intents(workflow)

        if not intents:
            return "# Intent Report\n\nNo intent metadata found in this workflow.\n"

        report = f"# Intent Report: {workflow.get('name', 'Unnamed Workflow')}\n\n"
        report += f"**Total Nodes with Intent**: {len(intents)}\n\n"
        report += "---\n\n"

        for node_name, intent in intents.items():
            report += f"## 📌 {node_name}\n\n"

            # Reason (required)
            report += f"**Why it exists:**\n{intent['reason']}\n\n"

            # Assumption (optional)
            if "assumption" in intent:
                report += f"**Assumptions:**\n{intent['assumption']}\n\n"

            # Risk (optional)
            if "risk" in intent:
                report += f"⚠️ **Known Risks:**\n{intent['risk']}\n\n"

            # Alternative (optional)
            if "alternative" in intent:
                report += f"**Alternatives Considered:**\n{intent['alternative']}\n\n"

            # Dependency (optional)
            if "dependency" in intent:
                report += f"**Dependencies:**\n{intent['dependency']}\n\n"

            # Metadata
            report += f"*Created: {intent.get('created_at', 'Unknown')}*\n"
            if "updated_at" in intent:
                report += f"*Updated: {intent['updated_at']}*\n"

            report += "\n---\n\n"

        return report

    @staticmethod
    def analyze_intent_coverage(workflow: Dict) -> Dict:
        """Analyze how well the workflow is documented with intents

        Args:
            workflow: Workflow object

        Returns:
            Analysis results with coverage statistics
        """
        nodes = workflow.get("nodes", [])
        total_nodes = len(nodes)

        if total_nodes == 0:
            return {
                "coverage_percentage": 0,
                "total_nodes": 0,
                "nodes_with_intent": 0,
                "nodes_without_intent": 0,
                "recommendation": "Workflow has no nodes"
            }

        nodes_with_intent = sum(1 for node in nodes if "_intent" in node)
        nodes_without_intent = total_nodes - nodes_with_intent
        coverage_percentage = (nodes_with_intent / total_nodes) * 100

        # Categorize nodes by type
        trigger_nodes = [n for n in nodes if "trigger" in n.get("type", "").lower()]
        logic_nodes = [n for n in nodes if any(x in n.get("type", "").lower() for x in ["if", "switch", "merge"])]
        action_nodes = [n for n in nodes if n not in trigger_nodes and n not in logic_nodes]

        # Check which critical nodes lack intent
        critical_without_intent = []
        for node in logic_nodes + trigger_nodes:
            if "_intent" not in node:
                critical_without_intent.append(node["name"])

        # Generate recommendation
        if coverage_percentage >= 80:
            recommendation = "Excellent documentation! Most nodes have clear intent."
        elif coverage_percentage >= 50:
            recommendation = "Good coverage, but consider adding intent to remaining nodes for better maintainability."
        elif coverage_percentage >= 25:
            recommendation = "Moderate coverage. Adding intent to critical nodes (triggers, logic) would improve understanding."
        else:
            recommendation = "Low coverage. Consider documenting the 'why' for each node to maintain context across iterations."

        return {
            "coverage_percentage": round(coverage_percentage, 1),
            "total_nodes": total_nodes,
            "nodes_with_intent": nodes_with_intent,
            "nodes_without_intent": nodes_without_intent,
            "critical_without_intent": critical_without_intent,
            "node_breakdown": {
                "triggers": len(trigger_nodes),
                "logic": len(logic_nodes),
                "actions": len(action_nodes)
            },
            "recommendation": recommendation
        }

    @staticmethod
    def suggest_intent_for_node(node: Dict, workflow_context: Optional[Dict] = None) -> str:
        """Suggest intent documentation for a node based on its type and parameters

        Args:
            node: Node object
            workflow_context: Optional workflow context for better suggestions

        Returns:
            Suggested intent template as markdown
        """
        node_type = node.get("type", "unknown")
        node_name = node.get("name", "Unknown Node")

        # Generate suggestions based on node type
        suggestions = f"# Suggested Intent for: {node_name}\n\n"
        suggestions += f"**Node Type**: `{node_type}`\n\n"
        suggestions += "## Template:\n\n"
        suggestions += "```json\n"
        suggestions += '{\n'
        suggestions += '  "_intent": {\n'

        # Type-specific suggestions
        if "trigger" in node_type.lower():
            suggestions += '    "reason": "Triggers the workflow when [CONDITION]",\n'
            suggestions += '    "assumption": "Event will occur at least [FREQUENCY]",\n'
            suggestions += '    "risk": "May miss events if [CONDITION]"\n'
        elif "http" in node_type.lower():
            suggestions += '    "reason": "Fetches [DATA] from [SERVICE] API",\n'
            suggestions += '    "assumption": "API returns [FORMAT] and is available 24/7",\n'
            suggestions += '    "risk": "Rate limits, timeouts, authentication failures",\n'
            suggestions += '    "dependency": "Requires valid API credentials and network access"\n'
        elif "if" in node_type.lower():
            suggestions += '    "reason": "Routes data based on [CONDITION]",\n'
            suggestions += '    "assumption": "Data field [FIELD] always exists",\n'
            suggestions += '    "alternative": "Could use Switch node for multiple conditions"\n'
        elif "set" in node_type.lower():
            suggestions += '    "reason": "Transforms data to match [TARGET] format",\n'
            suggestions += '    "assumption": "Input data structure is consistent",\n'
            suggestions += '    "risk": "May fail if input format changes"\n'
        else:
            suggestions += '    "reason": "Performs [ACTION] to achieve [GOAL]",\n'
            suggestions += '    "assumption": "[ASSUMPTIONS ABOUT INPUT/OUTPUT]",\n'
            suggestions += '    "risk": "[POTENTIAL ISSUES OR FAILURES]"\n'

        suggestions += '  }\n'
        suggestions += '}\n'
        suggestions += '```\n\n'
        suggestions += "## Guidelines:\n\n"
        suggestions += "- **reason**: Explain WHAT this node does and WHY it's needed\n"
        suggestions += "- **assumption**: State any assumptions about data, timing, or environment\n"
        suggestions += "- **risk**: Identify potential failure points or limitations\n"
        suggestions += "- **alternative**: Mention other approaches you considered\n"
        suggestions += "- **dependency**: List dependencies on other systems or nodes\n"

        return suggestions
