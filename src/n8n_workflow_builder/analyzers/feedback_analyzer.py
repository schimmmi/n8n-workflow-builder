#!/usr/bin/env python3
"""
AI Feedback Analyzer Module
Analyzes AI responses and provides actionable feedback
"""
import json
import re
from typing import Dict, List, Optional


class AIFeedbackAnalyzer:
    """Analyzes workflow execution errors and provides AI-friendly feedback"""

    @staticmethod
    def analyze_execution_error(execution: Dict, workflow: Dict = None) -> Dict:
        """Analyze execution errors and generate structured feedback for AI

        Args:
            execution: Execution data from n8n
            workflow: Optional workflow data for context

        Returns:
            Dict with error analysis, suggestions, and AI-friendly feedback
        """
        feedback = {
            "has_errors": False,
            "errors": [],
            "root_cause": None,
            "suggestions": [],
            "affected_nodes": [],
            "ai_guidance": "",
            "fix_examples": []
        }

        # Check if execution failed
        if not execution.get('finished') or execution.get('stoppedAt'):
            feedback["has_errors"] = True

        # Analyze execution data
        exec_data = execution.get('data', {})
        result_data = exec_data.get('resultData', {})
        run_data = result_data.get('runData', {})

        # Collect all errors from nodes
        for node_name, node_runs in run_data.items():
            for run in node_runs:
                if 'error' in run:
                    error = run['error']
                    error_info = {
                        "node": node_name,
                        "message": error.get('message', 'Unknown error'),
                        "type": error.get('name', 'Error'),
                        "stack": error.get('stack', '')
                    }
                    feedback["errors"].append(error_info)
                    feedback["affected_nodes"].append(node_name)

        # Analyze error patterns and generate feedback
        if feedback["errors"]:
            feedback = AIFeedbackAnalyzer._analyze_error_patterns(feedback, workflow)

        return feedback

    @staticmethod
    def _analyze_error_patterns(feedback: Dict, workflow: Dict = None) -> Dict:
        """Analyze error patterns and generate specific guidance"""

        all_errors = " ".join([e['message'].lower() for e in feedback['errors']])

        # Authentication/Authorization errors
        if any(keyword in all_errors for keyword in ['401', '403', 'unauthorized', 'forbidden', 'authentication']):
            feedback["root_cause"] = "Authentication/Authorization Error"
            feedback["suggestions"] = [
                "Check if credentials are correctly configured",
                "Verify API key/token is valid and not expired",
                "Ensure correct authentication method is used",
                "Check if user has necessary permissions"
            ]
            feedback["ai_guidance"] = (
                "The workflow failed due to authentication issues. When generating workflows, ensure:\n"
                "1. Use credential references: {{$credentials.credentialName}} instead of hardcoded values\n"
                "2. Specify correct authentication type (Bearer, Basic, OAuth, etc.)\n"
                "3. Include proper headers (Authorization, API-Key, etc.)\n"
                "4. Test credentials before deploying workflow"
            )
            feedback["fix_examples"] = [
                {
                    "description": "Use credentials instead of hardcoded API key",
                    "wrong": {"parameters": {"headerParameters": {"parameters": [{"name": "Authorization", "value": "Bearer sk-abc123"}]}}},
                    "correct": {"parameters": {"authentication": "predefinedCredentialType", "nodeCredentialType": "apiKey"}}
                }
            ]

        # Network/Connection errors
        elif any(keyword in all_errors for keyword in ['timeout', 'econnrefused', 'network', 'connection', 'unreachable']):
            feedback["root_cause"] = "Network/Connection Error"
            feedback["suggestions"] = [
                "Check if the external service is reachable",
                "Verify the URL is correct",
                "Increase timeout settings",
                "Check firewall/VPN settings",
                "Verify SSL/TLS certificates"
            ]
            feedback["ai_guidance"] = (
                "The workflow failed due to network connectivity issues. When generating workflows:\n"
                "1. Always set reasonable timeouts (e.g., 30000ms for most APIs)\n"
                "2. Add retry logic for flaky connections\n"
                "3. Validate URLs are correct and reachable\n"
                "4. Consider using error handling nodes for network failures"
            )
            feedback["fix_examples"] = [
                {
                    "description": "Add timeout to HTTP Request node",
                    "wrong": {"parameters": {"url": "https://api.example.com"}},
                    "correct": {"parameters": {"url": "https://api.example.com", "timeout": 30000, "retry": {"maxRetries": 3}}}
                }
            ]

        # Data/Type errors
        elif any(keyword in all_errors for keyword in ['undefined', 'null', 'cannot read property', 'type error', 'invalid json']):
            feedback["root_cause"] = "Data/Type Error"
            feedback["suggestions"] = [
                "Check if previous node provides expected data structure",
                "Add data validation before processing",
                "Use default values for optional fields",
                "Verify JSON structure is valid",
                "Check if expressions reference existing fields"
            ]
            feedback["ai_guidance"] = (
                "The workflow failed due to data structure or type issues. When generating workflows:\n"
                "1. Always validate data exists before accessing: {{$json.field ?? 'default'}}\n"
                "2. Use IF nodes to check data before processing\n"
                "3. Add default values for optional fields\n"
                "4. Test with sample data that matches production structure\n"
                "5. Use Set nodes to normalize data structure"
            )
            feedback["fix_examples"] = [
                {
                    "description": "Add null checks and defaults",
                    "wrong": {"expression": "{{$json.user.email}}"},
                    "correct": {"expression": "{{$json.user?.email ?? 'no-email@example.com'}}"}
                }
            ]

        # Database/SQL errors
        elif any(keyword in all_errors for keyword in ['sql', 'database', 'query', 'syntax error', 'relation']):
            feedback["root_cause"] = "Database/SQL Error"
            feedback["suggestions"] = [
                "Verify SQL syntax is correct",
                "Check if table/column names exist",
                "Use parameterized queries to prevent SQL injection",
                "Verify database connection credentials",
                "Check if user has necessary database permissions"
            ]
            feedback["ai_guidance"] = (
                "The workflow failed due to database query issues. When generating workflows:\n"
                "1. Always use parameterized queries with placeholders\n"
                "2. Validate table and column names exist\n"
                "3. Test queries separately before adding to workflow\n"
                "4. Avoid SELECT * - specify columns explicitly\n"
                "5. Use proper escaping for dynamic values"
            )
            feedback["fix_examples"] = [
                {
                    "description": "Use parameterized query",
                    "wrong": {"query": "SELECT * FROM users WHERE id = '{{$json.id}}'"},
                    "correct": {"query": "SELECT id, name, email FROM users WHERE id = $1", "values": "={{[$json.id]}}"}
                }
            ]

        # Rate limiting
        elif any(keyword in all_errors for keyword in ['429', 'rate limit', 'too many requests']):
            feedback["root_cause"] = "Rate Limiting"
            feedback["suggestions"] = [
                "Add delay between requests",
                "Implement exponential backoff",
                "Batch requests if API supports it",
                "Check API rate limit quotas",
                "Consider caching responses"
            ]
            feedback["ai_guidance"] = (
                "The workflow failed due to rate limiting. When generating workflows:\n"
                "1. Add Wait nodes between API calls (e.g., 1000-2000ms)\n"
                "2. Implement retry logic with exponential backoff\n"
                "3. Use batching when processing multiple items\n"
                "4. Cache API responses when appropriate\n"
                "5. Check API documentation for rate limits"
            )
            feedback["fix_examples"] = [
                {
                    "description": "Add delay between requests",
                    "add_node": {"type": "n8n-nodes-base.wait", "name": "Rate Limit Delay", "parameters": {"amount": 1000}}
                }
            ]

        # Missing/Invalid parameters
        elif any(keyword in all_errors for keyword in ['required parameter', 'missing', 'invalid parameter']):
            feedback["root_cause"] = "Missing/Invalid Parameters"
            feedback["suggestions"] = [
                "Check if all required parameters are set",
                "Verify parameter values are in correct format",
                "Review node configuration",
                "Check API documentation for required fields"
            ]
            feedback["ai_guidance"] = (
                "The workflow failed due to missing or invalid parameters. When generating workflows:\n"
                "1. Always set all required parameters for each node\n"
                "2. Validate parameter formats (URLs, emails, dates, etc.)\n"
                "3. Use validation before passing data to nodes\n"
                "4. Check node documentation for parameter requirements\n"
                "5. Test with sample data that matches expected format"
            )

        # Generic error
        else:
            feedback["root_cause"] = "Unknown Error"
            feedback["suggestions"] = [
                "Check node configuration",
                "Verify input data format",
                "Enable workflow logging for more details",
                "Test with minimal data",
                "Check n8n logs for detailed error information"
            ]
            feedback["ai_guidance"] = (
                "The workflow encountered an unexpected error. When generating workflows:\n"
                "1. Add error handling nodes (Error Trigger)\n"
                "2. Use try/catch in Code nodes\n"
                "3. Add logging for debugging\n"
                "4. Test each node individually\n"
                "5. Start simple and add complexity gradually"
            )

        return feedback

    @staticmethod
    def generate_fix_workflow(feedback: Dict, workflow: Dict) -> Dict:
        """Generate an improved workflow based on error feedback

        Args:
            feedback: Error feedback from analyze_execution_error
            workflow: Original workflow

        Returns:
            Dict with suggested workflow improvements
        """
        improvements = {
            "original_issues": feedback.get("errors", []),
            "root_cause": feedback.get("root_cause"),
            "recommended_changes": [],
            "nodes_to_modify": [],
            "nodes_to_add": []
        }

        affected_nodes = feedback.get("affected_nodes", [])
        nodes = workflow.get('nodes', [])

        # Analyze affected nodes and suggest changes
        for node in nodes:
            if node['name'] in affected_nodes:
                node_type = node.get('type', '')
                changes = []

                # HTTP Request improvements
                if 'httpRequest' in node_type:
                    if not node.get('parameters', {}).get('timeout'):
                        changes.append({
                            "field": "timeout",
                            "current": None,
                            "suggested": 30000,
                            "reason": "Prevent indefinite hanging"
                        })

                    if feedback['root_cause'] == 'Authentication/Authorization Error':
                        changes.append({
                            "field": "authentication",
                            "current": node.get('parameters', {}).get('authentication'),
                            "suggested": "Use credentials",
                            "reason": "Fix authentication issues"
                        })

                # Code node improvements
                elif 'code' in node_type:
                    if feedback['root_cause'] == 'Data/Type Error':
                        changes.append({
                            "field": "jsCode",
                            "suggestion": "Add null checks and error handling",
                            "reason": "Prevent null/undefined errors"
                        })

                # Database node improvements
                elif 'postgres' in node_type or 'mysql' in node_type:
                    if feedback['root_cause'] == 'Database/SQL Error':
                        changes.append({
                            "field": "query",
                            "suggestion": "Use parameterized queries",
                            "reason": "Fix SQL errors and prevent injection"
                        })

                if changes:
                    improvements["nodes_to_modify"].append({
                        "node_name": node['name'],
                        "node_type": node_type,
                        "changes": changes
                    })

        # Suggest new nodes to add
        if feedback['root_cause'] == 'Rate Limiting':
            improvements["nodes_to_add"].append({
                "type": "n8n-nodes-base.wait",
                "name": "Rate Limit Delay",
                "parameters": {"amount": 1000},
                "reason": "Add delay between API calls to respect rate limits"
            })

        if not any(n.get('type') == 'n8n-nodes-base.errorTrigger' for n in nodes):
            improvements["nodes_to_add"].append({
                "type": "n8n-nodes-base.errorTrigger",
                "name": "Error Handler",
                "reason": "Catch and handle workflow errors gracefully"
            })

        # Add recommendations
        improvements["recommended_changes"] = feedback.get("suggestions", [])

        return improvements

    @staticmethod
    def format_ai_feedback(feedback: Dict, workflow_name: str = "Workflow") -> str:
        """Format feedback as a readable report for AI/humans

        Args:
            feedback: Feedback from analyze_execution_error
            workflow_name: Name of the workflow

        Returns:
            Formatted markdown report
        """
        report = f"# 🔍 Execution Error Analysis: {workflow_name}\n\n"

        if not feedback["has_errors"]:
            report += "✅ **Status:** Execution completed successfully\n"
            return report

        report += f"❌ **Status:** Execution failed\n"
        report += f"🎯 **Root Cause:** {feedback['root_cause']}\n\n"

        # Errors section
        if feedback["errors"]:
            report += "## 🔴 Errors Detected:\n\n"
            for idx, error in enumerate(feedback["errors"], 1):
                report += f"**{idx}. Node: `{error['node']}`**\n"
                report += f"   - Type: {error['type']}\n"
                report += f"   - Message: {error['message']}\n\n"

        # Affected nodes
        if feedback["affected_nodes"]:
            report += f"## 📍 Affected Nodes: {', '.join(feedback['affected_nodes'])}\n\n"

        # Suggestions
        if feedback["suggestions"]:
            report += "## 💡 Suggested Fixes:\n\n"
            for idx, suggestion in enumerate(feedback["suggestions"], 1):
                report += f"{idx}. {suggestion}\n"
            report += "\n"

        # AI Guidance
        if feedback["ai_guidance"]:
            report += "## 🤖 AI Guidance (for workflow generation):\n\n"
            report += feedback["ai_guidance"] + "\n\n"

        # Fix examples
        if feedback["fix_examples"]:
            report += "## 📝 Fix Examples:\n\n"
            for example in feedback["fix_examples"]:
                report += f"### {example['description']}\n\n"
                if 'wrong' in example:
                    report += "**❌ Wrong:**\n```json\n"
                    report += json.dumps(example['wrong'], indent=2)
                    report += "\n```\n\n"
                if 'correct' in example:
                    report += "**✅ Correct:**\n```json\n"
                    report += json.dumps(example['correct'], indent=2)
                    report += "\n```\n\n"

        return report

