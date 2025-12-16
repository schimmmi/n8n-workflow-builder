#!/usr/bin/env python3
"""
n8n Workflow Builder MCP Server
Advanced MCP server for n8n workflow creation, optimization, and management
"""
import asyncio
import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

import httpx
from mcp.server import Server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("n8n-workflow-builder")

# State file location
STATE_FILE = Path.home() / ".n8n_workflow_builder_state.json"

# n8n Node Knowledge Base - The most common and useful nodes
NODE_KNOWLEDGE = {
    "triggers": {
        "webhook": {
            "name": "Webhook",
            "desc": "Receives HTTP requests from external sources",
            "use_cases": ["API endpoints", "External integrations", "Form submissions"],
            "best_practices": ["Use authentication", "Validate input data", "Return proper status codes"]
        },
        "schedule": {
            "name": "Schedule Trigger",
            "desc": "Runs workflows on a schedule",
            "use_cases": ["Daily reports", "Periodic data syncs", "Cleanup tasks"],
            "best_practices": ["Use cron for complex schedules", "Consider timezone", "Avoid peak times"]
        },
        "manual": {
            "name": "Manual Trigger",
            "desc": "Manually start workflows",
            "use_cases": ["Testing", "One-time tasks", "Manual interventions"],
            "best_practices": ["Add clear description", "Use for development"]
        }
    },
    "logic": {
        "if": {
            "name": "IF",
            "desc": "Conditional branching based on rules",
            "use_cases": ["Data validation", "Route based on conditions", "Error handling"],
            "best_practices": ["Keep conditions simple", "Use meaningful names", "Handle both paths"]
        },
        "switch": {
            "name": "Switch",
            "desc": "Multi-way branching",
            "use_cases": ["Multiple conditions", "Status-based routing", "Category routing"],
            "best_practices": ["Add default case", "Use for 3+ branches", "Clear case names"]
        },
        "merge": {
            "name": "Merge",
            "desc": "Combine data from multiple sources",
            "use_cases": ["Combine API results", "Aggregate data", "Join datasets"],
            "best_practices": ["Choose right merge mode", "Handle missing data", "Check data structure"]
        },
        "code": {
            "name": "Code",
            "desc": "Execute JavaScript/Python code",
            "use_cases": ["Complex transforms", "Custom logic", "Data processing"],
            "best_practices": ["Keep code simple", "Add comments", "Handle errors", "Use $input for data"]
        }
    },
    "data": {
        "http_request": {
            "name": "HTTP Request",
            "desc": "Make HTTP API calls",
            "use_cases": ["API integration", "Web scraping", "External services"],
            "best_practices": ["Set timeout", "Handle errors", "Use retry logic", "Validate responses"]
        },
        "set": {
            "name": "Edit Fields (Set)",
            "desc": "Transform and set data fields",
            "use_cases": ["Data mapping", "Format conversion", "Add calculated fields"],
            "best_practices": ["Use expressions", "Keep transforms simple", "Clear field names"]
        },
        "function": {
            "name": "Function",
            "desc": "Transform data with JavaScript",
            "use_cases": ["Complex calculations", "Array operations", "String manipulation"],
            "best_practices": ["Return items array", "Handle edge cases", "Use lodash when needed"]
        }
    },
    "storage": {
        "postgres": {
            "name": "Postgres",
            "desc": "PostgreSQL database operations",
            "use_cases": ["Data persistence", "Complex queries", "Transactions"],
            "best_practices": ["Use parameterized queries", "Index lookups", "Batch operations"]
        },
        "redis": {
            "name": "Redis",
            "desc": "Redis key-value store",
            "use_cases": ["Caching", "Rate limiting", "Session storage"],
            "best_practices": ["Set TTL", "Use appropriate data types", "Handle connection errors"]
        }
    },
    "integrations": {
        "slack": {
            "name": "Slack",
            "desc": "Slack messaging integration",
            "use_cases": ["Notifications", "Bot interactions", "Team updates"],
            "best_practices": ["Format messages", "Use thread replies", "Handle rate limits"]
        },
        "telegram": {
            "name": "Telegram",
            "desc": "Telegram bot integration",
            "use_cases": ["Notifications", "Bot commands", "Interactive messages"],
            "best_practices": ["Parse mode HTML/Markdown", "Keyboard layouts", "Handle commands"]
        },
        "gmail": {
            "name": "Gmail",
            "desc": "Gmail email operations",
            "use_cases": ["Email automation", "Read emails", "Send emails"],
            "best_practices": ["Use filters", "Batch operations", "Handle attachments"]
        }
    }
}

# Workflow Templates
WORKFLOW_TEMPLATES = {
    "api_endpoint": {
        "name": "Simple API Endpoint",
        "nodes": [
            {"type": "webhook", "name": "Webhook"},
            {"type": "set", "name": "Process Data"},
            {"type": "http_request", "name": "Call External API"},
            {"type": "code", "name": "Transform Response"},
            {"type": "respond_to_webhook", "name": "Return Response"}
        ],
        "connections": "linear"
    },
    "scheduled_report": {
        "name": "Daily Report Generator",
        "nodes": [
            {"type": "schedule", "name": "Daily at 9AM"},
            {"type": "postgres", "name": "Fetch Data"},
            {"type": "function", "name": "Calculate Metrics"},
            {"type": "set", "name": "Format Report"},
            {"type": "slack", "name": "Send to Slack"}
        ],
        "connections": "linear"
    },
    "data_sync": {
        "name": "Database Sync",
        "nodes": [
            {"type": "schedule", "name": "Every Hour"},
            {"type": "http_request", "name": "Fetch from API"},
            {"type": "if", "name": "Has New Data?"},
            {"type": "postgres", "name": "Insert/Update"},
            {"type": "telegram", "name": "Notify on Errors"}
        ],
        "connections": "conditional"
    }
}


class StateManager:
    """Manages persistent state and context for workflow operations"""

    def __init__(self, state_file: Path = STATE_FILE):
        self.state_file = state_file
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        """Load state from file"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load state file: {e}")
                return self._default_state()
        return self._default_state()

    def _default_state(self) -> Dict:
        """Get default state structure"""
        return {
            "current_workflow_id": None,
            "current_workflow_name": None,
            "last_execution_id": None,
            "recent_workflows": [],
            "session_history": [],
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }

    def _save_state(self):
        """Save state to file"""
        try:
            self.state["last_updated"] = datetime.now().isoformat()
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save state file: {e}")

    def set_current_workflow(self, workflow_id: str, workflow_name: str):
        """Set the current active workflow"""
        self.state["current_workflow_id"] = workflow_id
        self.state["current_workflow_name"] = workflow_name

        # Update recent workflows (keep last 10)
        workflow_entry = {
            "id": workflow_id,
            "name": workflow_name,
            "accessed_at": datetime.now().isoformat()
        }

        # Remove if already in list
        self.state["recent_workflows"] = [
            w for w in self.state["recent_workflows"]
            if w["id"] != workflow_id
        ]

        # Add to front
        self.state["recent_workflows"].insert(0, workflow_entry)
        self.state["recent_workflows"] = self.state["recent_workflows"][:10]

        self._save_state()
        logger.info(f"Set current workflow: {workflow_name} ({workflow_id})")

    def get_current_workflow(self) -> Optional[Dict]:
        """Get current workflow info"""
        if self.state["current_workflow_id"]:
            return {
                "id": self.state["current_workflow_id"],
                "name": self.state["current_workflow_name"]
            }
        return None

    def set_last_execution(self, execution_id: str):
        """Record last execution"""
        self.state["last_execution_id"] = execution_id
        self._save_state()

    def get_last_execution(self) -> Optional[str]:
        """Get last execution ID"""
        return self.state.get("last_execution_id")

    def log_action(self, action: str, details: Dict = None):
        """Log an action to session history"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details or {}
        }

        self.state["session_history"].append(entry)

        # Keep last 50 entries
        self.state["session_history"] = self.state["session_history"][-50:]

        self._save_state()

    def get_session_history(self, limit: int = 10) -> List[Dict]:
        """Get recent session history"""
        return self.state["session_history"][-limit:]

    def get_recent_workflows(self) -> List[Dict]:
        """Get recently accessed workflows"""
        return self.state["recent_workflows"]

    def clear_state(self):
        """Clear all state"""
        self.state = self._default_state()
        self._save_state()
        logger.info("State cleared")

    def get_state_summary(self) -> str:
        """Get a formatted summary of current state"""
        summary = "# Current Session State\n\n"

        current = self.get_current_workflow()
        if current:
            summary += f"**Active Workflow:** {current['name']} (`{current['id']}`)\n\n"
        else:
            summary += "**Active Workflow:** None\n\n"

        if self.state.get("last_execution_id"):
            summary += f"**Last Execution:** `{self.state['last_execution_id']}`\n\n"

        recent = self.get_recent_workflows()
        if recent:
            summary += "## Recent Workflows:\n\n"
            for wf in recent[:5]:
                summary += f"- {wf['name']} (`{wf['id']}`) - {wf['accessed_at']}\n"
            summary += "\n"

        history = self.get_session_history(5)
        if history:
            summary += "## Recent Actions:\n\n"
            for entry in reversed(history):
                summary += f"- **{entry['timestamp']}** - {entry['action']}\n"

        return summary


