"""
Miscellaneous Tools - Remaining specialized tools for n8n workflow management

This handler consolidates various specialized tools including:
- Advanced drift detection (schema, rate limit, quality, root cause, fixes)
- Workflow analysis (data flow, dependencies, change simulation)  
- Change management (requests, reviews, history)
- Migration utilities (available migrations, workflow templates, debugging)
- Node search and recommendations
"""

import json
from typing import Any
from mcp.types import TextContent, Tool
from .base import BaseTool


class MiscellaneousTools(BaseTool):
    """Handler for miscellaneous specialized workflow tools"""

    def get_tools(self) -> list[Tool]:
        """Return list of all miscellaneous tools"""
        return [
            # Advanced Drift Detection Tools
            Tool(
                name="get_drift_root_cause",
                description="Analyze root cause of detected workflow drift",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {"type": "string", "description": "Workflow ID to analyze"},
                        "lookback_days": {"type": "integer", "description": "How many days to analyze (default: 30)", "default": 30}
                    },
                    "required": ["workflow_id"]
                }
            ),
            Tool(
                name="get_drift_fix_suggestions",
                description="Get specific fix suggestions for detected drift",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {"type": "string", "description": "Workflow ID to analyze"}
                    },
                    "required": ["workflow_id"]
                }
            ),
            Tool(
                name="detect_schema_drift",
                description="Detect API schema drift in workflow data",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {"type": "string", "description": "Workflow ID to analyze"},
                        "lookback_days": {"type": "integer", "description": "How many days to analyze (default: 30)", "default": 30}
                    },
                    "required": ["workflow_id"]
                }
            ),
            Tool(
                name="detect_rate_limit_drift",
                description="Detect rate limiting issues and throughput changes",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {"type": "string", "description": "Workflow ID to analyze"},
                        "lookback_days": {"type": "integer", "description": "How many days to analyze (default: 30)", "default": 30}
                    },
                    "required": ["workflow_id"]
                }
            ),
            Tool(
                name="detect_quality_drift",
                description="Detect data quality degradation over time",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {"type": "string", "description": "Workflow ID to analyze"},
                        "lookback_days": {"type": "integer", "description": "How many days to analyze (default: 30)", "default": 30}
                    },
                    "required": ["workflow_id"]
                }
            ),
            
            # Workflow Analysis Tools
            Tool(
                name="trace_data_flow",
                description="Trace data flow through workflow nodes",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {"type": "string", "description": "Workflow ID to trace"}
                    },
                    "required": ["workflow_id"]
                }
            ),
            Tool(
                name="map_dependencies",
                description="Map internal and external workflow dependencies",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {"type": "string", "description": "Workflow ID to analyze"}
                    },
                    "required": ["workflow_id"]
                }
            ),
            Tool(
                name="simulate_workflow_changes",
                description="Simulate effects of proposed workflow changes",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {"type": "string", "description": "Workflow ID"},
                        "changes": {"type": "object", "description": "Proposed changes to simulate"}
                    },
                    "required": ["workflow_id", "changes"]
                }
            ),
            
            # Change Management Tools
            Tool(
                name="create_change_request",
                description="Create a change request for workflow modification",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {"type": "string", "description": "Target workflow ID"},
                        "workflow_name": {"type": "string", "description": "Workflow name"},
                        "changes": {"type": "object", "description": "Proposed changes"},
                        "reason": {"type": "string", "description": "Reason for change"},
                        "requester": {"type": "string", "description": "Who is requesting the change"}
                    },
                    "required": ["workflow_id", "workflow_name", "changes", "reason", "requester"]
                }
            ),
            Tool(
                name="review_change_request",
                description="Approve or reject a change request",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "request_id": {"type": "string", "description": "Request ID to review"},
                        "action": {"type": "string", "enum": ["approve", "reject"], "description": "Review action"},
                        "reviewer": {"type": "string", "description": "Who is reviewing"},
                        "comments": {"type": "string", "description": "Review comments"}
                    },
                    "required": ["request_id", "action", "reviewer"]
                }
            ),
            Tool(
                name="get_change_history",
                description="Get change request history for a workflow",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {"type": "string", "description": "Workflow ID"}
                    },
                    "required": ["workflow_id"]
                }
            ),
            
            # Migration & Utility Tools
            Tool(
                name="get_available_migrations",
                description="Get available migration rules for a node type",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "node_type": {"type": "string", "description": "Node type to check migrations for"}
                    },
                    "required": ["node_type"]
                }
            ),
            Tool(
                name="generate_workflow_template",
                description="Generate a workflow template from description",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "description": {"type": "string", "description": "Workflow description"},
                        "template_type": {"type": "string", "description": "Template type (default: custom)", "default": "custom"}
                    },
                    "required": ["description"]
                }
            ),
            Tool(
                name="debug_workflow_error",
                description="Debug and explain workflow errors",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "error_message": {"type": "string", "description": "Error message to debug"},
                        "node_type": {"type": "string", "description": "Node type where error occurred"}
                    },
                    "required": ["error_message"]
                }
            ),
            
            # Node Search Tools
            Tool(
                name="search_nodes",
                description="Search discovered nodes by query",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"}
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="recommend_nodes_for_task",
                description="Get node recommendations for a specific task",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_description": {"type": "string", "description": "Task description"},
                        "top_k": {"type": "integer", "description": "Number of recommendations (default: 5)", "default": 5}
                    },
                    "required": ["task_description"]
                }
            )
        ]

    async def handle(self, name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Route tool calls to appropriate handlers"""
        
        # Get dependencies
        n8n_client = self.deps.client
        workflow_builder = self.deps.workflow_builder
        state_manager = self.deps.state_manager
        approval_workflow = self.deps.approval_workflow
        node_discovery = self.deps.node_discovery
        node_recommender = self.deps.node_recommender
        
        # Advanced Drift Detection
        if name == "get_drift_root_cause":
            return await self._get_drift_root_cause(arguments, n8n_client)
            
        elif name == "get_drift_fix_suggestions":
            return await self._get_drift_fix_suggestions(arguments, n8n_client)
            
        elif name == "detect_schema_drift":
            return await self._detect_schema_drift(arguments, n8n_client)
            
        elif name == "detect_rate_limit_drift":
            return await self._detect_rate_limit_drift(arguments, n8n_client)
            
        elif name == "detect_quality_drift":
            return await self._detect_quality_drift(arguments, n8n_client)
        
        # Workflow Analysis
        elif name == "trace_data_flow":
            return await self._trace_data_flow(arguments, n8n_client)
            
        elif name == "map_dependencies":
            return await self._map_dependencies(arguments, n8n_client)
            
        elif name == "simulate_workflow_changes":
            return await self._simulate_workflow_changes(arguments, n8n_client)
        
        # Change Management
        elif name == "create_change_request":
            return await self._create_change_request(arguments, approval_workflow)
            
        elif name == "review_change_request":
            return await self._review_change_request(arguments, approval_workflow)
            
        elif name == "get_change_history":
            return await self._get_change_history(arguments, approval_workflow)
        
        # Migration & Utilities
        elif name == "get_available_migrations":
            return await self._get_available_migrations(arguments)
            
        elif name == "generate_workflow_template":
            return await self._generate_workflow_template(arguments, workflow_builder)
            
        elif name == "debug_workflow_error":
            return await self._debug_workflow_error(arguments)
        
        # Node Search
        elif name == "search_nodes":
            return await self._search_nodes(arguments, node_discovery)
            
        elif name == "recommend_nodes_for_task":
            return await self._recommend_nodes_for_task(arguments, node_discovery, node_recommender)
        
        raise ValueError(f"Unknown miscellaneous tool: {name}")

    # Advanced Drift Detection Methods
    async def _get_drift_root_cause(self, arguments: dict, n8n_client) -> list[TextContent]:
        from ..drift import DriftDetector, DriftRootCauseAnalyzer
        
        workflow_id = arguments["workflow_id"]
        lookback_days = arguments.get("lookback_days", 30)
        
        workflow = await n8n_client.get_workflow(workflow_id)
        executions = await n8n_client.get_executions(workflow_id, limit=100)
        
        drift_analysis = DriftDetector.analyze_execution_history(executions)
        
        if not drift_analysis.get("drift_detected"):
            return [TextContent(
                type="text",
                text="ℹ️ No drift detected - root cause analysis not applicable"
            )]
        
        root_cause = DriftRootCauseAnalyzer.analyze_root_cause(
            drift_analysis, executions, workflow
        )
        
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

    async def _get_drift_fix_suggestions(self, arguments: dict, n8n_client) -> list[TextContent]:
        from ..drift import DriftDetector, DriftRootCauseAnalyzer, DriftFixSuggester
        
        workflow_id = arguments["workflow_id"]
        
        workflow = await n8n_client.get_workflow(workflow_id)
        executions = await n8n_client.get_executions(workflow_id, limit=100)
        
        drift_analysis = DriftDetector.analyze_execution_history(executions)
        
        if not drift_analysis.get("drift_detected"):
            return [TextContent(
                type="text",
                text="ℹ️ No drift detected - no fixes needed"
            )]
        
        root_cause = DriftRootCauseAnalyzer.analyze_root_cause(
            drift_analysis, executions, workflow
        )
        
        patterns = drift_analysis.get("patterns", [])
        suggestions = DriftFixSuggester.suggest_fixes(root_cause, workflow, patterns)
        
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

    async def _detect_schema_drift(self, arguments: dict, n8n_client) -> list[TextContent]:
        from ..drift import SchemaDriftAnalyzer
        
        workflow_id = arguments["workflow_id"]
        lookback_days = arguments.get("lookback_days", 30)
        
        workflow = await n8n_client.get_workflow(workflow_id)
        executions = await n8n_client.get_executions(workflow_id, limit=100)
        
        if not executions or len(executions) < 2:
            return [TextContent(
                type="text",
                text=f"ℹ️ Insufficient execution history for schema drift detection (need at least 2 executions)"
            )]
        
        drift_analysis = SchemaDriftAnalyzer.analyze_schema_drift(executions)
        
        result = f"# Schema Drift Detection: {workflow['name']}\n\n"
        
        if not drift_analysis.get("drift_detected"):
            result += "✅ **No schema drift detected**\n\n"
            result += "API response schemas appear stable.\n"
            return [TextContent(type="text", text=result)]
        
        severity = drift_analysis.get("severity", "info")
        severity_emoji = {"critical": "🔴", "warning": "⚠️", "info": "ℹ️"}.get(severity, "ℹ️")
        
        result += f"{severity_emoji} **Schema Drift Detected - Severity: {severity.upper()}**\n\n"
        
        summary = drift_analysis.get("summary", {})
        result += "## Summary\n\n"
        result += f"- Missing fields: {summary.get('missing_fields', 0)}\n"
        result += f"- New fields: {summary.get('new_fields', 0)}\n"
        result += f"- Type changes: {summary.get('type_changes', 0)}\n"
        result += f"- Null rate increases: {summary.get('null_rate_increases', 0)}\n\n"
        
        patterns = drift_analysis.get("patterns", [])
        if patterns:
            result += "## 🔍 Detected Changes\n\n"
            for pattern in patterns[:10]:
                severity_icon = {"critical": "🔴", "warning": "⚠️", "info": "ℹ️"}.get(pattern.get("severity"), "ℹ️")
                result += f"{severity_icon} **{pattern.get('type')}**\n"
                result += f"- {pattern.get('description')}\n\n"
        
        fixes = SchemaDriftAnalyzer.suggest_schema_fixes(drift_analysis, workflow)
        if fixes:
            result += "## 💡 Suggested Fixes\n\n"
            for fix in fixes[:5]:
                result += f"- {fix.get('suggestion')}\n"
        
        return [TextContent(type="text", text=result)]

    async def _detect_rate_limit_drift(self, arguments: dict, n8n_client) -> list[TextContent]:
        from ..drift import RateLimitDriftAnalyzer
        
        workflow_id = arguments["workflow_id"]
        lookback_days = arguments.get("lookback_days", 30)
        
        workflow = await n8n_client.get_workflow(workflow_id)
        executions = await n8n_client.get_executions(workflow_id, limit=100)
        
        if not executions or len(executions) < 2:
            return [TextContent(
                type="text",
                text=f"ℹ️ Insufficient execution history for rate limit drift detection (need at least 2 executions)"
            )]
        
        drift_analysis = RateLimitDriftAnalyzer.analyze_rate_limit_drift(executions, workflow)
        
        result = f"# Rate Limit Drift Detection: {workflow['name']}\n\n"
        
        if not drift_analysis.get("drift_detected"):
            result += "✅ **No rate limit issues detected**\n\n"
            result += "Workflow throughput and API limits appear stable.\n"
            return [TextContent(type="text", text=result)]
        
        severity = drift_analysis.get("severity", "info")
        severity_emoji = {"critical": "🔴", "warning": "⚠️", "info": "ℹ️"}.get(severity, "ℹ️")
        
        result += f"{severity_emoji} **Rate Limit Issues Detected - Severity: {severity.upper()}**\n\n"
        
        baseline = drift_analysis.get("baseline_period", {})
        current = drift_analysis.get("current_period", {})
        
        result += "## Metrics Comparison\n\n"
        result += f"**Rate Limit Errors:**\n"
        result += f"- Baseline: {baseline.get('rate_limit_errors', 0)} errors\n"
        result += f"- Current: {current.get('rate_limit_errors', 0)} errors\n\n"
        
        result += f"**Throughput:**\n"
        result += f"- Baseline: {baseline.get('throughput_per_hour', 0):.1f} exec/hour\n"
        result += f"- Current: {current.get('throughput_per_hour', 0):.1f} exec/hour\n\n"
        
        patterns = drift_analysis.get("patterns", [])
        if patterns:
            result += "## 🔍 Detected Issues\n\n"
            for pattern in patterns:
                severity_icon = {"critical": "🔴", "warning": "⚠️", "info": "ℹ️"}.get(pattern.get("severity"), "ℹ️")
                result += f"{severity_icon} **{pattern.get('type')}**\n"
                result += f"- {pattern.get('description')}\n\n"
        
        fixes = RateLimitDriftAnalyzer.suggest_rate_limit_fixes(drift_analysis, workflow)
        if fixes:
            result += "## 💡 Suggested Fixes\n\n"
            for fix in fixes[:5]:
                result += f"- {fix.get('suggestion')}\n"
        
        return [TextContent(type="text", text=result)]

    async def _detect_quality_drift(self, arguments: dict, n8n_client) -> list[TextContent]:
        from ..drift import DataQualityDriftAnalyzer
        
        workflow_id = arguments["workflow_id"]
        lookback_days = arguments.get("lookback_days", 30)
        
        workflow = await n8n_client.get_workflow(workflow_id)
        executions = await n8n_client.get_executions(workflow_id, limit=100)
        
        if not executions or len(executions) < 2:
            return [TextContent(
                type="text",
                text=f"ℹ️ Insufficient execution history for quality drift detection (need at least 2 executions)"
            )]
        
        drift_analysis = DataQualityDriftAnalyzer.analyze_quality_drift(executions)
        
        result = f"# Data Quality Drift Detection: {workflow['name']}\n\n"
        
        if not drift_analysis.get("drift_detected"):
            result += "✅ **No data quality issues detected**\n\n"
            result += "Data quality appears stable.\n"
            return [TextContent(type="text", text=result)]
        
        severity = drift_analysis.get("severity", "info")
        severity_emoji = {"critical": "🔴", "warning": "⚠️", "info": "ℹ️"}.get(severity, "ℹ️")
        
        result += f"{severity_emoji} **Quality Issues Detected - Severity: {severity.upper()}**\n\n"
        
        summary = drift_analysis.get("summary", {})
        result += "## Summary\n\n"
        result += f"- Empty value issues: {summary.get('empty_value_issues', 0)}\n"
        result += f"- Completeness issues: {summary.get('completeness_issues', 0)}\n"
        result += f"- Format validation issues: {summary.get('format_issues', 0)}\n"
        result += f"- Consistency issues: {summary.get('consistency_issues', 0)}\n\n"
        
        baseline = drift_analysis.get("baseline_period", {})
        current = drift_analysis.get("current_period", {})
        
        result += "## Quality Metrics\n\n"
        result += f"**Completeness:**\n"
        result += f"- Baseline: {baseline.get('completeness', 0):.1%}\n"
        result += f"- Current: {current.get('completeness', 0):.1%}\n\n"
        
        result += f"**Avg Output Size:**\n"
        result += f"- Baseline: {baseline.get('avg_output_size', 0):.1f} items\n"
        result += f"- Current: {current.get('avg_output_size', 0):.1f} items\n\n"
        
        patterns = drift_analysis.get("patterns", [])
        if patterns:
            result += "## 🔍 Detected Issues\n\n"
            for pattern in patterns[:10]:
                severity_icon = {"critical": "🔴", "warning": "⚠️", "info": "ℹ️"}.get(pattern.get("severity"), "ℹ️")
                result += f"{severity_icon} **{pattern.get('type')}**\n"
                result += f"- {pattern.get('description')}\n\n"
        
        fixes = DataQualityDriftAnalyzer.suggest_quality_fixes(drift_analysis, workflow)
        if fixes:
            result += "## 💡 Suggested Fixes\n\n"
            for fix in fixes[:5]:
                result += f"- {fix.get('suggestion')}\n"
        
        return [TextContent(type="text", text=result)]

    # Workflow Analysis Methods
    async def _trace_data_flow(self, arguments: dict, n8n_client) -> list[TextContent]:
        from ..analysis import DataFlowTracer
        
        workflow_id = arguments["workflow_id"]
        
        workflow = await n8n_client.get_workflow(workflow_id)
        if isinstance(workflow, list):
            workflow = workflow[0] if workflow else {}
        
        data_flow = DataFlowTracer.trace_data_flow(workflow)
        
        result = f"# Data Flow: {workflow['name']}\n\n"
        result += f"**Summary**: {data_flow.get('summary')}\n\n"
        
        input_sources = data_flow.get("input_sources", [])
        if input_sources:
            result += "## Input Sources\n\n"
            for source in input_sources:
                result += f"- **{source['node_name']}**: {source['source_type']}\n"
                details = source.get('details', {})
                if details.get('url'):
                    result += f"  - URL: `{details['url']}`\n"
            result += "\n"
        
        transformations = data_flow.get("transformations", [])
        if transformations:
            result += "## Transformations\n\n"
            for trans in transformations:
                result += f"- **{trans['node_name']}**: {trans['transformation_type']}\n"
            result += "\n"
        
        output_destinations = data_flow.get("output_destinations", [])
        if output_destinations:
            result += "## Output Destinations\n\n"
            for dest in output_destinations:
                result += f"- **{dest['node_name']}**: {dest['sink_type']}\n"
            result += "\n"
        
        critical_paths = data_flow.get("critical_paths", [])
        if critical_paths:
            result += "## Critical Data Paths\n\n"
            for idx, path in enumerate(critical_paths[:5], 1):
                path_str = " → ".join(path['path'])
                result += f"{idx}. {path_str}\n"
        
        return [TextContent(type="text", text=result)]

    async def _map_dependencies(self, arguments: dict, n8n_client) -> list[TextContent]:
        from ..analysis import DependencyMapper
        
        workflow_id = arguments["workflow_id"]
        
        workflow = await n8n_client.get_workflow(workflow_id)
        all_workflows = await n8n_client.get_workflows()
        
        dependencies = DependencyMapper.map_dependencies(workflow, all_workflows)
        
        result = f"# Dependencies: {workflow['name']}\n\n"
        result += f"**Summary**: {dependencies.get('summary')}\n\n"
        
        internal_deps = dependencies.get("internal_dependencies", [])
        if internal_deps:
            result += "## Internal Dependencies\n\n"
            for dep in internal_deps:
                if dep["type"] == "workflow_call":
                    result += f"- Calls workflow: **{dep['target_workflow_name']}**\n"
                    result += f"  - Node: `{dep['node_name']}`\n"
                    result += f"  - Criticality: {dep['criticality']}\n"
            result += "\n"
        
        external_deps = dependencies.get("external_dependencies", [])
        if external_deps:
            result += "## External Dependencies\n\n"
            for dep in external_deps:
                result += f"- **{dep['service_name']}** ({dep.get('service_type', 'unknown')})\n"
                if dep.get('endpoint'):
                    result += f"  - Endpoint: `{dep['endpoint']}`\n"
            result += "\n"
        
        credentials = dependencies.get("credentials", [])
        if credentials:
            result += "## Credentials\n\n"
            for cred in credentials:
                result += f"- **{cred['credential_name']}** ({cred['credential_type']})\n"
                result += f"  - Criticality: {cred['criticality']}\n"
                result += f"  - Used by: {', '.join(cred['used_by_nodes'])}\n"
            result += "\n"
        
        spofs = dependencies.get("single_points_of_failure", [])
        if spofs:
            result += "## ⚠️ Single Points of Failure\n\n"
            for spof in spofs:
                result += f"- **{spof.get('type')}** (Severity: {spof.get('severity')})\n"
                result += f"  - {spof.get('impact')}\n"
        
        return [TextContent(type="text", text=result)]

    async def _simulate_workflow_changes(self, arguments: dict, n8n_client) -> list[TextContent]:
        from ..analysis.simulator import ChangeSimulator
        
        workflow_id = arguments["workflow_id"]
        new_workflow = arguments["new_workflow"]
        
        # Initialize simulator with client
        simulator = ChangeSimulator(n8n_client)
        
        # Run simulation
        simulation = await simulator.simulate(workflow_id, new_workflow)
        
        # Format as Terraform-style output
        result = simulator.format_terraform_style(simulation)
        
        # Add additional details
        if simulation.get('breaking_changes'):
            result += "\n## 🚨 Action Required\n\n"
            result += "Review breaking changes carefully before applying!\n"
        
        return [TextContent(type="text", text=result)]

    # Change Management Methods
    async def _create_change_request(self, arguments: dict, approval_workflow) -> list[TextContent]:
        workflow_id = arguments["workflow_id"]
        workflow_name = arguments["workflow_name"]
        changes = arguments["changes"]
        reason = arguments["reason"]
        requester = arguments["requester"]
        
        request = approval_workflow.create_request(
            workflow_id, workflow_name, changes, reason, requester
        )
        
        result = f"# Change Request Created\n\n"
        result += f"**Request ID**: {request.id}\n"
        result += f"**Workflow**: {request.workflow_name} ({request.workflow_id})\n"
        result += f"**Status**: {request.status}\n"
        result += f"**Requester**: {request.requester}\n"
        result += f"**Reason**: {request.reason}\n"
        result += f"**Created**: {request.created_at}\n\n"
        result += "✅ Request created successfully. Use `review_change_request` to approve or reject.\n"
        
        return [TextContent(type="text", text=result)]

    async def _review_change_request(self, arguments: dict, approval_workflow) -> list[TextContent]:
        request_id = arguments["request_id"]
        action = arguments["action"]
        reviewer = arguments["reviewer"]
        comments = arguments.get("comments", "")
        
        if action == "approve":
            response = approval_workflow.approve_request(request_id, reviewer, comments)
        elif action == "reject":
            response = approval_workflow.reject_request(request_id, reviewer, comments)
        else:
            return [TextContent(type="text", text=f"Invalid action: {action}. Must be 'approve' or 'reject'.")]
        
        if not response["success"]:
            return [TextContent(type="text", text=f"❌ Error: {response['error']}")]
        
        request_data = response["request"]
        result = f"# Change Request {'Approved' if action == 'approve' else 'Rejected'}\n\n"
        result += f"**Request ID**: {request_data['id']}\n"
        result += f"**Workflow**: {request_data['workflow_name']}\n"
        result += f"**Status**: {request_data['status']}\n"
        result += f"**Reviewer**: {request_data['reviewer']}\n"
        result += f"**Reviewed**: {request_data['reviewed_at']}\n"
        
        if request_data.get("review_comments"):
            result += f"**Comments**: {request_data['review_comments']}\n"
        
        if action == "approve":
            result += "\n✅ Request approved. You can now apply the changes to the workflow.\n"
        else:
            result += "\n❌ Request rejected. Changes will not be applied.\n"
        
        return [TextContent(type="text", text=result)]

    async def _get_change_history(self, arguments: dict, approval_workflow) -> list[TextContent]:
        workflow_id = arguments["workflow_id"]
        
        history = approval_workflow.get_workflow_history(workflow_id)
        
        if not history:
            return [TextContent(type="text", text=f"No change history found for workflow {workflow_id}")]
        
        result = f"# Change History\n\n"
        result += f"**Total Requests**: {len(history)}\n\n"
        
        status_groups = {}
        for req in history:
            status = req["status"]
            if status not in status_groups:
                status_groups[status] = []
            status_groups[status].append(req)
        
        result += "**Status Summary**:\n"
        for status, requests in status_groups.items():
            result += f"  - {status}: {len(requests)}\n"
        result += "\n"
        
        result += "## Recent Changes\n\n"
        for req in sorted(history, key=lambda x: x["created_at"], reverse=True)[:10]:
            status_icon = {
                "pending": "⏳",
                "approved": "✅",
                "rejected": "❌",
                "applied": "✔️",
                "failed": "⚠️"
            }.get(req["status"], "❓")
            
            result += f"### {status_icon} Request {req['id']}\n"
            result += f"- **Status**: {req['status']}\n"
            result += f"- **Requester**: {req['requester']}\n"
            result += f"- **Reason**: {req['reason']}\n"
            result += f"- **Created**: {req['created_at']}\n"
            
            if req.get("reviewer"):
                result += f"- **Reviewer**: {req['reviewer']}\n"
            if req.get("reviewed_at"):
                result += f"- **Reviewed**: {req['reviewed_at']}\n"
            if req.get("review_comments"):
                result += f"- **Comments**: {req['review_comments']}\n"
            
            result += "\n"
        
        return [TextContent(type="text", text=result)]

    # Migration & Utility Methods
    async def _get_available_migrations(self, arguments: dict) -> list[TextContent]:
        from ..migration.migration_rules import get_rules_for_node
        
        node_type = arguments["node_type"]
        
        rules = get_rules_for_node(node_type)
        
        if not rules:
            return [TextContent(type="text", text=f"No migration rules found for node type: {node_type}")]
        
        result = f"# Available Migrations for {node_type}\n\n"
        result += f"**Total Rules:** {len(rules)}\n\n"
        
        for rule in rules:
            result += f"## {rule.name}\n"
            result += f"- **ID:** `{rule.rule_id}`\n"
            result += f"- **Version:** {rule.from_version} → {rule.to_version}\n"
            result += f"- **Severity:** {rule.severity}\n"
            result += f"- **Description:** {rule.description}\n"
            result += "\n"
        
        return [TextContent(type="text", text=result)]

    async def _generate_workflow_template(self, arguments: dict, workflow_builder) -> list[TextContent]:
        from ..templates import WORKFLOW_TEMPLATES
        
        description = arguments["description"]
        template_type = arguments.get("template_type", "custom")
        
        suggestions = workflow_builder.suggest_nodes(description)
        outline = workflow_builder.generate_workflow_outline(description, suggestions)
        
        if template_type in WORKFLOW_TEMPLATES:
            template = WORKFLOW_TEMPLATES[template_type]
            outline += f"\n## Template: {template['name']}\n\n"
            outline += "Recommended Node Structure:\n"
            for i, node in enumerate(template['nodes'], 1):
                outline += f"{i}. {node['name']} ({node['type']})\n"
        
        return [TextContent(type="text", text=outline)]

    async def _debug_workflow_error(self, arguments: dict) -> list[TextContent]:
        error_msg = arguments["error_message"]
        node_type = arguments.get("node_type", "").lower()
        
        debug_info = f"# Workflow Error Debug\n\n"
        debug_info += f"**Error Message:** {error_msg}\n\n"
        
        if "timeout" in error_msg.lower():
            debug_info += "## Probable Cause: Timeout\n\n"
            debug_info += "**Solutions:**\n"
            debug_info += "- Increase timeout setting in node configuration\n"
            debug_info += "- Check if external service is responding slowly\n"
            debug_info += "- Add retry logic\n"
        
        elif "authentication" in error_msg.lower() or "401" in error_msg:
            debug_info += "## Probable Cause: Authentication Error\n\n"
            debug_info += "**Solutions:**\n"
            debug_info += "- Check credentials are correct\n"
            debug_info += "- Verify API key hasn't expired\n"
            debug_info += "- Ensure correct authentication method\n"
        
        elif "404" in error_msg:
            debug_info += "## Probable Cause: Resource Not Found\n\n"
            debug_info += "**Solutions:**\n"
            debug_info += "- Verify URL is correct\n"
            debug_info += "- Check if resource ID exists\n"
            debug_info += "- Confirm API endpoint path\n"
        
        elif "rate limit" in error_msg.lower() or "429" in error_msg:
            debug_info += "## Probable Cause: Rate Limiting\n\n"
            debug_info += "**Solutions:**\n"
            debug_info += "- Add delay between requests\n"
            debug_info += "- Implement exponential backoff\n"
            debug_info += "- Batch requests if possible\n"
        
        else:
            debug_info += "## Generic Troubleshooting Steps:\n\n"
            debug_info += "- Check node configuration\n"
            debug_info += "- Verify input data format\n"
            debug_info += "- Review execution logs\n"
            debug_info += "- Test with minimal data\n"
        
        return [TextContent(type="text", text=debug_info)]

    # Node Search Methods
    async def _search_nodes(self, arguments: dict, node_discovery) -> list[TextContent]:
        query = arguments["query"]
        
        matches = node_discovery.search_nodes(query)
        
        if not matches:
            return [TextContent(
                type="text",
                text=f"❌ No nodes found matching '{query}'.\n\n"
                     f"💡 Tips:\n"
                     f"- Try different keywords\n"
                     f"- Run `discover_nodes` to update node knowledge\n"
                     f"- Use `recommend_nodes_for_task` for task-based recommendations"
            )]
        
        result = f"# 🔎 Search Results for '{query}' ({len(matches)} matches)\n\n"
        
        category_icons = {
            'trigger': '⚡',
            'data_source': '📊',
            'transform': '🔄',
            'notification': '📬',
            'http': '🌐',
            'logic': '🔀',
            'utility': '🔧',
            'other': '📦'
        }
        
        for match in matches:
            category = match.get('category', 'other')
            icon = category_icons.get(category, '📦')
            result += f"## {icon} {match['name'] or match['type']}\n"
            result += f"- **Type:** `{match['type']}`\n"
            result += f"- **Category:** {category}\n"
            result += f"- **Usage Count:** {match['usage_count']} times\n"
            result += f"- **Parameters:** {match['parameters']} discovered\n"
            result += f"- **Version:** {match['typeVersion']}\n"
            result += "\n"
        
        result += f"💡 **Tip:** Use `get_node_schema('{matches[0]['type']}')` to see detailed parameters.\n"
        
        return [TextContent(type="text", text=result)]

    async def _recommend_nodes_for_task(self, arguments: dict, node_discovery, node_recommender) -> list[TextContent]:
        from ..discovery.recommender import NodeRecommender
        
        task_description = arguments["task_description"]
        top_k = arguments.get("top_k", 5)
        
        if node_recommender is None:
            if not node_discovery.discovered_nodes:
                return [TextContent(
                    type="text",
                    text=f"❌ No nodes discovered yet.\n\n"
                         f"💡 Run `discover_nodes` first to analyze workflows and build recommendations."
                )]
            node_recommender = NodeRecommender(node_discovery)
        
        # Call async recommend_for_task
        recommendations = await node_recommender.recommend_for_task(task_description, top_k)
        
        if not recommendations:
            return [TextContent(
                type="text",
                text=f"❌ No recommendations found for: '{task_description}'\n\n"
                     f"💡 Try:\n"
                     f"- More descriptive task description\n"
                     f"- Different keywords\n"
                     f"- Run `search_nodes` to browse available nodes"
            )]
        
        result = f"# 💡 Node Recommendations for Task\n\n"
        result += f"**Task:** {task_description}\n"
        result += f"**Found:** {len(recommendations)} matching nodes\n\n"
        
        for i, (node_type, score, reason) in enumerate(recommendations, 1):
            result += f"## {i}. {node_type}\n"
            result += f"- **Type:** `{node_type}`\n"
            result += f"- **Score:** {score:.1f}\n"
            result += f"- **Reason:** {reason}\n"
            result += "\n"
        
        result += f"💡 **Next Steps:**\n"
        result += f"- Use `get_node_schema('{recommendations[0][0]}')` to see parameters\n"
        result += f"- Use `generate_workflow_template` to create a workflow with these nodes\n"
        
        return [TextContent(type="text", text=result)]
