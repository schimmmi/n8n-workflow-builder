#!/usr/bin/env python3
"""
Drift Detection Tool Handlers
Handles workflow drift detection, pattern analysis, root cause determination, and fix suggestions
"""
from typing import Any, TYPE_CHECKING

from mcp.types import TextContent

from .base import BaseTool, ToolError
from ..drift.detector import DriftDetector, DriftRootCauseAnalyzer, DriftFixSuggester
from ..changes import WorkflowDiffEngine, ChangeFormatter, ChangeImpactAnalyzer

if TYPE_CHECKING:
    from ..dependencies import Dependencies


class DriftTools(BaseTool):
    """Handler for drift detection and workflow comparison tools"""
    
    async def handle(self, name: str, arguments: dict) -> list[TextContent]:
        """Route drift tool calls to appropriate handler methods
        
        Args:
            name: Tool name
            arguments: Tool arguments
            
        Returns:
            List of TextContent responses
        """
        handlers = {
            "detect_workflow_drift": self.detect_workflow_drift,
            "analyze_drift_pattern": self.analyze_drift_pattern,
            "get_drift_root_cause": self.get_drift_root_cause,
            "get_drift_fix_suggestions": self.get_drift_fix_suggestions,
            "compare_workflows": self.compare_workflows,
        }
        
        handler = handlers.get(name)
        if not handler:
            raise ToolError("UNKNOWN_TOOL", f"Tool '{name}' not found in drift tools")
        
        return await handler(arguments)
    
    async def detect_workflow_drift(self, arguments: dict) -> list[TextContent]:
        """Detect drift in workflow execution patterns"""
        workflow_id = arguments["workflow_id"]
        lookback_days = arguments.get("lookback_days", 30)
        
        # Fetch workflow and executions
        workflow = await self.deps.client.get_workflow(workflow_id)
        executions = await self.deps.client.get_executions(workflow_id, limit=100)
        
        if not executions or len(executions) < 2:
            return [TextContent(
                type="text",
                text=f"ℹ️ Insufficient execution history for drift detection (need at least 2 executions)"
            )]
        
        # Analyze drift
        drift_analysis = DriftDetector.analyze_execution_history(executions)
        
        # Log action
        self.deps.state_manager.log_action("detect_workflow_drift", {
            "workflow_id": workflow_id,
            "drift_detected": drift_analysis.get("drift_detected", False),
            "severity": drift_analysis.get("severity", "none")
        })
        
        # Format result
        result = f"# Drift Detection: {workflow['name']}\n\n"
        
        if not drift_analysis.get("drift_detected"):
            result += "✅ **No significant drift detected**\n\n"
            result += "Workflow appears stable over analyzed period.\n"
            return [TextContent(type="text", text=result)]
        
        severity = drift_analysis.get("severity", "info")
        severity_emoji = {"critical": "🔴", "warning": "⚠️", "info": "ℹ️"}.get(severity, "ℹ️")
        
        result += f"{severity_emoji} **Drift Detected - Severity: {severity.upper()}**\n\n"
        
        # Show metrics comparison
        baseline = drift_analysis.get("baseline_period", {}).get("metrics", {})
        current = drift_analysis.get("current_period", {}).get("metrics", {})
        
        result += "## Metrics Comparison\n\n"
        result += f"**Success Rate:**\n"
        result += f"- Baseline: {baseline.get('success_rate', 0):.1%}\n"
        result += f"- Current: {current.get('success_rate', 0):.1%}\n"
        result += f"- Change: {(current.get('success_rate', 0) - baseline.get('success_rate', 0)):.1%}\n\n"
        
        result += f"**Avg Duration:**\n"
        result += f"- Baseline: {baseline.get('avg_duration', 0):.0f}ms\n"
        result += f"- Current: {current.get('avg_duration', 0):.0f}ms\n\n"
        
        # Show drift patterns
        patterns = drift_analysis.get("patterns", [])
        if patterns:
            result += "## 🔍 Detected Patterns\n\n"
            for pattern in patterns:
                severity_icon = {"critical": "🔴", "warning": "⚠️", "info": "ℹ️"}.get(pattern.get("severity"), "ℹ️")
                result += f"{severity_icon} **{pattern.get('type')}**\n"
                result += f"- {pattern.get('description')}\n\n"
        
        result += f"\n💡 **Next Steps:**\n"
        result += f"- Use `analyze_drift_pattern` for detailed pattern analysis\n"
        result += f"- Use `get_drift_root_cause` to find root cause\n"
        result += f"- Use `get_drift_fix_suggestions` for fix recommendations\n"
        
        return [TextContent(type="text", text=result)]
    
    async def analyze_drift_pattern(self, arguments: dict) -> list[TextContent]:
        """Analyze specific drift patterns in detail"""
        workflow_id = arguments["workflow_id"]
        pattern_type = arguments["pattern_type"]
        
        # Fetch workflow and executions
        workflow = await self.deps.client.get_workflow(workflow_id)
        executions = await self.deps.client.get_executions(workflow_id, limit=100)
        
        # Get drift analysis
        drift_analysis = DriftDetector.analyze_execution_history(executions)
        
        if not drift_analysis.get("drift_detected"):
            return [TextContent(
                type="text",
                text="ℹ️ No drift detected - pattern analysis not applicable"
            )]
        
        # Find specific pattern
        patterns = drift_analysis.get("patterns", [])
        pattern = next((p for p in patterns if p["type"] == pattern_type), None)
        
        if not pattern:
            return [TextContent(
                type="text",
                text=f"ℹ️ Pattern '{pattern_type}' not found in drift analysis. Available patterns: {', '.join([p['type'] for p in patterns])}"
            )]
        
        # Detailed pattern analysis
        result = f"# Drift Pattern Analysis: {workflow['name']}\n\n"
        result += f"**Pattern**: `{pattern_type}`\n"
        result += f"**Severity**: {pattern.get('severity', 'unknown').upper()}\n"
        result += f"**Description**: {pattern.get('description')}\n\n"
        
        # Add pattern-specific details
        if pattern.get("frequency"):
            result += f"**Frequency**: {pattern['frequency']}\n"
        if pattern.get("first_seen"):
            result += f"**First Seen**: {pattern['first_seen']}\n"
        if pattern.get("affected_nodes"):
            result += f"**Affected Nodes**: {', '.join(pattern['affected_nodes'])}\n"
        
        result += "\n## 📊 Pattern Details\n\n"
        details = pattern.get("details", {})
        for key, value in details.items():
            result += f"- **{key}**: {value}\n"
        
        return [TextContent(type="text", text=result)]
    
    async def get_drift_root_cause(self, arguments: dict) -> list[TextContent]:
        """Determine the root cause of workflow drift"""
        workflow_id = arguments["workflow_id"]
        lookback_days = arguments.get("lookback_days", 30)
        
        # Fetch workflow and executions
        workflow = await self.deps.client.get_workflow(workflow_id)
        executions = await self.deps.client.get_executions(workflow_id, limit=100)
        
        # Get drift analysis
        drift_analysis = DriftDetector.analyze_execution_history(executions)
        
        if not drift_analysis.get("drift_detected"):
            return [TextContent(
                type="text",
                text="ℹ️ No drift detected - root cause analysis not applicable"
            )]
        
        # Analyze root cause
        root_cause = DriftRootCauseAnalyzer.analyze_root_cause(
            drift_analysis, executions, workflow
        )
        
        # Format result
        result = f"# Root Cause Analysis: {workflow['name']}\n\n"
        result += f"**Root Cause**: `{root_cause.get('root_cause', 'unknown')}`\n"
        result += f"**Confidence**: {root_cause.get('confidence', 0):.0%}\n\n"
        
        evidence = root_cause.get("evidence", [])
        if evidence:
            result += "## 📋 Evidence\n\n"
            for item in evidence:
                result += f"- {item}\n"
            result += "\n"
        
        result += f"## 💡 Recommended Action\n\n{root_cause.get('recommended_action')}\n"
        
        return [TextContent(type="text", text=result)]
    
    async def get_drift_fix_suggestions(self, arguments: dict) -> list[TextContent]:
        """Get concrete fix suggestions for detected drift"""
        workflow_id = arguments["workflow_id"]
        
        # Fetch workflow and executions
        workflow = await self.deps.client.get_workflow(workflow_id)
        executions = await self.deps.client.get_executions(workflow_id, limit=100)
        
        # Get drift analysis and root cause
        drift_analysis = DriftDetector.analyze_execution_history(executions)
        
        if not drift_analysis.get("drift_detected"):
            return [TextContent(
                type="text",
                text="ℹ️ No drift detected - no fixes needed"
            )]
        
        root_cause = DriftRootCauseAnalyzer.analyze_root_cause(
            drift_analysis, executions, workflow
        )
        
        # Get fix suggestions
        patterns = drift_analysis.get("patterns", [])
        suggestions = DriftFixSuggester.suggest_fixes(root_cause, workflow, patterns)
        
        # Format result
        result = f"# Fix Suggestions: {workflow['name']}\n\n"
        result += f"**Root Cause**: {suggestions.get('root_cause')}\n"
        result += f"**Confidence**: {suggestions.get('confidence', 0):.0%}\n\n"
        
        fixes = suggestions.get("fixes", [])
        if fixes:
            result += "## 🔧 Suggested Fixes\n\n"
            for i, fix in enumerate(fixes, 1):
                result += f"### {i}. {fix.get('description')}\n\n"
                if fix.get("node"):
                    result += f"**Node**: {fix.get('node')}\n"
                result += f"**Suggestion**: {fix.get('suggestion')}\n"
                result += f"**Confidence**: {fix.get('confidence', 0):.0%}\n\n"
        
        testing = suggestions.get("testing_recommendations", [])
        if testing:
            result += "## ✅ Testing Recommendations\n\n"
            for rec in testing:
                result += f"- {rec}\n"
        
        return [TextContent(type="text", text=result)]
    
    async def compare_workflows(self, arguments: dict) -> list[TextContent]:
        """Compare two workflows and show differences"""
        workflow_id_1 = arguments["workflow_id_1"]
        workflow_id_2 = arguments["workflow_id_2"]
        
        # Fetch both workflows
        workflow_1 = await self.deps.client.get_workflow(workflow_id_1)
        workflow_2 = await self.deps.client.get_workflow(workflow_id_2)
        
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
                result +=f"  + {node['name']} ({node.get('type', 'unknown')})\n"
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
