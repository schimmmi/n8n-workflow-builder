#!/usr/bin/env python3
"""
n8n Workflow Builder MCP Server
Advanced MCP server for n8n workflow creation, optimization, and management
"""
import asyncio
import json
import logging
import os
from typing import Any

from mcp.server import Server
from mcp.types import Tool, TextContent

# Import all components from refactored modules
from .client import N8nClient
from .state import StateManager
from .validators.workflow_validator import WorkflowValidator
from .validators.semantic_analyzer import SemanticWorkflowAnalyzer
from .analyzers.feedback_analyzer import AIFeedbackAnalyzer
from .security.rbac import RBACManager
from .templates.recommender import TemplateRecommendationEngine, WORKFLOW_TEMPLATES
from .builders.workflow_builder import WorkflowBuilder, NODE_KNOWLEDGE

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("n8n-workflow-builder")


def create_n8n_server(api_url: str, api_key: str) -> Server:
    """Create the n8n workflow builder MCP server"""

    server = Server("n8n-workflow-builder")
    n8n_client = N8nClient(api_url, api_key)
    workflow_builder = WorkflowBuilder()
    workflow_validator = WorkflowValidator()
    semantic_analyzer = SemanticWorkflowAnalyzer()
    ai_feedback_analyzer = AIFeedbackAnalyzer()
    state_manager = StateManager()
    rbac_manager = RBACManager()
    template_engine = TemplateRecommendationEngine()
    

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
                name="analyze_workflow_semantics",
                description=(
                    "🔬 Deep semantic analysis of workflow logic and patterns. "
                    "Goes beyond schema validation to detect anti-patterns, logic errors, "
                    "security issues, and performance problems. Provides LLM-friendly fix suggestions. "
                    "Checks: HTTP retry patterns, loop completeness, timezone config, IF node paths, "
                    "webhook security, infinite loops, credential usage, N+1 queries, rate limiting, "
                    "data validation, and more. Returns copy-paste ready code fixes."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "string",
                            "description": "Workflow ID to analyze"
                        }
                    },
                    "required": ["workflow_id"]
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
            ),
            Tool(
                name="recommend_templates",
                description=(
                    "🎯 Get AI-powered template recommendations based on workflow description and goal. "
                    "Uses advanced relevance scoring to suggest the best templates for your use case. "
                    "Returns templates with match scores and detailed information."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "Description of the workflow you want to build"
                        },
                        "workflow_goal": {
                            "type": "string",
                            "description": "Optional: Specific goal or objective of the workflow"
                        },
                        "min_score": {
                            "type": "number",
                            "description": "Minimum relevance score (0.0-1.0, default: 0.3)",
                            "default": 0.3
                        },
                        "max_results": {
                            "type": "number",
                            "description": "Maximum number of recommendations (default: 5)",
                            "default": 5
                        }
                    },
                    "required": ["description"]
                }
            ),
            Tool(
                name="get_template_library",
                description=(
                    "📚 Get comprehensive template library report. "
                    "Shows all available templates grouped by category and difficulty, "
                    "with full descriptions, use cases, and metadata."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="search_templates",
                description=(
                    "🔍 Search templates by keyword or phrase. "
                    "Searches across template names, descriptions, tags, and use cases. "
                    "Great for finding templates when you know what you're looking for."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (e.g., 'email', 'database sync', 'notification')"
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="get_templates_by_category",
                description=(
                    "📁 Get all templates in a specific category. "
                    "Categories: api, reporting, integration, communication, data_pipeline, "
                    "monitoring, notification, file_processing"
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "Category name",
                            "enum": ["api", "reporting", "integration", "communication",
                                   "data_pipeline", "monitoring", "notification", "file_processing"]
                        }
                    },
                    "required": ["category"]
                }
            ),
            Tool(
                name="get_templates_by_difficulty",
                description=(
                    "📊 Get templates filtered by difficulty level. "
                    "Helps find templates appropriate for your skill level."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "difficulty": {
                            "type": "string",
                            "description": "Difficulty level",
                            "enum": ["beginner", "intermediate", "advanced"]
                        }
                    },
                    "required": ["difficulty"]
                }
            ),
            Tool(
                name="get_template_details",
                description=(
                    "📄 Get detailed information about a specific template. "
                    "Shows full template structure, nodes, estimated time, and implementation guide."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "template_id": {
                            "type": "string",
                            "description": "Template ID (e.g., 'api_endpoint', 'data_sync', 'email_automation')"
                        }
                    },
                    "required": ["template_id"]
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

            elif name == "analyze_workflow_semantics":
                workflow_id = arguments["workflow_id"]

                # Fetch workflow
                workflow = await n8n_client.get_workflow(workflow_id)
                workflow_name = workflow.get('name', 'Unnamed Workflow')

                # Run semantic analysis
                analysis = semantic_analyzer.analyze_workflow_semantics(workflow)

                # Log action
                state_manager.log_action("analyze_workflow_semantics", {
                    "workflow_id": workflow_id,
                    "workflow_name": workflow_name,
                    "total_issues": sum(analysis['severity'].values()),
                    "critical": analysis['severity']['critical'],
                    "high": analysis['severity']['high']
                })

                # Format report
                report = semantic_analyzer.format_analysis_report(analysis, workflow_name)

                return [TextContent(type="text", text=report)]

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

            elif name == "recommend_templates":
                description = arguments["description"]
                workflow_goal = arguments.get("workflow_goal")
                min_score = arguments.get("min_score", 0.3)
                max_results = arguments.get("max_results", 5)

                recommendations = template_engine.recommend_templates(
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

            elif name == "get_template_library":
                report = template_engine.generate_template_report()
                return [TextContent(type="text", text=report)]

            elif name == "search_templates":
                query = arguments["query"]
                results = template_engine.search_templates(query)

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

            elif name == "get_templates_by_category":
                category = arguments["category"]
                templates = template_engine.get_templates_by_category(category)

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

            elif name == "get_templates_by_difficulty":
                difficulty = arguments["difficulty"]
                templates = template_engine.get_templates_by_difficulty(difficulty)

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

            elif name == "get_template_details":
                template_id = arguments["template_id"]

                if template_id not in WORKFLOW_TEMPLATES:
                    available = ", ".join(WORKFLOW_TEMPLATES.keys())
                    return [TextContent(
                        type="text",
                        text=f"❌ Template '{template_id}' not found.\n\nAvailable templates: {available}"
                    )]

                template = WORKFLOW_TEMPLATES[template_id]

                result = f"# 📄 Template Details: {template['name']}\n\n"
                result += f"**Template ID:** `{template_id}`\n"
                result += f"**Category:** {template.get('category', 'N/A')}\n"
                result += f"**Difficulty:** {template.get('difficulty', 'N/A')}\n"
                result += f"**Estimated Time:** {template.get('estimated_time', 'N/A')}\n\n"
                result += f"## Description\n\n{template.get('description', 'N/A')}\n\n"

                result += f"## Use Cases\n\n"
                for uc in template.get('use_cases', []):
                    result += f"- {uc}\n"
                result += "\n"

                result += f"## Node Structure\n\n"
                for idx, node in enumerate(template.get('nodes', []), 1):
                    result += f"{idx}. **{node['name']}** (`{node['type']}`)\n"
                result += "\n"

                result += f"## Tags\n\n"
                result += ", ".join(f"`{tag}`" for tag in template.get('tags', []))
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
