#!/usr/bin/env python3
"""
Error Analysis and Execution Monitoring Module
Provides execution-aware feedback loop for workflow debugging
"""
import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime


class ExecutionMonitor:
    """Monitors workflow executions and detects errors"""

    @staticmethod
    def analyze_execution(execution: Dict, workflow: Dict) -> Dict:
        """Analyze an execution and extract error information

        Args:
            execution: Execution data from n8n API
            workflow: Workflow definition

        Returns:
            Analysis results with error detection
        """
        execution_id = execution.get("id", "unknown")
        status = execution.get("status", execution.get("finished", False))

        # Determine if execution failed
        has_errors = False
        error_nodes = []

        if status == "error" or status is False:
            has_errors = True
            error_nodes = ExecutionMonitor._extract_error_nodes(execution)

        # Calculate execution time
        started_at = execution.get("startedAt")
        stopped_at = execution.get("stoppedAt")
        duration_ms = None

        if started_at and stopped_at:
            try:
                start = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
                stop = datetime.fromisoformat(stopped_at.replace('Z', '+00:00'))
                duration_ms = int((stop - start).total_seconds() * 1000)
            except:
                pass

        return {
            "execution_id": execution_id,
            "workflow_id": execution.get("workflowId", "unknown"),
            "workflow_name": workflow.get("name", "Unknown"),
            "status": "error" if has_errors else "success",
            "has_errors": has_errors,
            "error_nodes": error_nodes,
            "started_at": started_at,
            "stopped_at": stopped_at,
            "duration_ms": duration_ms,
            "mode": execution.get("mode", "unknown"),
            "data": execution.get("data", {})
        }

    @staticmethod
    def _extract_error_nodes(execution: Dict) -> List[Dict]:
        """Extract nodes that failed during execution

        Args:
            execution: Execution data

        Returns:
            List of error node information
        """
        error_nodes = []
        data = execution.get("data", {})

        if not data:
            return error_nodes

        # Check resultData for errors
        result_data = data.get("resultData", {})
        if result_data:
            runs_data = result_data.get("runData", {})

            for node_name, runs in runs_data.items():
                if not runs or len(runs) == 0:
                    continue

                # Check last run of this node
                last_run = runs[-1]

                if "error" in last_run:
                    error_info = last_run["error"]
                    error_nodes.append({
                        "node_name": node_name,
                        "error": error_info,
                        "run_index": len(runs) - 1
                    })

        # Also check top-level error
        if "error" in data:
            top_error = data["error"]
            if "node" in top_error:
                error_nodes.append({
                    "node_name": top_error["node"].get("name", "Unknown"),
                    "error": top_error,
                    "run_index": 0
                })

        return error_nodes


class ErrorContextExtractor:
    """Extracts context around errors for better debugging"""

    @staticmethod
    def extract_error_context(
        execution: Dict,
        workflow: Dict,
        error_node_name: str
    ) -> Dict:
        """Extract full context for an error node

        Args:
            execution: Execution data
            workflow: Workflow definition
            error_node_name: Name of the node that failed

        Returns:
            Error context with all relevant information
        """
        # Find the node definition
        node_def = None
        for node in workflow.get("nodes", []):
            if node["name"] == error_node_name:
                node_def = node
                break

        if not node_def:
            return {
                "error": f"Node '{error_node_name}' not found in workflow"
            }

        # Extract error details from execution
        error_details = ErrorContextExtractor._get_error_details(
            execution, error_node_name
        )

        # Get input from previous nodes
        previous_output = ErrorContextExtractor._get_previous_node_output(
            execution, workflow, error_node_name
        )

        # Get intent metadata if available
        intent = None
        if "parameters" in node_def and "_intent" in node_def["parameters"]:
            intent = node_def["parameters"]["_intent"]

        return {
            "node_name": error_node_name,
            "node_type": node_def.get("type", "unknown"),
            "error_details": error_details,
            "node_parameters": node_def.get("parameters", {}),
            "previous_output": previous_output,
            "intent": intent,
            "position": node_def.get("position", [0, 0])
        }

    @staticmethod
    def _get_error_details(execution: Dict, node_name: str) -> Dict:
        """Get detailed error information for a node

        Args:
            execution: Execution data
            node_name: Node name

        Returns:
            Error details
        """
        data = execution.get("data", {})
        result_data = data.get("resultData", {})
        runs_data = result_data.get("runData", {})

        if node_name in runs_data:
            runs = runs_data[node_name]
            if runs and len(runs) > 0:
                last_run = runs[-1]
                if "error" in last_run:
                    return last_run["error"]

        # Check top-level error
        if "error" in data:
            return data["error"]

        return {"message": "No error details found"}

    @staticmethod
    def _get_previous_node_output(
        execution: Dict,
        workflow: Dict,
        node_name: str
    ) -> Optional[Dict]:
        """Get output from the previous node(s) in the workflow

        Args:
            execution: Execution data
            workflow: Workflow definition
            node_name: Current node name

        Returns:
            Previous node output or None
        """
        # Find incoming connections to this node
        connections = workflow.get("connections", {})
        previous_nodes = []

        for source_node, targets in connections.items():
            for output_type, output_connections in targets.items():
                for connection_list in output_connections:
                    for connection in connection_list:
                        if connection.get("node") == node_name:
                            previous_nodes.append(source_node)

        if not previous_nodes:
            return None

        # Get execution data for previous node
        data = execution.get("data", {})
        result_data = data.get("resultData", {})
        runs_data = result_data.get("runData", {})

        previous_output = {}
        for prev_node in previous_nodes:
            if prev_node in runs_data:
                runs = runs_data[prev_node]
                if runs and len(runs) > 0:
                    last_run = runs[-1]
                    if "data" in last_run:
                        previous_output[prev_node] = last_run["data"]

        return previous_output if previous_output else None


