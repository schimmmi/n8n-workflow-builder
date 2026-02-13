#!/usr/bin/env python3
"""
Execution & Monitoring Tool Handlers
Handles workflow execution tracking, error analysis, and execution monitoring
"""
from typing import Any, TYPE_CHECKING
import json

from mcp.types import TextContent

from .base import BaseTool, ToolError
from ..execution.error_analyzer import ExecutionMonitor, ErrorSimplifier, ErrorContextExtractor, FeedbackGenerator

if TYPE_CHECKING:
    from ..dependencies import Dependencies


class ExecutionTools(BaseTool):
    """Handler for execution monitoring and error analysis tools"""
    
    async def handle(self, name: str, arguments: dict) -> list[TextContent]:
        """Route execution tool calls to appropriate handler methods
        
        Args:
            name: Tool name
            arguments: Tool arguments
            
        Returns:
            List of TextContent responses
        """
        handlers = {
            "get_executions": self.get_executions,
            "get_execution_details": self.get_execution_details,
            "watch_workflow_execution": self.watch_workflow_execution,
            "get_execution_error_context": self.get_execution_error_context,
            "analyze_execution_errors": self.analyze_execution_errors,
        }
        
        handler = handlers.get(name)
        if not handler:
            raise ToolError("UNKNOWN_TOOL", f"Tool '{name}' not found in execution tools")
        
        return await handler(arguments)
    
    async def get_executions(self, arguments: dict) -> list[TextContent]:
        """Get recent executions for a workflow"""
        workflow_id = arguments.get("workflow_id")
        limit = arguments.get("limit", 10)
        
        executions = await self.deps.client.get_executions(workflow_id, limit)
        
        result = f"# Recent Executions ({len(executions)})\n\n"
        for exec in executions:
            status = "✅" if exec.get('finished') else "⏳"
            result += f"{status} **Execution {exec['id']}**\n"
            result += f"   Workflow: {exec.get('workflowData', {}).get('name', 'N/A')}\n"
            result += f"   Started: {exec.get('startedAt', 'N/A')}\n"
            if exec.get('stoppedAt'):
                result += f"   Duration: {exec.get('stoppedAt', 'N/A')}\n"
            result += "\n"
        
        return [TextContent(type="text", text=result)]
    
    async def get_execution_details(self, arguments: dict) -> list[TextContent]:
        """Get detailed information about a specific execution"""
        execution_id = arguments["execution_id"]
        
        execution = await self.deps.client.get_execution(execution_id)
        
        result = f"# Execution Details: {execution_id}\n\n"
        result += f"**Workflow:** {execution.get('workflowData', {}).get('name', 'N/A')}\n"
        result += f"**Status:** {'✅ Finished' if execution.get('finished') else '⏳ Running'}\n"
        result += f"**Started:** {execution.get('startedAt', 'N/A')}\n"
        
        if execution.get('stoppedAt'):
            result += f"**Stopped:** {execution.get('stoppedAt', 'N/A')}\n"
        
        if execution.get('mode'):
            result += f"**Mode:** {execution.get('mode')}\n"
        
        # Show node execution data
        exec_data = execution.get('data', {})
        result_data = exec_data.get('resultData', {})
        run_data = result_data.get('runData', {}) if result_data else {}
        
        if run_data:
            result += "\n## Node Results:\n\n"
            for node_name, node_runs in run_data.items():
                result += f"### {node_name}\n"
                for idx, run in enumerate(node_runs):
                    result += f"**Run {idx + 1}:**\n"
                    if 'data' in run:
                        main_data = run['data'].get('main', [[]])[0]
                        if main_data:
                            result += f"- Output items: {len(main_data)}\n"
                            # Show first item as sample
                            if main_data and len(main_data) > 0:
                                first_item = main_data[0]
                                result += f"- Sample data: `{json.dumps(first_item.get('json', {}), indent=2)[:500]}...`\n"
                    if 'error' in run:
                        result += f"- ❌ Error: {run['error'].get('message', 'Unknown error')}\n"
                result += "\n"
        else:
            result += "\n⚠️ **No node execution data available.**\n\n"
            result += "This can happen if:\n"
            result += "- n8n is configured to not save execution data (check Settings > Executions)\n"
            result += "- The execution data has been pruned/deleted\n"
            result += "- The workflow hasn't been executed yet\n\n"
            result += "To see execution data, ensure 'Save manual executions' and 'Save execution progress' are enabled in n8n settings.\n"
        
        return [TextContent(type="text", text=result)]
    
    async def watch_workflow_execution(self, arguments: dict) -> list[TextContent]:
        """Monitor a workflow execution and report status/errors"""
        workflow_id = arguments["workflow_id"]
        execution_id = arguments.get("execution_id")
        
        # Fetch workflow
        workflow = await self.deps.client.get_workflow(workflow_id)
        
        # Get execution - either specific ID or most recent
        if execution_id:
            execution = await self.deps.client.get_execution(execution_id)
        else:
            # Get most recent execution for this workflow
            executions = await self.deps.client.get_executions(workflow_id, limit=1)
            if not executions or len(executions) == 0:
                return [TextContent(
                    type="text",
                    text=f"ℹ️ No executions found for workflow: {workflow['name']}"
                )]
            execution = executions[0]
            execution_id = execution["id"]
        
        # Analyze execution
        analysis = ExecutionMonitor.analyze_execution(execution, workflow)
        
        # Log action
        self.deps.state_manager.log_action("watch_workflow_execution", {
            "workflow_id": workflow_id,
            "execution_id": execution_id,
            "has_errors": analysis["has_errors"]
        })
        
        # Format result
        result = f"# Execution Monitor: {analysis['workflow_name']}\n\n"
        result += f"**Execution ID**: `{execution_id}`\n"
        result += f"**Status**: {'❌ Failed' if analysis['has_errors'] else '✅ Success'}\n"
        result += f"**Mode**: {analysis['mode']}\n"
        
        if analysis['started_at']:
            result += f"**Started**: {analysis['started_at']}\n"
        if analysis['stopped_at']:
            result += f"**Stopped**: {analysis['stopped_at']}\n"
        if analysis['duration_ms']:
            result += f"**Duration**: {analysis['duration_ms']}ms\n"
        
        result += "\n"
        
        if analysis["has_errors"]:
            result += "## ❌ Errors Detected\n\n"
            for error_node in analysis["error_nodes"]:
                node_name = error_node["node_name"]
                error = error_node["error"]
                
                # Simplify error
                simplified = ErrorSimplifier.simplify_error(error)
                
                result += f"### Node: {node_name}\n\n"
                result += f"**Error Type**: `{simplified['error_type']}`\n"
                result += f"**Message**: {simplified['simplified_message']}\n\n"
            
            result += f"---\n\n"
            result += f"💡 **Tip**: Use `get_execution_error_context` with execution_id `{execution_id}` "
            result += f"to get detailed error analysis and fix suggestions.\n"
        else:
            result += "✅ Execution completed successfully with no errors.\n"
        
        return [TextContent(type="text", text=result)]
    
    async def get_execution_error_context(self, arguments: dict) -> list[TextContent]:
        """Get detailed error context and fix suggestions for a failed execution"""
        execution_id = arguments["execution_id"]
        workflow_id = arguments["workflow_id"]
        
        # Fetch workflow and execution
        workflow = await self.deps.client.get_workflow(workflow_id)
        execution = await self.deps.client.get_execution(execution_id)
        
        # Analyze execution to find error nodes
        analysis = ExecutionMonitor.analyze_execution(execution, workflow)
        
        if not analysis["has_errors"]:
            return [TextContent(
                type="text",
                text=f"ℹ️ Execution {execution_id} completed successfully - no errors to analyze"
            )]
        
        if not analysis["error_nodes"] or len(analysis["error_nodes"]) == 0:
            return [TextContent(
                type="text",
                text=f"⚠️ Execution failed but no specific error node could be identified"
            )]
        
        # Get first error node (most common case)
        error_node_info = analysis["error_nodes"][0]
        error_node_name = error_node_info["node_name"]
        
        # Extract full error context
        error_context = ErrorContextExtractor.extract_error_context(
            execution, workflow, error_node_name
        )
        
        # Simplify error
        simplified_error = ErrorSimplifier.simplify_error(
            error_context["error_details"]
        )
        
        # Generate feedback
        feedback = FeedbackGenerator.generate_feedback(
            error_context, simplified_error
        )
        
        # Format for LLM
        result = FeedbackGenerator.format_feedback_for_llm(feedback)
        
        # Log action
        self.deps.state_manager.log_action("get_execution_error_context", {
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "error_node": error_node_name,
            "error_type": simplified_error["error_type"]
        })
        
        return [TextContent(type="text", text=result)]
    
    async def analyze_execution_errors(self, arguments: dict) -> list[TextContent]:
        """Analyze error patterns across multiple executions"""
        workflow_id = arguments["workflow_id"]
        limit = arguments.get("limit", 10)
        
        # Fetch workflow
        workflow = await self.deps.client.get_workflow(workflow_id)
        
        # Get recent executions
        executions = await self.deps.client.get_executions(workflow_id, limit=limit)
        
        if not executions or len(executions) == 0:
            return [TextContent(
                type="text",
                text=f"ℹ️ No executions found for workflow: {workflow['name']}"
            )]
        
        # Analyze all executions
        error_patterns = {}
        failed_count = 0
        success_count = 0
        
        for execution in executions:
            analysis = ExecutionMonitor.analyze_execution(execution, workflow)
            
            if analysis["has_errors"]:
                failed_count += 1
                
                for error_node in analysis["error_nodes"]:
                    node_name = error_node["node_name"]
                    error = error_node["error"]
                    simplified = ErrorSimplifier.simplify_error(error)
                    
                    # Track error patterns
                    key = f"{node_name}:{simplified['error_type']}"
                    if key not in error_patterns:
                        error_patterns[key] = {
                            "node_name": node_name,
                            "error_type": simplified['error_type'],
                            "message": simplified['simplified_message'],
                            "count": 0,
                            "execution_ids": []
                        }
                    error_patterns[key]["count"] += 1
                    error_patterns[key]["execution_ids"].append(execution["id"])
            else:
                success_count += 1
        
        # Format result
        result = f"# Execution Error Analysis: {workflow['name']}\n\n"
        result += f"**Total Executions Analyzed**: {len(executions)}\n"
        result += f"**Successful**: ✅ {success_count}\n"
        result += f"**Failed**: ❌ {failed_count}\n"
        result += f"**Success Rate**: {round(success_count / len(executions) * 100, 1)}%\n\n"
        
        if error_patterns:
            result += "## 🔥 Error Patterns\n\n"
            result += "Most common errors across executions:\n\n"
            
            # Sort by count
            sorted_patterns = sorted(
                error_patterns.values(),
                key=lambda x: x["count"],
                reverse=True
            )
            
            for pattern in sorted_patterns:
                result += f"### {pattern['node_name']}\n\n"
                result += f"**Error Type**: `{pattern['error_type']}`\n"
                result += f"**Message**: {pattern['message']}\n"
                result += f"**Occurrences**: {pattern['count']} times\n"
                result += f"**Execution IDs**: {', '.join(pattern['execution_ids'][:3])}"
                if len(pattern['execution_ids']) > 3:
                    result += f" (+{len(pattern['execution_ids']) - 3} more)"
                result += "\n\n"
            
            result += "---\n\n"
            result += "💡 **Recommendation**: Focus on fixing the most frequent errors first. "
            result += "Use `get_execution_error_context` for detailed fix suggestions.\n"
        else:
            result += "✅ No error patterns detected - all executions succeeded!\n"
        
        # Log action
        self.deps.state_manager.log_action("analyze_execution_errors", {
            "workflow_id": workflow_id,
            "executions_analyzed": len(executions),
            "failed_count": failed_count,
            "error_patterns": len(error_patterns)
        })
        
        return [TextContent(type="text", text=result)]
