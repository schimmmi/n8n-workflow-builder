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
from typing import Any, Dict, List, Optional
from datetime import datetime

import httpx
from mcp.server import Server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("n8n-workflow-builder")

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
                
                result = f"# Workflow Execution\n\n"
                result += f"**Execution ID:** {execution.get('id', 'N/A')}\n"
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