class ErrorSimplifier:
    """Simplifies complex error messages for LLM consumption"""

    # Common error patterns and their simplifications
    ERROR_PATTERNS = [
        # HTTP Errors
        (r"401|Unauthorized", "authentication", "API authentication failed (401 Unauthorized)"),
        (r"403|Forbidden", "permission", "API access forbidden (403 Forbidden)"),
        (r"404|Not Found", "not_found", "Resource not found (404)"),
        (r"429|Too Many Requests|rate limit", "rate_limit", "API rate limit exceeded (429)"),
        (r"500|Internal Server Error", "server_error", "API server error (500)"),
        (r"502|Bad Gateway", "gateway_error", "API gateway error (502)"),
        (r"503|Service Unavailable", "unavailable", "API service unavailable (503)"),
        (r"timeout|timed out", "timeout", "Request timed out"),

        # JSON Errors
        (r"JSON|json.*parse|parse.*json|unexpected token", "json_parse", "Failed to parse JSON response"),
        (r"invalid json", "json_invalid", "Invalid JSON format"),

        # Network Errors
        (r"ECONNREFUSED|connection refused", "connection_refused", "Connection refused - service not reachable"),
        (r"ENOTFOUND|DNS|getaddrinfo", "dns_error", "DNS resolution failed - domain not found"),
        (r"ETIMEDOUT|ESOCKETTIMEDOUT", "timeout", "Network timeout"),

        # Data Errors
        (r"undefined is not an object|cannot read.*undefined", "undefined_data", "Accessing undefined data"),
        (r"null.*reference", "null_reference", "Null reference error"),
        (r"required.*missing|missing.*required", "missing_field", "Required field is missing"),

        # Authentication
        (r"invalid.*credentials|invalid.*token|invalid.*key", "invalid_credentials", "Invalid credentials or API key"),
        (r"expired.*token|token.*expired", "expired_token", "Authentication token expired"),
    ]

    @staticmethod
    def simplify_error(error: Dict) -> Dict:
        """Simplify an error message for better LLM understanding

        Args:
            error: Raw error object

        Returns:
            Simplified error with category and message
        """
        raw_message = error.get("message", "Unknown error")

        # Try to match against known patterns
        error_type = "unknown"
        simplified_message = raw_message

        for pattern, err_type, simple_msg in ErrorSimplifier.ERROR_PATTERNS:
            if re.search(pattern, raw_message, re.IGNORECASE):
                error_type = err_type
                simplified_message = simple_msg
                break

        # Extract HTTP status code if present
        status_code = None
        status_match = re.search(r'\b(\d{3})\b', raw_message)
        if status_match:
            status_code = int(status_match.group(1))

        return {
            "error_type": error_type,
            "simplified_message": simplified_message,
            "raw_message": raw_message,
            "status_code": status_code,
            "timestamp": error.get("timestamp", datetime.now().isoformat())
        }