class N8nClient:
    """Client for n8n API"""
    
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)
        self.headers = {"X-N8N-API-KEY": api_key, "Content-Type": "application/json"}
    
    async def get_workflows(self, active_only: bool = False) -> List[Dict]:
        """Get all workflows"""
        params = {}
        if active_only:
            params["active"] = "true"
        
        response = await self.client.get(
            f"{self.api_url}/api/v1/workflows",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()["data"]
    
    async def get_workflow(self, workflow_id: str) -> Dict:
        """Get a specific workflow"""
        response = await self.client.get(
            f"{self.api_url}/api/v1/workflows/{workflow_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    async def create_workflow(self, workflow: Dict) -> Dict:
        """Create a new workflow"""
        response = await self.client.post(
            f"{self.api_url}/api/v1/workflows",
            headers=self.headers,
            json=workflow
        )
        response.raise_for_status()
        return response.json()

    async def execute_workflow(self, workflow_id: str, data: Optional[Dict] = None) -> Dict:
        """Execute a workflow (test run)

        Note: This triggers a workflow execution similar to the "Execute Workflow" button in the UI.
        For production workflows, they should be triggered via webhooks or schedule.
        """
        # n8n API endpoint for running/testing workflows
        # The correct endpoint might be /run or /test depending on n8n version
        try:
            # Try the /run endpoint first (newer n8n versions)
            response = await self.client.post(
                f"{self.api_url}/api/v1/workflows/{workflow_id}/run",
                headers=self.headers,
                json=data or {}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                # Try alternative endpoint /test (older versions)
                try:
                    response = await self.client.post(
                        f"{self.api_url}/api/v1/workflows/{workflow_id}/test",
                        headers=self.headers,
                        json=data or {}
                    )
                    response.raise_for_status()
                    return response.json()
                except httpx.HTTPStatusError:
                    # If both fail, provide helpful error message
                    raise Exception(
                        f"Cannot execute workflow via API. "
                        f"This workflow might need to be triggered via webhook or schedule, "
                        f"or use the 'Execute Workflow' button in the n8n UI."
                    )
            raise
    
    async def get_executions(self, workflow_id: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Get workflow executions (summary only, without full node data)"""
        params = {"limit": limit}
        if workflow_id:
            params["workflowId"] = workflow_id

        response = await self.client.get(
            f"{self.api_url}/api/v1/executions",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()["data"]

    async def get_execution(self, execution_id: str, include_data: bool = True) -> Dict:
        """Get detailed execution data including all node inputs/outputs

        Args:
            execution_id: The execution ID
            include_data: Whether to include full execution data (default: True)

        Returns:
            Full execution data with node data
        """
        # Add includeData parameter to get full node execution data
        params = {}
        if include_data:
            params['includeData'] = 'true'

        response = await self.client.get(
            f"{self.api_url}/api/v1/executions/{execution_id}",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()

        result = response.json()

        # Log for debugging if data is still missing
        if not result.get('data', {}).get('resultData'):
            logger.warning(f"Execution {execution_id} has no resultData - execution data might not be saved by n8n")

        return result

    async def update_workflow(self, workflow_id: str, updates: Dict) -> Dict:
        """Update an existing workflow

        Args:
            workflow_id: ID of the workflow to update
            updates: Dictionary with fields to update (name, active, nodes, connections, settings, etc.)

        Returns:
            Updated workflow data
        """
        # First get the current workflow to merge with updates
        current_workflow = await self.get_workflow(workflow_id)

        # Whitelist of fields that are allowed by n8n API for updates
        # Note: 'active', 'tags', 'id', 'createdAt', 'updatedAt' etc. are read-only
        allowed_fields = ['name', 'nodes', 'connections', 'settings', 'staticData']

        # Build the update payload - start with required fields
        payload = {
            'name': current_workflow.get('name', 'Unnamed Workflow'),
            'nodes': current_workflow.get('nodes', []),
            'connections': current_workflow.get('connections', {}),
        }

        # Add optional allowed fields if they exist in current workflow
        for field in ['settings', 'staticData']:
            if field in current_workflow:
                payload[field] = current_workflow[field]

        # Apply updates - only allow whitelisted fields
        for key, value in updates.items():
            if key in allowed_fields:
                payload[key] = value
            else:
                logger.warning(f"Skipping field '{key}' - it's read-only or not supported by n8n API")

        # Ensure connections is always present and is a dict
        if 'connections' not in payload or payload['connections'] is None:
            payload['connections'] = {}

        # n8n API uses PUT for updates, not PATCH
        try:
            response = await self.client.put(
                f"{self.api_url}/api/v1/workflows/{workflow_id}",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            # Log the detailed error response for debugging
            error_detail = ""
            try:
                error_detail = e.response.text
            except:
                error_detail = str(e)
            logger.error(f"Failed to update workflow {workflow_id}: {error_detail}")
            logger.error(f"Payload sent: {json.dumps(payload, indent=2)}")
            raise Exception(f"Failed to update workflow: {error_detail}")

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


class WorkflowValidator:
    """Validates workflows before deployment"""

    # Required fields for workflow schema
    REQUIRED_WORKFLOW_FIELDS = ['name', 'nodes', 'connections']
    REQUIRED_NODE_FIELDS = ['name', 'type', 'position', 'parameters']

    # Node type patterns for validation
    TRIGGER_NODE_TYPES = ['n8n-nodes-base.webhook', 'n8n-nodes-base.scheduleTrigger', 'n8n-nodes-base.manualTrigger']

    @staticmethod
    def validate_workflow_schema(workflow: Dict) -> Dict[str, List[str]]:
        """Validate workflow schema structure

        Returns:
            Dict with 'errors' and 'warnings' lists
        """
        errors = []
        warnings = []

        # Check required workflow fields
        for field in WorkflowValidator.REQUIRED_WORKFLOW_FIELDS:
            if field not in workflow:
                errors.append(f"Missing required field: '{field}'")

        # Check if workflow has a name
        if 'name' in workflow:
            if not workflow['name'] or not workflow['name'].strip():
                errors.append("Workflow name cannot be empty")
            elif len(workflow['name']) > 200:
                warnings.append("Workflow name is very long (>200 chars)")

        # Validate nodes
        nodes = workflow.get('nodes', [])
        if not isinstance(nodes, list):
            errors.append("'nodes' must be a list")
        else:
            if len(nodes) == 0:
                errors.append("Workflow has no nodes")

            for idx, node in enumerate(nodes):
                if not isinstance(node, dict):
                    errors.append(f"Node at index {idx} is not a dictionary")
                    continue

                # Check required node fields
                for field in WorkflowValidator.REQUIRED_NODE_FIELDS:
                    if field not in node:
                        errors.append(f"Node '{node.get('name', f'at index {idx}')}': Missing required field '{field}'")

                # Validate node name
                if 'name' in node:
                    if not node['name'] or not node['name'].strip():
                        errors.append(f"Node at index {idx}: Name cannot be empty")

                # Validate node type
                if 'type' in node:
                    if not node['type'] or not node['type'].strip():
                        errors.append(f"Node '{node.get('name')}': Type cannot be empty")

                # Validate position
                if 'position' in node:
                    if not isinstance(node['position'], list) or len(node['position']) != 2:
                        errors.append(f"Node '{node.get('name')}': Position must be [x, y] array")

        # Validate connections
        connections = workflow.get('connections', {})
        if not isinstance(connections, dict):
            errors.append("'connections' must be a dictionary")

        return {'errors': errors, 'warnings': warnings}

    @staticmethod
    def validate_workflow_semantics(workflow: Dict) -> Dict[str, List[str]]:
        """Validate semantic rules (logic, best practices)

        Returns:
            Dict with 'errors' and 'warnings' lists
        """
        errors = []
        warnings = []
        nodes = workflow.get('nodes', [])
        connections = workflow.get('connections', {})

        # Check for at least one trigger node
        trigger_nodes = [n for n in nodes if n.get('type') in WorkflowValidator.TRIGGER_NODE_TYPES]
        if not trigger_nodes:
            errors.append("Workflow must have at least one trigger node (Webhook, Schedule, or Manual)")

        # Check for duplicate node names
        node_names = [n.get('name') for n in nodes if n.get('name')]
        duplicate_names = [name for name in node_names if node_names.count(name) > 1]
        if duplicate_names:
            errors.append(f"Duplicate node names found: {', '.join(set(duplicate_names))}")

        # Check for orphaned nodes (nodes without connections)
        if len(nodes) > 1:
            connected_nodes = set()
            for source_name, targets in connections.items():
                connected_nodes.add(source_name)
                if isinstance(targets, dict):
                    for target_list in targets.values():
                        if isinstance(target_list, list):
                            for target in target_list:
                                if isinstance(target, dict):
                                    connected_nodes.add(target.get('node'))

            orphaned = [n['name'] for n in nodes if n.get('name') and n['name'] not in connected_nodes and n.get('type') not in WorkflowValidator.TRIGGER_NODE_TYPES]
            if orphaned:
                warnings.append(f"Orphaned nodes (no connections): {', '.join(orphaned)}")

        # Check for default node names (bad practice)
        default_names = ['Webhook', 'HTTP Request', 'Set', 'IF', 'Function', 'Code']
        unnamed_nodes = [n['name'] for n in nodes if n.get('name') in default_names]
        if unnamed_nodes:
            warnings.append(f"Nodes with default names (should be renamed): {', '.join(set(unnamed_nodes))}")

        # Check for missing credentials in nodes that require them
        credential_nodes = ['n8n-nodes-base.httpRequest', 'n8n-nodes-base.postgres', 'n8n-nodes-base.redis']
        for node in nodes:
            if node.get('type') in credential_nodes:
                if not node.get('credentials') or len(node.get('credentials', {})) == 0:
                    warnings.append(f"Node '{node.get('name')}' may need credentials configured")

        # Check for hardcoded sensitive data
        for node in nodes:
            node_str = json.dumps(node.get('parameters', {}))
            if any(keyword in node_str.lower() for keyword in ['password', 'apikey', 'api_key', 'secret', 'token']) and '{{' not in node_str:
                warnings.append(f"Node '{node.get('name')}' may contain hardcoded sensitive data")

        # Check workflow complexity
        if len(nodes) > 30:
            warnings.append(f"Workflow is complex ({len(nodes)} nodes). Consider splitting into sub-workflows.")

        # Check for missing error handling
        error_trigger = any(n.get('type') == 'n8n-nodes-base.errorTrigger' for n in nodes)
        if len(nodes) > 5 and not error_trigger:
            warnings.append("Workflow lacks error handling (Error Trigger node)")

        return {'errors': errors, 'warnings': warnings}

    @staticmethod
    def validate_node_parameters(workflow: Dict) -> Dict[str, List[str]]:
        """Validate node-specific parameter requirements

        Returns:
            Dict with 'errors' and 'warnings' lists
        """
        errors = []
        warnings = []
        nodes = workflow.get('nodes', [])

        for node in nodes:
            node_type = node.get('type', '')
            node_name = node.get('name', 'Unknown')
            params = node.get('parameters', {})

            # Webhook node validation
            if node_type == 'n8n-nodes-base.webhook':
                if not params.get('path'):
                    errors.append(f"Webhook node '{node_name}': Missing 'path' parameter")

                auth_method = params.get('authentication')
                if not auth_method or auth_method == 'none':
                    warnings.append(f"Webhook node '{node_name}': No authentication enabled (security risk)")

            # HTTP Request node validation
            elif node_type == 'n8n-nodes-base.httpRequest':
                if not params.get('url'):
                    errors.append(f"HTTP Request node '{node_name}': Missing 'url' parameter")

                if not params.get('timeout'):
                    warnings.append(f"HTTP Request node '{node_name}': No timeout set (may hang)")

            # Schedule Trigger validation
            elif node_type == 'n8n-nodes-base.scheduleTrigger':
                if not params.get('rule') and not params.get('cronExpression'):
                    errors.append(f"Schedule Trigger node '{node_name}': Missing schedule configuration")

            # IF node validation
            elif node_type == 'n8n-nodes-base.if':
                conditions = params.get('conditions', {})
                if not conditions or len(conditions.get('boolean', [])) == 0:
                    warnings.append(f"IF node '{node_name}': No conditions defined")

            # Postgres node validation
            elif node_type == 'n8n-nodes-base.postgres':
                operation = params.get('operation')
                if operation in ['executeQuery', 'insert', 'update', 'delete']:
                    query = params.get('query', '')
                    if 'SELECT *' in query.upper():
                        warnings.append(f"Postgres node '{node_name}': Using SELECT * (bad practice)")
                    if operation != 'executeQuery' and '{{' not in query:
                        warnings.append(f"Postgres node '{node_name}': Query should use parameterized values")

            # Set node validation
            elif node_type == 'n8n-nodes-base.set':
                if not params.get('values'):
                    warnings.append(f"Set node '{node_name}': No values configured")

            # Code node validation
            elif node_type == 'n8n-nodes-base.code':
                code = params.get('jsCode', '')
                if not code or len(code.strip()) == 0:
                    errors.append(f"Code node '{node_name}': No code defined")

                # Check for common mistakes
                if 'return items' not in code and 'return [{' not in code:
                    warnings.append(f"Code node '{node_name}': Should return items array")

        return {'errors': errors, 'warnings': warnings}

    @classmethod
    def validate_workflow_full(cls, workflow: Dict) -> Dict:
        """Run all validations and combine results

        Returns:
            Dict with 'valid', 'errors', 'warnings', and 'summary'
        """
        schema_result = cls.validate_workflow_schema(workflow)
        semantic_result = cls.validate_workflow_semantics(workflow)
        param_result = cls.validate_node_parameters(workflow)

        all_errors = schema_result['errors'] + semantic_result['errors'] + param_result['errors']
        all_warnings = schema_result['warnings'] + semantic_result['warnings'] + param_result['warnings']

        is_valid = len(all_errors) == 0

        return {
            'valid': is_valid,
            'errors': all_errors,
            'warnings': all_warnings,
            'summary': {
                'total_errors': len(all_errors),
                'total_warnings': len(all_warnings),
                'schema_errors': len(schema_result['errors']),
                'semantic_errors': len(semantic_result['errors']),
                'parameter_errors': len(param_result['errors'])
            }
        }


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


class RBACManager:
    """Role-Based Access Control and Multi-Tenant Security Manager"""

    # Role definitions with permissions
    ROLES = {
        "admin": {
            "name": "Administrator",
            "permissions": [
                "workflow.create", "workflow.read", "workflow.update", "workflow.delete",
                "workflow.execute", "workflow.validate", "workflow.analyze",
                "execution.read", "execution.analyze",
                "state.read", "state.write", "state.clear",
                "approval.create", "approval.approve", "approval.reject",
                "user.manage", "role.manage", "audit.read"
            ],
            "description": "Full access to all operations"
        },
        "developer": {
            "name": "Developer",
            "permissions": [
                "workflow.create", "workflow.read", "workflow.update",
                "workflow.execute", "workflow.validate", "workflow.analyze",
                "execution.read", "execution.analyze",
                "state.read", "state.write",
                "approval.create"
            ],
            "description": "Can create, modify, and test workflows, but needs approval for critical operations"
        },
        "operator": {
            "name": "Operator",
            "permissions": [
                "workflow.read", "workflow.execute",
                "execution.read",
                "state.read"
            ],
            "description": "Can execute existing workflows and view results"
        },
        "viewer": {
            "name": "Viewer",
            "permissions": [
                "workflow.read",
                "execution.read",
                "state.read"
            ],
            "description": "Read-only access to workflows and executions"
        },
        "auditor": {
            "name": "Auditor",
            "permissions": [
                "workflow.read",
                "execution.read",
                "audit.read"
            ],
            "description": "Can view workflows, executions, and audit logs for compliance"
        }
    }

    # Critical operations requiring approval
    APPROVAL_REQUIRED_OPERATIONS = [
        "workflow.delete",
        "workflow.deploy_production",
        "workflow.modify_active",
        "state.clear"
    ]

    def __init__(self, state_file: Path = None):
        self.state_file = state_file or (Path.home() / ".n8n_rbac_state.json")
        self.rbac_state = self._load_rbac_state()

    def _load_rbac_state(self) -> Dict:
        """Load RBAC state from file"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load RBAC state: {e}")
                return self._default_rbac_state()
        return self._default_rbac_state()

    def _default_rbac_state(self) -> Dict:
        """Default RBAC state structure"""
        return {
            "users": {
                "default": {
                    "username": "default",
                    "role": "admin",
                    "tenant_id": "default",
                    "created_at": datetime.now().isoformat()
                }
            },
            "tenants": {
                "default": {
                    "tenant_id": "default",
                    "name": "Default Tenant",
                    "workflows": [],
                    "users": ["default"],
                    "created_at": datetime.now().isoformat()
                }
            },
            "pending_approvals": [],
            "audit_log": [],
            "created_at": datetime.now().isoformat()
        }

    def _save_rbac_state(self):
        """Save RBAC state to file"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.rbac_state, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save RBAC state: {e}")

    def check_permission(self, username: str, permission: str) -> bool:
        """Check if user has specific permission"""
        user = self.rbac_state["users"].get(username)
        if not user:
            return False

        role = user.get("role")
        if role not in self.ROLES:
            return False

        return permission in self.ROLES[role]["permissions"]

    def require_approval(self, operation: str) -> bool:
        """Check if operation requires approval"""
        return operation in self.APPROVAL_REQUIRED_OPERATIONS

    def create_approval_request(self, username: str, operation: str, details: Dict) -> str:
        """Create approval request for critical operation"""
        approval_id = f"approval-{datetime.now().timestamp()}"
        approval = {
            "id": approval_id,
            "username": username,
            "operation": operation,
            "details": details,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "approved_by": None,
            "approved_at": None
        }

        self.rbac_state["pending_approvals"].append(approval)
        self._save_rbac_state()

        self._audit_log(username, "approval_request_created", {
            "approval_id": approval_id,
            "operation": operation
        })

        return approval_id

    def approve_request(self, approval_id: str, approver: str) -> Dict:
        """Approve a pending request"""
        approval = self._find_approval(approval_id)
        if not approval:
            return {"success": False, "error": "Approval request not found"}

        if approval["status"] != "pending":
            return {"success": False, "error": f"Approval already {approval['status']}"}

        # Check if approver has approval permission
        if not self.check_permission(approver, "approval.approve"):
            return {"success": False, "error": "Insufficient permissions to approve"}

        # Cannot approve own request
        if approver == approval["username"]:
            return {"success": False, "error": "Cannot approve your own request"}

        approval["status"] = "approved"
        approval["approved_by"] = approver
        approval["approved_at"] = datetime.now().isoformat()

        self._save_rbac_state()

        self._audit_log(approver, "approval_approved", {
            "approval_id": approval_id,
            "requested_by": approval["username"],
            "operation": approval["operation"]
        })

        return {"success": True, "approval": approval}

    def reject_request(self, approval_id: str, rejector: str, reason: str = None) -> Dict:
        """Reject a pending request"""
        approval = self._find_approval(approval_id)
        if not approval:
            return {"success": False, "error": "Approval request not found"}

        if approval["status"] != "pending":
            return {"success": False, "error": f"Approval already {approval['status']}"}

        if not self.check_permission(rejector, "approval.reject"):
            return {"success": False, "error": "Insufficient permissions to reject"}

        approval["status"] = "rejected"
        approval["approved_by"] = rejector
        approval["approved_at"] = datetime.now().isoformat()
        approval["rejection_reason"] = reason

        self._save_rbac_state()

        self._audit_log(rejector, "approval_rejected", {
            "approval_id": approval_id,
            "requested_by": approval["username"],
            "operation": approval["operation"],
            "reason": reason
        })

        return {"success": True, "approval": approval}

    def _find_approval(self, approval_id: str) -> Optional[Dict]:
        """Find approval request by ID"""
        for approval in self.rbac_state["pending_approvals"]:
            if approval["id"] == approval_id:
                return approval
        return None

    def get_pending_approvals(self, username: str = None) -> List[Dict]:
        """Get pending approval requests"""
        pending = [a for a in self.rbac_state["pending_approvals"] if a["status"] == "pending"]

        if username:
            # Return requests for this user or requests they can approve
            can_approve = self.check_permission(username, "approval.approve")
            if can_approve:
                return pending
            else:
                return [a for a in pending if a["username"] == username]

        return pending

    def add_user(self, username: str, role: str, tenant_id: str = "default") -> Dict:
        """Add a new user"""
        if username in self.rbac_state["users"]:
            return {"success": False, "error": "User already exists"}

        if role not in self.ROLES:
            return {"success": False, "error": f"Invalid role: {role}"}

        user = {
            "username": username,
            "role": role,
            "tenant_id": tenant_id,
            "created_at": datetime.now().isoformat()
        }

        self.rbac_state["users"][username] = user

        # Add user to tenant
        if tenant_id in self.rbac_state["tenants"]:
            self.rbac_state["tenants"][tenant_id]["users"].append(username)

        self._save_rbac_state()

        self._audit_log("system", "user_created", {
            "username": username,
            "role": role,
            "tenant_id": tenant_id
        })

        return {"success": True, "user": user}

    def create_tenant(self, tenant_id: str, name: str) -> Dict:
        """Create a new tenant"""
        if tenant_id in self.rbac_state["tenants"]:
            return {"success": False, "error": "Tenant already exists"}

        tenant = {
            "tenant_id": tenant_id,
            "name": name,
            "workflows": [],
            "users": [],
            "created_at": datetime.now().isoformat()
        }

        self.rbac_state["tenants"][tenant_id] = tenant
        self._save_rbac_state()

        self._audit_log("system", "tenant_created", {
            "tenant_id": tenant_id,
            "name": name
        })

        return {"success": True, "tenant": tenant}

    def check_tenant_access(self, username: str, workflow_id: str) -> bool:
        """Check if user has access to workflow based on tenant"""
        user = self.rbac_state["users"].get(username)
        if not user:
            return False

        tenant_id = user["tenant_id"]
        tenant = self.rbac_state["tenants"].get(tenant_id)
        if not tenant:
            return False

        # Admin users can access all workflows
        if user["role"] == "admin":
            return True

        # Check if workflow belongs to user's tenant
        return workflow_id in tenant.get("workflows", [])

    def register_workflow(self, workflow_id: str, tenant_id: str):
        """Register workflow to tenant"""
        if tenant_id in self.rbac_state["tenants"]:
            tenant = self.rbac_state["tenants"][tenant_id]
            if workflow_id not in tenant["workflows"]:
                tenant["workflows"].append(workflow_id)
                self._save_rbac_state()

    def _audit_log(self, username: str, action: str, details: Dict):
        """Log security-relevant actions"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "username": username,
            "action": action,
            "details": details
        }

        self.rbac_state["audit_log"].append(log_entry)

        # Keep last 500 entries
        self.rbac_state["audit_log"] = self.rbac_state["audit_log"][-500:]

        self._save_rbac_state()

        logger.info(f"AUDIT: {username} - {action} - {details}")

    def get_audit_log(self, limit: int = 50, username: str = None, action: str = None) -> List[Dict]:
        """Get audit log with filters"""
        logs = self.rbac_state["audit_log"]

        if username:
            logs = [l for l in logs if l["username"] == username]

        if action:
            logs = [l for l in logs if l["action"] == action]

        return logs[-limit:]

    def get_user_info(self, username: str) -> Optional[Dict]:
        """Get user information"""
        user = self.rbac_state["users"].get(username)
        if not user:
            return None

        role_info = self.ROLES.get(user["role"], {})
        return {
            **user,
            "role_name": role_info.get("name"),
            "permissions": role_info.get("permissions", []),
            "role_description": role_info.get("description")
        }

    def generate_rbac_report(self) -> str:
        """Generate RBAC status report"""
        report = "# 🔒 RBAC & Security Status\n\n"

        # Users summary
        users = self.rbac_state["users"]
        report += f"## 👥 Users: {len(users)}\n\n"
        role_counts = {}
        for user in users.values():
            role = user["role"]
            role_counts[role] = role_counts.get(role, 0) + 1

        for role, count in role_counts.items():
            role_name = self.ROLES.get(role, {}).get("name", role)
            report += f"- **{role_name}**: {count} users\n"

        # Tenants summary
        tenants = self.rbac_state["tenants"]
        report += f"\n## 🏢 Tenants: {len(tenants)}\n\n"
        for tenant in tenants.values():
            report += f"- **{tenant['name']}** (`{tenant['tenant_id']}`)\n"
            report += f"  - Users: {len(tenant['users'])}\n"
            report += f"  - Workflows: {len(tenant['workflows'])}\n"

        # Pending approvals
        pending = self.get_pending_approvals()
        report += f"\n## ⏳ Pending Approvals: {len(pending)}\n\n"
        if pending:
            for approval in pending[:5]:
                report += f"- **{approval['id']}** - {approval['operation']} (by {approval['username']})\n"

        # Recent audit log
        recent_logs = self.get_audit_log(limit=5)
        report += f"\n## 📋 Recent Audit Log:\n\n"
        for log in reversed(recent_logs):
            report += f"- **{log['timestamp']}** - {log['username']}: {log['action']}\n"

        return report


class WorkflowBuilder:
    """AI-powered workflow builder"""

    @staticmethod
    def suggest_nodes(description: str) -> List[Dict]:
        """Suggest nodes based on workflow description"""
        description_lower = description.lower()
        suggestions = []
        
        # Trigger detection
        if any(word in description_lower for word in ["api", "endpoint", "webhook", "http"]):
            suggestions.append(NODE_KNOWLEDGE["triggers"]["webhook"])
        elif any(word in description_lower for word in ["schedule", "daily", "hourly", "cron"]):
            suggestions.append(NODE_KNOWLEDGE["triggers"]["schedule"])
        
        # Integration detection
        if "slack" in description_lower:
            suggestions.append(NODE_KNOWLEDGE["integrations"]["slack"])
        if "telegram" in description_lower:
            suggestions.append(NODE_KNOWLEDGE["integrations"]["telegram"])
        if "email" in description_lower or "gmail" in description_lower:
            suggestions.append(NODE_KNOWLEDGE["integrations"]["gmail"])
        
        # Logic detection
        if any(word in description_lower for word in ["if", "condition", "check", "validate"]):
            suggestions.append(NODE_KNOWLEDGE["logic"]["if"])
        if any(word in description_lower for word in ["switch", "multiple", "cases"]):
            suggestions.append(NODE_KNOWLEDGE["logic"]["switch"])
        
        # Data operations
        if any(word in description_lower for word in ["transform", "map", "convert"]):
            suggestions.append(NODE_KNOWLEDGE["data"]["set"])
        if any(word in description_lower for word in ["api call", "fetch", "get data"]):
            suggestions.append(NODE_KNOWLEDGE["data"]["http_request"])
        
        # Storage
        if any(word in description_lower for word in ["database", "postgres", "sql"]):
            suggestions.append(NODE_KNOWLEDGE["storage"]["postgres"])
        if any(word in description_lower for word in ["cache", "redis"]):
            suggestions.append(NODE_KNOWLEDGE["storage"]["redis"])
        
        return suggestions
    
    @staticmethod
    def generate_workflow_outline(description: str, suggested_nodes: List[Dict]) -> str:
        """Generate a workflow outline"""
        outline = f"# Workflow: {description}\n\n"
        outline += "## Suggested Structure:\n\n"
        
        for i, node in enumerate(suggested_nodes, 1):
            outline += f"{i}. **{node['name']}**\n"
            outline += f"   - Purpose: {node['desc']}\n"
            outline += f"   - Use Cases: {', '.join(node['use_cases'])}\n\n"
        
        outline += "\n## Best Practices:\n\n"
        for node in suggested_nodes:
            outline += f"### {node['name']}\n"
            for practice in node['best_practices']:
                outline += f"- {practice}\n"
            outline += "\n"
        
        return outline
    
    @staticmethod
    def analyze_workflow(workflow: Dict) -> Dict:
        """Analyze a workflow for potential issues"""
        issues = []
        suggestions = []
        nodes = workflow.get("nodes", [])
        
        # Check for common issues
        if not nodes:
            issues.append("Workflow has no nodes")
        
        # Check for missing error handling
        has_error_handling = any(
            node.get("type") == "n8n-nodes-base.errorTrigger" 
            for node in nodes
        )
        if not has_error_handling and len(nodes) > 3:
            suggestions.append("Consider adding error handling nodes")
        
        # Check for hardcoded values
        for node in nodes:
            node_str = json.dumps(node)
            if "password" in node_str.lower() and not "{{" in node_str:
                issues.append(f"Node '{node.get('name')}' may contain hardcoded credentials")
        
        # Check workflow structure
        if len(nodes) > 20:
            suggestions.append("Consider splitting into sub-workflows for better maintainability")
        
        # Check for proper naming
        default_names = ["Webhook", "HTTP Request", "Set", "IF"]
        unnamed_nodes = [
            node.get("name") for node in nodes 
            if node.get("name") in default_names
        ]
        if unnamed_nodes:
            suggestions.append(f"Consider renaming default node names: {', '.join(set(unnamed_nodes))}")
        
        return {
            "total_nodes": len(nodes),
            "issues": issues,
            "suggestions": suggestions,
            "complexity": "Low" if len(nodes) < 5 else "Medium" if len(nodes) < 15 else "High"
        }


def create_n8n_server(api_url: str, api_key: str) -> Server:
    """Create the n8n workflow builder MCP server"""

    server = Server("n8n-workflow-builder")
    n8n_client = N8nClient(api_url, api_key)
    workflow_builder = WorkflowBuilder()
    workflow_validator = WorkflowValidator()
    ai_feedback_analyzer = AIFeedbackAnalyzer()
    state_manager = StateManager()
    rbac_manager = RBACManager()
    
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available n8n workflow tools"""
        return [
            Tool(
                name="suggest_workflow_nodes",
                description=(
                    "🧠 AI-powered node suggestion based on workflow description. "
                    "Analyzes your workflow requirements and suggests the best n8n nodes to use, "
                    "including best practices and common pitfalls to avoid."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "Natural language description of what you want to build"
                        }
                    },
                    "required": ["description"]
                }
            ),
            Tool(
                name="generate_workflow_template",
                description=(
                    "🏗️ Generate a complete workflow template from description. "
                    "Creates a structured workflow outline with recommended nodes, connections, "
                    "and configuration tips."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "What the workflow should do"
                        },
                        "template_type": {
                            "type": "string",
                            "description": "Optional: api_endpoint, scheduled_report, data_sync",
                            "enum": ["api_endpoint", "scheduled_report", "data_sync", "custom"]
                        }
                    },
                    "required": ["description"]
                }
            ),
            Tool(
                name="analyze_workflow",
                description=(
                    "🔍 Analyze an existing workflow for issues and optimization opportunities. "
                    "Checks for common problems, security issues, and suggests improvements."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "string",
                            "description": "ID of the workflow to analyze"
                        }
                    },
                    "required": ["workflow_id"]
                }
            ),
            Tool(
                name="list_workflows",
                description=(
                    "📋 List all workflows with filtering options. "
                    "Get an overview of your workflows with status and basic info."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "active_only": {
                            "type": "boolean",
                            "description": "Only show active workflows",
                            "default": False
                        }
                    }
                }
            ),
            Tool(
                name="get_workflow_details",
                description=(
                    "📄 Get detailed information about a specific workflow including "
                    "all nodes, connections, and configuration."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "string",
                            "description": "Workflow ID"
                        }
                    },
                    "required": ["workflow_id"]
                }
            ),
            Tool(
                name="execute_workflow",
                description=(
                    "▶️ Execute a workflow with optional input data. "
                    "Trigger a workflow manually and get execution results."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "string",
                            "description": "Workflow ID to execute"
                        },
                        "input_data": {
                            "type": "object",
                            "description": "Optional input data as JSON"
                        }
                    },
                    "required": ["workflow_id"]
                }
            ),
            Tool(
                name="get_executions",
                description=(
                    "📊 Get execution history for workflows. "
                    "View past executions with status, duration, and error info. "
                    "Note: This returns summary data only. Use get_execution_details for full node data."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "string",
                            "description": "Optional: Filter by workflow ID"
                        },
                        "limit": {
                            "type": "number",
                            "description": "Number of executions to return (default: 10)",
                            "default": 10
                        }
                    }
                }
            ),
            Tool(
                name="get_execution_details",
                description=(
                    "🔍 Get detailed execution data including all node inputs and outputs. "
                    "Use this to see what data each node processed during an execution."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "execution_id": {
                            "type": "string",
                            "description": "Execution ID to get details for"
                        }
                    },
                    "required": ["execution_id"]
                }
            ),
            Tool(
                name="explain_node",
                description=(
                    "📚 Get detailed explanation of a specific n8n node type, "
                    "including use cases, configuration tips, and examples."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "node_type": {
                            "type": "string",
                            "description": "Node type (e.g., 'webhook', 'http_request', 'if', 'slack')"
                        }
                    },
                    "required": ["node_type"]
                }
            ),
            Tool(
                name="debug_workflow_error",
                description=(
                    "🐛 Help debug a workflow error. Analyzes error messages and "
                    "suggests potential fixes and troubleshooting steps."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "error_message": {
                            "type": "string",
                            "description": "The error message or description"
                        },
                        "node_type": {
                            "type": "string",
                            "description": "Optional: The node type where error occurred"
                        }
                    },
                    "required": ["error_message"]
                }
            ),
            Tool(
                name="update_workflow",
                description=(
                    "✏️ Update an existing workflow. Modify workflow properties like name, "
                    "nodes, connections, or settings. Can rename workflows or make structural changes. "
                    "Note: The 'active' field is read-only and cannot be changed via API - use the n8n UI instead."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "string",
                            "description": "ID of the workflow to update"
                        },
                        "name": {
                            "type": "string",
                            "description": "Optional: New name for the workflow"
                        },
                        "nodes": {
                            "type": "array",
                            "description": "Optional: Updated nodes array (full node structure)"
                        },
                        "connections": {
                            "type": "object",
                            "description": "Optional: Updated connections object"
                        },
                        "settings": {
                            "type": "object",
                            "description": "Optional: Workflow settings"
                        },
                        "tags": {
                            "type": "array",
                            "description": "Optional: Workflow tags"
                        }
                    },
                    "required": ["workflow_id"]
                }
            ),
            Tool(
                name="get_session_state",
                description=(
                    "🔄 Get current session state and context. "
                    "Shows the currently active workflow, recent workflows, and action history. "
                    "Use this to understand what you were working on."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="set_active_workflow",
                description=(
                    "📌 Set a workflow as the active/current workflow for the session. "
                    "This allows you to reference it later with 'current workflow' instead of IDs."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "string",
                            "description": "Workflow ID to set as active"
                        }
                    },
                    "required": ["workflow_id"]
                }
            ),
            Tool(
                name="get_active_workflow",
                description=(
                    "📍 Get the currently active workflow that was set via set_active_workflow. "
                    "Returns ID and name of the active workflow."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="get_recent_workflows",
                description=(
                    "📜 Get a list of recently accessed workflows. "
                    "Shows the last 10 workflows you worked with, ordered by most recent."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="get_session_history",
                description=(
                    "📝 Get recent action history for this session. "
                    "Shows what operations were performed recently."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "number",
                            "description": "Number of history entries to return (default: 10)",
                            "default": 10
                        }
                    }
                }
            ),
            Tool(
                name="clear_session_state",
                description=(
                    "🗑️ Clear all session state and history. "
                    "Resets the active workflow, recent workflows, and action history."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="validate_workflow",
                description=(
                    "✅ Validate a workflow before deployment. "
                    "Performs comprehensive validation: schema checks, semantic rules, "
                    "node parameter validation, security checks, and best practices. "
                    "Returns detailed errors and warnings."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "string",
                            "description": "Workflow ID to validate"
                        }
                    },
                    "required": ["workflow_id"]
                }
            ),
            Tool(
                name="validate_workflow_json",
                description=(
                    "✅ Validate a workflow from JSON structure. "
                    "Use this to validate a workflow before creating it. "
                    "Accepts raw workflow JSON and returns validation results."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workflow": {
                            "type": "object",
                            "description": "Workflow JSON object with nodes, connections, etc."
                        }
                    },
                    "required": ["workflow"]
                }
            ),
            Tool(
                name="analyze_execution_errors",
                description=(
                    "🔍 Analyze execution errors and provide AI-friendly feedback. "
                    "Examines failed workflow executions, identifies root causes, "
                    "and generates structured feedback with fix suggestions. "
                    "Perfect for debugging and learning from failures."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "execution_id": {
                            "type": "string",
                            "description": "Execution ID to analyze"
                        }
                    },
                    "required": ["execution_id"]
                }
            ),
            Tool(
                name="get_workflow_improvement_suggestions",
                description=(
                    "💡 Get improvement suggestions for a failed workflow. "
                    "Analyzes errors and generates specific recommendations "
                    "for fixing nodes, adding missing features, and improving reliability."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "execution_id": {
                            "type": "string",
                            "description": "Failed execution ID to analyze"
                        },
                        "workflow_id": {
                            "type": "string",
                            "description": "Workflow ID for context"
                        }
                    },
                    "required": ["execution_id", "workflow_id"]
                }
            ),
            Tool(
                name="rbac_get_status",
                description=(
                    "🔒 Get RBAC and security status report. "
                    "Shows users, roles, tenants, pending approvals, and recent audit log. "
                    "Use this to understand the current security configuration."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="rbac_add_user",
                description=(
                    "👤 Add a new user with specific role and tenant. "
                    "Creates a user account with assigned permissions based on role. "
                    "Roles: admin, developer, operator, viewer, auditor"
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "Username for the new user"
                        },
                        "role": {
                            "type": "string",
                            "description": "Role (admin, developer, operator, viewer, auditor)",
                            "enum": ["admin", "developer", "operator", "viewer", "auditor"]
                        },
                        "tenant_id": {
                            "type": "string",
                            "description": "Tenant ID (default: 'default')",
                            "default": "default"
                        }
                    },
                    "required": ["username", "role"]
                }
            ),
            Tool(
                name="rbac_get_user_info",
                description=(
                    "ℹ️ Get detailed information about a user. "
                    "Shows username, role, permissions, tenant, and creation date."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "Username to query"
                        }
                    },
                    "required": ["username"]
                }
            ),
            Tool(
                name="rbac_check_permission",
                description=(
                    "✅ Check if a user has a specific permission. "
                    "Validates whether the user's role grants access to an operation. "
                    "Examples: workflow.create, workflow.delete, approval.approve"
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "Username to check"
                        },
                        "permission": {
                            "type": "string",
                            "description": "Permission to check (e.g., 'workflow.create', 'approval.approve')"
                        }
                    },
                    "required": ["username", "permission"]
                }
            ),
            Tool(
                name="rbac_create_approval_request",
                description=(
                    "📝 Create an approval request for a critical operation. "
                    "Used when developer needs admin approval for operations like workflow.delete. "
                    "Returns approval_id for tracking."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "Username requesting approval"
                        },
                        "operation": {
                            "type": "string",
                            "description": "Operation requiring approval (workflow.delete, workflow.deploy_production, etc.)"
                        },
                        "details": {
                            "type": "object",
                            "description": "Additional details about the operation (workflow_id, reason, etc.)"
                        }
                    },
                    "required": ["username", "operation", "details"]
                }
            ),
            Tool(
                name="rbac_approve_request",
                description=(
                    "✅ Approve a pending approval request. "
                    "Admin approves a request from developer. Cannot approve own requests."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "approval_id": {
                            "type": "string",
                            "description": "Approval request ID to approve"
                        },
                        "approver": {
                            "type": "string",
                            "description": "Username of approver (must have approval.approve permission)"
                        }
                    },
                    "required": ["approval_id", "approver"]
                }
            ),
            Tool(
                name="rbac_reject_request",
                description=(
                    "❌ Reject a pending approval request. "
                    "Admin rejects a request with reason. Logged in audit trail."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "approval_id": {
                            "type": "string",
                            "description": "Approval request ID to reject"
                        },
                        "rejector": {
                            "type": "string",
                            "description": "Username of rejector"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for rejection"
                        }
                    },
                    "required": ["approval_id", "rejector"]
                }
            ),
            Tool(
                name="rbac_get_pending_approvals",
                description=(
                    "⏳ Get list of pending approval requests. "
                    "Shows all pending requests, or filtered by username if provided."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "Optional: Filter by username (shows requests by/for this user)"
                        }
                    }
                }
            ),
            Tool(
                name="rbac_create_tenant",
                description=(
                    "🏢 Create a new tenant for multi-tenant isolation. "
                    "Each tenant has separate workflows, users, and audit logs."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "tenant_id": {
                            "type": "string",
                            "description": "Unique tenant identifier (e.g., 'acme-corp')"
                        },
                        "name": {
                            "type": "string",
                            "description": "Display name for tenant (e.g., 'ACME Corporation')"
                        }
                    },
                    "required": ["tenant_id", "name"]
                }
            ),
            Tool(
                name="rbac_get_audit_log",
                description=(
                    "📋 Get audit log with optional filters. "
                    "Shows security-relevant actions (user created, workflow deleted, approvals, etc.). "
                    "Last 500 events stored, customizable retention."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "number",
                            "description": "Number of log entries to return (default: 50)",
                            "default": 50
                        },
                        "username": {
                            "type": "string",
                            "description": "Optional: Filter by username"
                        },
                        "action": {
                            "type": "string",
                            "description": "Optional: Filter by action type"
                        }
                    }
                }
            )
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: Any) -> list[TextContent]:
        """Handle tool calls"""
        
        try:
            if name == "suggest_workflow_nodes":
                description = arguments["description"]
                suggestions = workflow_builder.suggest_nodes(description)
                
                if not suggestions:
                    return [TextContent(
                        type="text",
                        text="I couldn't find specific nodes for this description. "
                             "Please describe in more detail what the workflow should do!"
                    )]
                
                outline = workflow_builder.generate_workflow_outline(description, suggestions)
                return [TextContent(type="text", text=outline)]
            
            elif name == "generate_workflow_template":
                description = arguments["description"]
                template_type = arguments.get("template_type", "custom")
                
                suggestions = workflow_builder.suggest_nodes(description)
                outline = workflow_builder.generate_workflow_outline(description, suggestions)
                
                # Add template-specific guidance
                if template_type in WORKFLOW_TEMPLATES:
                    template = WORKFLOW_TEMPLATES[template_type]
                    outline += f"\n## Template: {template['name']}\n\n"
                    outline += "Recommended Node Structure:\n"
                    for i, node in enumerate(template['nodes'], 1):
                        outline += f"{i}. {node['name']} ({node['type']})\n"
                
                return [TextContent(type="text", text=outline)]
            
            elif name == "analyze_workflow":
                workflow_id = arguments["workflow_id"]
                workflow = await n8n_client.get_workflow(workflow_id)
                analysis = workflow_builder.analyze_workflow(workflow)

                # Set as current and log
                state_manager.set_current_workflow(workflow['id'], workflow['name'])
                state_manager.log_action("analyze_workflow", {"workflow_id": workflow_id, "complexity": analysis['complexity']})

                result = f"# Workflow Analysis: {workflow.get('name', workflow_id)}\n\n"
                result += f"**Complexity:** {analysis['complexity']}\n"
                result += f"**Total Nodes:** {analysis['total_nodes']}\n\n"

                if analysis['issues']:
                    result += "## ⚠️ Issues Found:\n\n"
                    for issue in analysis['issues']:
                        result += f"- {issue}\n"
                    result += "\n"

                if analysis['suggestions']:
                    result += "## 💡 Suggestions:\n\n"
                    for suggestion in analysis['suggestions']:
                        result += f"- {suggestion}\n"

                if not analysis['issues'] and not analysis['suggestions']:
                    result += "✅ Workflow looks good! No major issues found.\n"

                return [TextContent(type="text", text=result)]
            
            elif name == "list_workflows":
                active_only = arguments.get("active_only", False)
                workflows = await n8n_client.get_workflows(active_only)
                
                result = f"# Workflows ({len(workflows)} total)\n\n"
                for wf in workflows:
                    status = "🟢" if wf.get("active") else "⚪"
                    result += f"{status} **{wf['name']}**\n"
                    result += f"   ID: `{wf['id']}`\n"
                    result += f"   Nodes: {len(wf.get('nodes', []))}\n"
                    result += f"   Updated: {wf.get('updatedAt', 'N/A')}\n\n"
                
                return [TextContent(type="text", text=result)]
            
            elif name == "get_workflow_details":
                workflow_id = arguments["workflow_id"]
                workflow = await n8n_client.get_workflow(workflow_id)

                # Set as current workflow and log action
                state_manager.set_current_workflow(workflow['id'], workflow['name'])
                state_manager.log_action("get_workflow_details", {"workflow_id": workflow_id, "workflow_name": workflow['name']})

                result = f"# Workflow: {workflow['name']}\n\n"
                result += f"**ID:** {workflow['id']}\n"
                result += f"**Active:** {'Yes' if workflow.get('active') else 'No'}\n"
                result += f"**Nodes:** {len(workflow.get('nodes', []))}\n\n"

                result += "## Nodes:\n\n"
                for node in workflow.get('nodes', []):
                    result += f"- **{node['name']}** ({node['type']})\n"

                return [TextContent(type="text", text=result)]
            
            elif name == "execute_workflow":
                workflow_id = arguments["workflow_id"]
                input_data = arguments.get("input_data")

                execution = await n8n_client.execute_workflow(workflow_id, input_data)

                # Log execution
                execution_id = execution.get('id', 'N/A')
                state_manager.set_last_execution(execution_id)
                state_manager.log_action("execute_workflow", {"workflow_id": workflow_id, "execution_id": execution_id})

                result = f"# Workflow Execution\n\n"
                result += f"**Execution ID:** {execution_id}\n"
                result += f"**Status:** {execution.get('finished', 'Running')}\n"
                result += f"**Data:** {json.dumps(execution.get('data', {}), indent=2)}\n"

                return [TextContent(type="text", text=result)]
            
            elif name == "get_executions":
                workflow_id = arguments.get("workflow_id")
                limit = arguments.get("limit", 10)
                
                executions = await n8n_client.get_executions(workflow_id, limit)
                
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

            elif name == "get_execution_details":
                execution_id = arguments["execution_id"]

                execution = await n8n_client.get_execution(execution_id)

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

            elif name == "explain_node":
                node_type = arguments["node_type"].lower()
                
                # Search in knowledge base
                explanation = None
                for category in NODE_KNOWLEDGE.values():
                    if node_type in category:
                        explanation = category[node_type]
                        break
                
                if not explanation:
                    return [TextContent(
                        type="text",
                        text=f"Node type '{node_type}' not found in knowledge base. "
                             f"Try: {', '.join(list(NODE_KNOWLEDGE['triggers'].keys()) + list(NODE_KNOWLEDGE['logic'].keys()))}"
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
            
            elif name == "debug_workflow_error":
                error_msg = arguments["error_message"]
                node_type = arguments.get("node_type", "").lower()
                
                debug_info = f"# Workflow Error Debug\n\n"
                debug_info += f"**Error Message:** {error_msg}\n\n"
                
                # Common error patterns
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
                    debug_info += "1. Check node configuration\n"
                    debug_info += "2. Verify input data format\n"
                    debug_info += "3. Enable workflow logging\n"
                    debug_info += "4. Test with minimal data\n"
                    debug_info += "5. Check n8n logs for details\n"
                
                return [TextContent(type="text", text=debug_info)]

            elif name == "update_workflow":
                workflow_id = arguments["workflow_id"]

                # Build updates dictionary from provided arguments
                updates = {}
                if "name" in arguments:
                    updates["name"] = arguments["name"]
                if "active" in arguments:
                    updates["active"] = arguments["active"]
                if "nodes" in arguments:
                    updates["nodes"] = arguments["nodes"]
                if "connections" in arguments:
                    updates["connections"] = arguments["connections"]
                if "settings" in arguments:
                    updates["settings"] = arguments["settings"]
                if "tags" in arguments:
                    updates["tags"] = arguments["tags"]

                if not updates:
                    return [TextContent(
                        type="text",
                        text="No updates provided. Please specify at least one field to update (name, active, nodes, connections, settings, or tags)."
                    )]

                # Update the workflow
                updated_workflow = await n8n_client.update_workflow(workflow_id, updates)

                result = f"# Workflow Updated Successfully\n\n"
                result += f"**ID:** {updated_workflow.get('id', 'N/A')}\n"
                result += f"**Name:** {updated_workflow.get('name', 'N/A')}\n"
                result += f"**Active:** {'✅ Yes' if updated_workflow.get('active') else '❌ No'}\n"
                result += f"**Nodes:** {len(updated_workflow.get('nodes', []))}\n"
                result += f"**Updated:** {updated_workflow.get('updatedAt', 'N/A')}\n\n"

                result += "## Changes Applied:\n\n"
                for key, value in updates.items():
                    if key in ["nodes", "connections"]:
                        result += f"- **{key}:** Updated structure\n"
                    elif key == "active":
                        result += f"- **{key}:** {'Enabled' if value else 'Disabled'}\n"
                    else:
                        result += f"- **{key}:** {value}\n"

                return [TextContent(type="text", text=result)]

            elif name == "get_session_state":
                result = state_manager.get_state_summary()
                return [TextContent(type="text", text=result)]

            elif name == "set_active_workflow":
                workflow_id = arguments["workflow_id"]

                # Fetch workflow to get its name
                workflow = await n8n_client.get_workflow(workflow_id)
                state_manager.set_current_workflow(workflow['id'], workflow['name'])
                state_manager.log_action("set_active_workflow", {"workflow_id": workflow_id, "workflow_name": workflow['name']})

                result = f"✅ Set active workflow: **{workflow['name']}** (`{workflow['id']}`)\n\n"
                result += "You can now reference this workflow as the 'current workflow' in future prompts."

                return [TextContent(type="text", text=result)]

            elif name == "get_active_workflow":
                current = state_manager.get_current_workflow()

                if not current:
                    return [TextContent(
                        type="text",
                        text="No active workflow set. Use `set_active_workflow` to set one."
                    )]

                result = f"# Active Workflow\n\n"
                result += f"**Name:** {current['name']}\n"
                result += f"**ID:** `{current['id']}`\n"

                return [TextContent(type="text", text=result)]

            elif name == "get_recent_workflows":
                recent = state_manager.get_recent_workflows()

                if not recent:
                    return [TextContent(
                        type="text",
                        text="No recent workflows. Start working with workflows to see them here."
                    )]

                result = f"# Recent Workflows ({len(recent)})\n\n"
                for wf in recent:
                    result += f"- **{wf['name']}** (`{wf['id']}`)\n"
                    result += f"  Last accessed: {wf['accessed_at']}\n\n"

                return [TextContent(type="text", text=result)]

            elif name == "get_session_history":
                limit = arguments.get("limit", 10)
                history = state_manager.get_session_history(limit)

                if not history:
                    return [TextContent(
                        type="text",
                        text="No session history yet. Actions will be logged here as you use the tools."
                    )]

                result = f"# Session History (Last {len(history)} actions)\n\n"
                for entry in reversed(history):
                    result += f"**{entry['timestamp']}**\n"
                    result += f"- Action: `{entry['action']}`\n"
                    if entry.get('details'):
                        details_str = ", ".join([f"{k}={v}" for k, v in entry['details'].items()])
                        result += f"- Details: {details_str}\n"
                    result += "\n"

                return [TextContent(type="text", text=result)]

            elif name == "clear_session_state":
                state_manager.clear_state()

                result = "✅ Session state cleared!\n\n"
                result += "All context has been reset:\n"
                result += "- Active workflow: None\n"
                result += "- Recent workflows: Cleared\n"
                result += "- Session history: Cleared\n"

                return [TextContent(type="text", text=result)]

            elif name == "validate_workflow":
                workflow_id = arguments["workflow_id"]

                # Fetch workflow
                workflow = await n8n_client.get_workflow(workflow_id)

                # Run validation
                validation_result = workflow_validator.validate_workflow_full(workflow)

                # Log action
                state_manager.log_action("validate_workflow", {
                    "workflow_id": workflow_id,
                    "valid": validation_result['valid'],
                    "errors": validation_result['summary']['total_errors'],
                    "warnings": validation_result['summary']['total_warnings']
                })

                # Format result
                result = f"# Workflow Validation: {workflow['name']}\n\n"

                if validation_result['valid']:
                    result += "## ✅ Validation Passed\n\n"
                    result += f"**Status:** Ready for deployment\n"
                    result += f"**Total Warnings:** {validation_result['summary']['total_warnings']}\n\n"
                else:
                    result += "## ❌ Validation Failed\n\n"
                    result += f"**Status:** Cannot deploy - fix errors first\n"
                    result += f"**Total Errors:** {validation_result['summary']['total_errors']}\n"
                    result += f"**Total Warnings:** {validation_result['summary']['total_warnings']}\n\n"

                # Show summary breakdown
                result += "### Validation Summary:\n\n"
                result += f"- Schema errors: {validation_result['summary']['schema_errors']}\n"
                result += f"- Semantic errors: {validation_result['summary']['semantic_errors']}\n"
                result += f"- Parameter errors: {validation_result['summary']['parameter_errors']}\n\n"

                # Show errors
                if validation_result['errors']:
                    result += "## 🔴 Errors (must fix):\n\n"
                    for idx, error in enumerate(validation_result['errors'], 1):
                        result += f"{idx}. {error}\n"
                    result += "\n"

                # Show warnings
                if validation_result['warnings']:
                    result += "## ⚠️ Warnings (should fix):\n\n"
                    for idx, warning in enumerate(validation_result['warnings'], 1):
                        result += f"{idx}. {warning}\n"
                    result += "\n"

                if validation_result['valid'] and not validation_result['warnings']:
                    result += "🎉 Perfect! No errors or warnings found.\n"

                return [TextContent(type="text", text=result)]

            elif name == "validate_workflow_json":
                workflow = arguments["workflow"]

                # Run validation
                validation_result = workflow_validator.validate_workflow_full(workflow)

                # Log action
                state_manager.log_action("validate_workflow_json", {
                    "workflow_name": workflow.get('name', 'Unknown'),
                    "valid": validation_result['valid'],
                    "errors": validation_result['summary']['total_errors'],
                    "warnings": validation_result['summary']['total_warnings']
                })

                # Format result
                result = f"# Workflow Validation: {workflow.get('name', 'Unnamed')}\n\n"

                if validation_result['valid']:
                    result += "## ✅ Validation Passed\n\n"
                    result += f"**Status:** Safe to create/deploy\n"
                    result += f"**Total Warnings:** {validation_result['summary']['total_warnings']}\n\n"
                else:
                    result += "## ❌ Validation Failed\n\n"
                    result += f"**Status:** Fix errors before creating workflow\n"
                    result += f"**Total Errors:** {validation_result['summary']['total_errors']}\n"
                    result += f"**Total Warnings:** {validation_result['summary']['total_warnings']}\n\n"

                # Show summary breakdown
                result += "### Validation Summary:\n\n"
                result += f"- Schema errors: {validation_result['summary']['schema_errors']}\n"
                result += f"- Semantic errors: {validation_result['summary']['semantic_errors']}\n"
                result += f"- Parameter errors: {validation_result['summary']['parameter_errors']}\n\n"

                # Show errors
                if validation_result['errors']:
                    result += "## 🔴 Errors (must fix):\n\n"
                    for idx, error in enumerate(validation_result['errors'], 1):
                        result += f"{idx}. {error}\n"
                    result += "\n"

                # Show warnings
                if validation_result['warnings']:
                    result += "## ⚠️ Warnings (should fix):\n\n"
                    for idx, warning in enumerate(validation_result['warnings'], 1):
                        result += f"{idx}. {warning}\n"
                    result += "\n"

                if validation_result['valid'] and not validation_result['warnings']:
                    result += "🎉 Perfect! No errors or warnings found.\n"

                return [TextContent(type="text", text=result)]

            elif name == "analyze_execution_errors":
                execution_id = arguments["execution_id"]

                # Get execution details
                execution = await n8n_client.get_execution(execution_id)

                # Get workflow for context (if available)
                workflow = None
                workflow_data = execution.get('workflowData')
                if workflow_data:
                    workflow_id = workflow_data.get('id')
                    if workflow_id:
                        try:
                            workflow = await n8n_client.get_workflow(workflow_id)
                        except:
                            pass

                # Analyze errors
                feedback = ai_feedback_analyzer.analyze_execution_error(execution, workflow)

                # Log action
                state_manager.log_action("analyze_execution_errors", {
                    "execution_id": execution_id,
                    "has_errors": feedback['has_errors'],
                    "root_cause": feedback.get('root_cause'),
                    "error_count": len(feedback.get('errors', []))
                })

                # Format feedback
                workflow_name = workflow.get('name') if workflow else workflow_data.get('name', 'Unknown') if workflow_data else 'Unknown'
                result = ai_feedback_analyzer.format_ai_feedback(feedback, workflow_name)

                return [TextContent(type="text", text=result)]

            elif name == "get_workflow_improvement_suggestions":
                execution_id = arguments["execution_id"]
                workflow_id = arguments["workflow_id"]

                # Get execution and workflow
                execution = await n8n_client.get_execution(execution_id)
                workflow = await n8n_client.get_workflow(workflow_id)

                # Analyze errors
                feedback = ai_feedback_analyzer.analyze_execution_error(execution, workflow)

                # Generate improvement suggestions
                improvements = ai_feedback_analyzer.generate_fix_workflow(feedback, workflow)

                # Log action
                state_manager.log_action("get_workflow_improvement_suggestions", {
                    "execution_id": execution_id,
                    "workflow_id": workflow_id,
                    "root_cause": improvements.get('root_cause'),
                    "nodes_to_modify": len(improvements.get('nodes_to_modify', [])),
                    "nodes_to_add": len(improvements.get('nodes_to_add', []))
                })

                # Format result
                result = f"# 💡 Workflow Improvement Suggestions: {workflow['name']}\n\n"

                result += f"**Root Cause:** {improvements['root_cause']}\n\n"

                # Original issues
                if improvements['original_issues']:
                    result += "## 🔴 Original Issues:\n\n"
                    for idx, error in enumerate(improvements['original_issues'], 1):
                        result += f"{idx}. **{error['node']}**: {error['message']}\n"
                    result += "\n"

                # Nodes to modify
                if improvements['nodes_to_modify']:
                    result += "## 🔧 Nodes to Modify:\n\n"
                    for node_mod in improvements['nodes_to_modify']:
                        result += f"### `{node_mod['node_name']}` ({node_mod['node_type']})\n\n"
                        for change in node_mod['changes']:
                            result += f"**{change['field']}:**\n"
                            result += f"- Current: `{change.get('current', 'Not set')}`\n"
                            result += f"- Suggested: `{change.get('suggested', change.get('suggestion'))}`\n"
                            result += f"- Reason: {change['reason']}\n\n"

                # Nodes to add
                if improvements['nodes_to_add']:
                    result += "## ➕ Nodes to Add:\n\n"
                    for node_add in improvements['nodes_to_add']:
                        result += f"### `{node_add['name']}` ({node_add['type']})\n"
                        result += f"- Reason: {node_add['reason']}\n"
                        if 'parameters' in node_add:
                            result += f"- Parameters: `{json.dumps(node_add['parameters'])}`\n"
                        result += "\n"

                # Recommended changes
                if improvements['recommended_changes']:
                    result += "## 📋 Recommended Changes:\n\n"
                    for idx, change in enumerate(improvements['recommended_changes'], 1):
                        result += f"{idx}. {change}\n"

                return [TextContent(type="text", text=result)]

            elif name == "rbac_get_status":
                report = rbac_manager.generate_rbac_report()
                return [TextContent(type="text", text=report)]

            elif name == "rbac_add_user":
                username = arguments["username"]
                role = arguments["role"]
                tenant_id = arguments.get("tenant_id", "default")

                result_data = rbac_manager.add_user(username, role, tenant_id)

                if not result_data["success"]:
                    return [TextContent(type="text", text=f"❌ Failed to add user: {result_data['error']}")]

                user = result_data["user"]
                result = f"✅ User created successfully!\n\n"
                result += f"**Username:** {user['username']}\n"
                result += f"**Role:** {role}\n"
                result += f"**Tenant:** {tenant_id}\n"
                result += f"**Created:** {user['created_at']}\n"

                return [TextContent(type="text", text=result)]

            elif name == "rbac_get_user_info":
                username = arguments["username"]
                user_info = rbac_manager.get_user_info(username)

                if not user_info:
                    return [TextContent(type="text", text=f"❌ User '{username}' not found")]

                result = f"# User Information: {username}\n\n"
                result += f"**Role:** {user_info['role_name']} ({user_info['role']})\n"
                result += f"**Tenant:** {user_info['tenant_id']}\n"
                result += f"**Created:** {user_info['created_at']}\n\n"
                result += f"## Permissions ({len(user_info['permissions'])}):\n\n"
                for perm in user_info['permissions']:
                    result += f"- {perm}\n"
                result += f"\n**Description:** {user_info['role_description']}\n"

                return [TextContent(type="text", text=result)]

            elif name == "rbac_check_permission":
                username = arguments["username"]
                permission = arguments["permission"]

                has_permission = rbac_manager.check_permission(username, permission)

                if has_permission:
                    result = f"✅ User '{username}' HAS permission: `{permission}`"
                else:
                    result = f"❌ User '{username}' DOES NOT HAVE permission: `{permission}`"

                return [TextContent(type="text", text=result)]

            elif name == "rbac_create_approval_request":
                username = arguments["username"]
                operation = arguments["operation"]
                details = arguments["details"]

                approval_id = rbac_manager.create_approval_request(username, operation, details)

                result = f"📝 Approval request created!\n\n"
                result += f"**Approval ID:** `{approval_id}`\n"
                result += f"**Operation:** {operation}\n"
                result += f"**Requested by:** {username}\n"
                result += f"**Status:** Pending\n\n"
                result += "This request needs approval from an admin before the operation can proceed."

                return [TextContent(type="text", text=result)]

            elif name == "rbac_approve_request":
                approval_id = arguments["approval_id"]
                approver = arguments["approver"]

                result_data = rbac_manager.approve_request(approval_id, approver)

                if not result_data["success"]:
                    return [TextContent(type="text", text=f"❌ Failed to approve: {result_data['error']}")]

                approval = result_data["approval"]
                result = f"✅ Approval request APPROVED!\n\n"
                result += f"**Approval ID:** `{approval['id']}`\n"
                result += f"**Operation:** {approval['operation']}\n"
                result += f"**Requested by:** {approval['username']}\n"
                result += f"**Approved by:** {approver}\n"
                result += f"**Approved at:** {approval['approved_at']}\n\n"
                result += "The operation can now proceed."

                return [TextContent(type="text", text=result)]

            elif name == "rbac_reject_request":
                approval_id = arguments["approval_id"]
                rejector = arguments["rejector"]
                reason = arguments.get("reason", "No reason provided")

                result_data = rbac_manager.reject_request(approval_id, rejector, reason)

                if not result_data["success"]:
                    return [TextContent(type="text", text=f"❌ Failed to reject: {result_data['error']}")]

                approval = result_data["approval"]
                result = f"❌ Approval request REJECTED\n\n"
                result += f"**Approval ID:** `{approval['id']}`\n"
                result += f"**Operation:** {approval['operation']}\n"
                result += f"**Requested by:** {approval['username']}\n"
                result += f"**Rejected by:** {rejector}\n"
                result += f"**Rejected at:** {approval['approved_at']}\n"
                result += f"**Reason:** {reason}\n"

                return [TextContent(type="text", text=result)]

            elif name == "rbac_get_pending_approvals":
                username = arguments.get("username")
                pending = rbac_manager.get_pending_approvals(username)

                if not pending:
                    result = "✅ No pending approval requests"
                    if username:
                        result += f" for user '{username}'"
                    return [TextContent(type="text", text=result)]

                result = f"# Pending Approval Requests ({len(pending)})\n\n"
                for approval in pending:
                    result += f"## `{approval['id']}`\n\n"
                    result += f"**Operation:** {approval['operation']}\n"
                    result += f"**Requested by:** {approval['username']}\n"
                    result += f"**Created:** {approval['created_at']}\n"
                    if approval.get('details'):
                        result += f"**Details:** {json.dumps(approval['details'], indent=2)}\n"
                    result += "\n"

                return [TextContent(type="text", text=result)]

            elif name == "rbac_create_tenant":
                tenant_id = arguments["tenant_id"]
                name = arguments["name"]

                result_data = rbac_manager.create_tenant(tenant_id, name)

                if not result_data["success"]:
                    return [TextContent(type="text", text=f"❌ Failed to create tenant: {result_data['error']}")]

                tenant = result_data["tenant"]
                result = f"✅ Tenant created successfully!\n\n"
                result += f"**Tenant ID:** `{tenant['tenant_id']}`\n"
                result += f"**Name:** {tenant['name']}\n"
                result += f"**Created:** {tenant['created_at']}\n\n"
                result += "You can now add users to this tenant."

                return [TextContent(type="text", text=result)]

            elif name == "rbac_get_audit_log":
                limit = arguments.get("limit", 50)
                username = arguments.get("username")
                action = arguments.get("action")

                logs = rbac_manager.get_audit_log(limit, username, action)

                if not logs:
                    result = "📋 No audit log entries found"
                    if username:
                        result += f" for user '{username}'"
                    if action:
                        result += f" with action '{action}'"
                    return [TextContent(type="text", text=result)]

                result = f"# Audit Log ({len(logs)} entries)\n\n"
                for log in reversed(logs):
                    result += f"**{log['timestamp']}**\n"
                    result += f"- User: `{log['username']}`\n"
                    result += f"- Action: `{log['action']}`\n"
                    if log.get('details'):
                        details_str = ", ".join([f"{k}={v}" for k, v in log['details'].items()])
                        result += f"- Details: {details_str}\n"
                    result += "\n"

                return [TextContent(type="text", text=result)]

            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]
        
        except Exception as e:
            logger.error(f"Error in tool {name}: {e}")
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    return server


async def main():
    """Main entry point"""
    import sys
    
    # Get configuration from environment
    api_url = os.getenv("N8N_API_URL")
    api_key = os.getenv("N8N_API_KEY")
    
    if not api_url or not api_key:
        logger.error("N8N_API_URL and N8N_API_KEY environment variables must be set")
        sys.exit(1)
    
    logger.info(f"Starting n8n Workflow Builder MCP Server... (API: {api_url})")
    server = create_n8n_server(api_url, api_key)
    
    # Run the server
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