class FeedbackGenerator:
    """Generates actionable feedback for LLMs based on errors"""

    # Error-type specific suggestions
    SUGGESTIONS_MAP = {
        "authentication": [
            "Verify API key or credentials are correctly configured",
            "Check if authentication type matches API requirements (Basic, Bearer, OAuth, etc.)",
            "Ensure credentials have not expired",
            "Test authentication manually with a tool like curl or Postman"
        ],
        "permission": [
            "Check if API key has required permissions/scopes",
            "Verify account/user has access to this resource",
            "Review API documentation for required permissions"
        ],
        "not_found": [
            "Verify the resource ID or URL is correct",
            "Check if the resource exists in the target system",
            "Ensure base URL is correctly configured"
        ],
        "rate_limit": [
            "Add delay between requests",
            "Implement exponential backoff retry logic",
            "Check API rate limit documentation",
            "Consider upgrading API plan if available"
        ],
        "timeout": [
            "Increase timeout value in node settings",
            "Check if API endpoint is responding slowly",
            "Verify network connectivity",
            "Consider adding retry logic"
        ],
        "json_parse": [
            "Check if API is returning HTML error page instead of JSON",
            "Verify Content-Type header is set correctly",
            "Add error handling to parse non-JSON responses",
            "Check API documentation for correct response format"
        ],
        "connection_refused": [
            "Verify the service is running and accessible",
            "Check firewall rules and network connectivity",
            "Ensure correct hostname and port",
            "Check if service requires VPN or special network access"
        ],
        "missing_field": [
            "Check which field is required in API documentation",
            "Verify data from previous node contains expected fields",
            "Add data transformation to include missing fields",
            "Check if field name uses correct casing (camelCase vs snake_case)"
        ],
        "undefined_data": [
            "Check if previous node returned data",
            "Verify field path expression is correct",
            "Add conditional logic to handle missing data",
            "Check if array is empty before accessing items"
        ]
    }

    @staticmethod
    def generate_feedback(
        error_context: Dict,
        simplified_error: Dict
    ) -> Dict:
        """Generate comprehensive feedback for an error

        Args:
            error_context: Full error context from ErrorContextExtractor
            simplified_error: Simplified error from ErrorSimplifier

        Returns:
            Structured feedback for LLM
        """
        error_type = simplified_error["error_type"]
        node_name = error_context.get("node_name", "Unknown")
        node_type = error_context.get("node_type", "unknown")

        # Get suggestions based on error type
        suggestions = FeedbackGenerator.SUGGESTIONS_MAP.get(
            error_type,
            ["Review error message and node configuration",
             "Check API documentation",
             "Verify input data format"]
        )

        # Add node-type specific suggestions
        if node_type == "n8n-nodes-base.httpRequest":
            suggestions.insert(0, "Check HTTP method, URL, headers, and body format")
        elif "database" in node_type.lower():
            suggestions.insert(0, "Verify database connection string and credentials")

        # Build feedback structure
        feedback = {
            "summary": f"Error in node '{node_name}': {simplified_error['simplified_message']}",
            "node": {
                "name": node_name,
                "type": node_type,
            },
            "error": {
                "type": error_type,
                "message": simplified_error["simplified_message"],
                "raw_message": simplified_error["raw_message"],
                "status_code": simplified_error.get("status_code")
            },
            "suggestions": suggestions,
            "context": {
                "has_intent": error_context.get("intent") is not None,
                "intent_reason": error_context.get("intent", {}).get("reason") if error_context.get("intent") else None,
                "has_previous_output": error_context.get("previous_output") is not None
            }
        }

        # Add intent context if available
        if error_context.get("intent"):
            intent = error_context["intent"]
            feedback["context"]["intent"] = {
                "reason": intent.get("reason"),
                "assumption": intent.get("assumption"),
                "known_risk": intent.get("risk")
            }

        # Add info about previous node output
        if error_context.get("previous_output"):
            prev_output = error_context["previous_output"]
            feedback["context"]["previous_nodes"] = list(prev_output.keys())

        return feedback

    @staticmethod
    def format_feedback_for_llm(feedback: Dict) -> str:
        """Format feedback as readable markdown for LLM

        Args:
            feedback: Feedback dictionary

        Returns:
            Markdown formatted feedback
        """
        output = f"# ❌ Execution Error Detected\n\n"
        output += f"## Error Summary\n\n"
        output += f"{feedback['summary']}\n\n"

        output += f"## Node Details\n\n"
        output += f"- **Name**: {feedback['node']['name']}\n"
        output += f"- **Type**: `{feedback['node']['type']}`\n\n"

        output += f"## Error Details\n\n"
        output += f"- **Type**: `{feedback['error']['type']}`\n"
        output += f"- **Message**: {feedback['error']['message']}\n"

        if feedback['error'].get('status_code'):
            output += f"- **Status Code**: {feedback['error']['status_code']}\n"

        output += "\n"

        # Add intent context if available
        if feedback['context'].get('intent'):
            intent = feedback['context']['intent']
            output += f"## 📝 Original Intent\n\n"
            output += f"**Why this node exists**: {intent['reason']}\n\n"

            if intent.get('assumption'):
                output += f"**Assumption**: {intent['assumption']}\n\n"

            if intent.get('known_risk'):
                output += f"**Known Risk**: {intent['known_risk']}\n\n"

        # Add suggestions
        output += f"## 💡 Suggested Fixes\n\n"
        for i, suggestion in enumerate(feedback['suggestions'], 1):
            output += f"{i}. {suggestion}\n"

        output += "\n"

        # Add debug context
        if feedback['context'].get('previous_nodes'):
            output += f"## 🔍 Debug Context\n\n"
            output += f"**Previous nodes**: {', '.join(feedback['context']['previous_nodes'])}\n"
            output += f"**Has input data**: Yes\n\n"

        output += f"---\n\n"
        output += f"**Raw Error**: `{feedback['error']['raw_message']}`\n"

        return output
