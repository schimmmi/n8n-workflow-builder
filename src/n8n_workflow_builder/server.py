#!/usr/bin/env python3
"""
n8n Workflow Builder MCP Server
Advanced MCP server for n8n workflow creation, optimization, and management
"""
import sys
print("DEBUG: Starting server.py imports", file=sys.stderr, flush=True)

import asyncio
import json
import logging
import os
from typing import Any

print("DEBUG: Basic imports done", file=sys.stderr, flush=True)

from mcp.server import Server
from mcp.types import Tool, TextContent

print("DEBUG: MCP imports done", file=sys.stderr, flush=True)

# Import all components from refactored modules
print("DEBUG: Starting module imports", file=sys.stderr, flush=True)
from .client import N8nClient
print("DEBUG: N8nClient imported", file=sys.stderr, flush=True)
from .state import StateManager
print("DEBUG: StateManager imported", file=sys.stderr, flush=True)
from .validators.workflow_validator import WorkflowValidator
print("DEBUG: WorkflowValidator imported", file=sys.stderr, flush=True)
from .validators.semantic_analyzer import SemanticWorkflowAnalyzer
print("DEBUG: SemanticWorkflowAnalyzer imported", file=sys.stderr, flush=True)
from .analyzers.feedback_analyzer import AIFeedbackAnalyzer
print("DEBUG: AIFeedbackAnalyzer imported", file=sys.stderr, flush=True)
from .security.rbac import RBACManager
print("DEBUG: RBACManager imported", file=sys.stderr, flush=True)
from .templates.recommender import TemplateRecommendationEngine, WORKFLOW_TEMPLATES
print("DEBUG: TemplateRecommendationEngine imported", file=sys.stderr, flush=True)
from .builders.workflow_builder import WorkflowBuilder, NODE_KNOWLEDGE
print("DEBUG: WorkflowBuilder imported", file=sys.stderr, flush=True)
from .intent import IntentManager
print("DEBUG: IntentManager imported", file=sys.stderr, flush=True)
from .execution.error_analyzer import (
    ExecutionMonitor,
    ErrorContextExtractor,
    ErrorSimplifier,
    FeedbackGenerator
)
print("DEBUG: error_analyzer imported", file=sys.stderr, flush=True)
from .drift.detector import (
    DriftDetector,
    DriftPatternAnalyzer,
    DriftRootCauseAnalyzer,
    DriftFixSuggester
)
print("DEBUG: drift.detector imported", file=sys.stderr, flush=True)
from .explainability import (
    WorkflowExplainer,
    WorkflowPurposeAnalyzer,
    DataFlowTracer,
    DependencyMapper,
    RiskAnalyzer,
    ExplainabilityFormatter
)
print("DEBUG: explainability imported", file=sys.stderr, flush=True)
from .changes import (
    WorkflowDiffEngine,
    ChangeImpactAnalyzer,
    DryRunSimulator,
    ApprovalWorkflow,
    ChangeFormatter
)
print("DEBUG: changes imported", file=sys.stderr, flush=True)
from .templates import (
    TemplateRegistry,
    TemplateIntentExtractor,
    TemplateMatcher,
    TemplateAdapter,
    ProvenanceTracker
)
print("DEBUG: templates imported", file=sys.stderr, flush=True)

print("DEBUG: All imports completed successfully!", file=sys.stderr, flush=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("n8n-workflow-builder")


def create_n8n_server(api_url: str, api_key: str) -> Server:
    """Create the n8n workflow builder MCP server"""
    import sys

    print("DEBUG: create_n8n_server() started", file=sys.stderr, flush=True)

    server = Server("n8n-workflow-builder")
    print("DEBUG: Server() created", file=sys.stderr, flush=True)
    n8n_client = N8nClient(api_url, api_key)
    print("DEBUG: N8nClient created", file=sys.stderr, flush=True)
    workflow_builder = WorkflowBuilder()
    workflow_validator = WorkflowValidator()
    semantic_analyzer = SemanticWorkflowAnalyzer()
    ai_feedback_analyzer = AIFeedbackAnalyzer()
    state_manager = StateManager()
    rbac_manager = RBACManager()
    template_engine = TemplateRecommendationEngine()
    intent_manager = IntentManager()
    approval_workflow = ApprovalWorkflow()

    # Template System v2.0
    template_registry = TemplateRegistry()
    template_adapter = TemplateAdapter()
    provenance_tracker = ProvenanceTracker()

    print("DEBUG: All components initialized, registering tools...", file=sys.stderr, flush=True)

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available n8n workflow tools"""
        print("DEBUG: list_tools() called", file=sys.stderr, flush=True)
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
                name="create_workflow",
                description=(
                    "✨ Create a new workflow in n8n. Provide workflow name, nodes, and connections. "
                    "This is the primary tool for building new workflows. "
                    "Note: Workflows are created inactive by default and must be activated in the n8n UI."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Workflow name"
                        },
                        "nodes": {
                            "type": "array",
                            "description": "Array of workflow nodes with type, name, parameters, position",
                            "items": {"type": "object"}
                        },
                        "connections": {
                            "type": "object",
                            "description": "Workflow connections between nodes"
                        },
                        "settings": {
                            "type": "object",
                            "description": "Optional workflow settings"
                        }
                    },
                    "required": ["name", "nodes", "connections"]
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
                name="delete_workflow",
                description=(
                    "🗑️ Delete (archive) a workflow. This removes the workflow from n8n. "
                    "Use with caution as this action may be irreversible depending on n8n configuration."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "string",
                            "description": "ID of the workflow to delete"
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
            ),
            Tool(
                name="add_node_intent",
                description="📝 Add 'why' metadata to a workflow node for AI context continuity. Helps LLMs remember reasoning, assumptions, and risks across iterations.",
                inputSchema={"type":"object","properties":{"workflow_id":{"type":"string","description":"Workflow ID"},"node_name":{"type":"string","description":"Name of the node to add intent to"},"reason":{"type":"string","description":"Why this node exists / what problem it solves"},"assumption":{"type":"string","description":"Optional: Assumptions made when building this node"},"risk":{"type":"string","description":"Optional: Known risks or limitations"},"alternative":{"type":"string","description":"Optional: Alternative approaches considered"},"dependency":{"type":"string","description":"Optional: Dependencies on other nodes or systems"}},"required":["workflow_id","node_name","reason"]}
            ),
            Tool(
                name="get_workflow_intents",
                description="📋 Get all intent metadata from a workflow. Shows the 'why' behind each node - perfect for understanding existing workflows.",
                inputSchema={"type":"object","properties":{"workflow_id":{"type":"string","description":"Workflow ID"},"format":{"type":"string","description":"Output format: 'report' (markdown) or 'json'","enum":["report","json"],"default":"report"}},"required":["workflow_id"]}
            ),
            Tool(
                name="analyze_intent_coverage",
                description="📊 Analyze how well a workflow is documented with intent metadata. Shows coverage percentage and recommendations.",
                inputSchema={"type":"object","properties":{"workflow_id":{"type":"string","description":"Workflow ID to analyze"}},"required":["workflow_id"]}
            ),
            Tool(
                name="suggest_node_intent",
                description="💡 Get AI-generated intent template for a specific node. Provides a starting point for documenting the 'why'.",
                inputSchema={"type":"object","properties":{"workflow_id":{"type":"string","description":"Workflow ID"},"node_name":{"type":"string","description":"Node name to generate suggestion for"}},"required":["workflow_id","node_name"]}
            ),
            Tool(
                name="update_node_intent",
                description="✏️ Update existing intent metadata for a node. Refine documentation as understanding evolves.",
                inputSchema={"type":"object","properties":{"workflow_id":{"type":"string"},"node_name":{"type":"string"},"reason":{"type":"string"},"assumption":{"type":"string"},"risk":{"type":"string"},"alternative":{"type":"string"},"dependency":{"type":"string"}},"required":["workflow_id","node_name"]}
            ),
            Tool(
                name="remove_node_intent",
                description="🗑️ Remove intent metadata from a node. Use when intent needs to be completely rewritten.",
                inputSchema={"type":"object","properties":{"workflow_id":{"type":"string","description":"Workflow ID"},"node_name":{"type":"string","description":"Node name to remove intent from"}},"required":["workflow_id","node_name"]}
            ),
            Tool(
                name="watch_workflow_execution",
                description="👁️ Monitor workflow execution and get detailed error feedback. Returns execution status with error analysis if execution failed.",
                inputSchema={"type":"object","properties":{"workflow_id":{"type":"string","description":"Workflow ID to monitor"},"execution_id":{"type":"string","description":"Optional: Specific execution ID. If not provided, analyzes the most recent execution."}},"required":["workflow_id"]}
            ),
            Tool(
                name="get_execution_error_context",
                description="🔍 Get detailed error context for a failed execution. Extracts error node, simplifies error message, provides fix suggestions.",
                inputSchema={"type":"object","properties":{"execution_id":{"type":"string","description":"Execution ID that failed"},"workflow_id":{"type":"string","description":"Workflow ID"}},"required":["execution_id","workflow_id"]}
            ),
            Tool(
                name="analyze_execution_errors",
                description="📊 Analyze error patterns across multiple executions of a workflow. Identifies common failure points and recurring issues.",
                inputSchema={"type":"object","properties":{"workflow_id":{"type":"string","description":"Workflow ID to analyze"},"limit":{"type":"number","description":"Number of recent executions to analyze (default: 10)","default":10}},"required":["workflow_id"]}
            ),
            Tool(
                name="detect_workflow_drift",
                description="🔍 Detect workflow degradation over time by comparing baseline vs current execution patterns. Identifies success rate drops, performance degradation, and new error patterns.",
                inputSchema={"type":"object","properties":{"workflow_id":{"type":"string","description":"Workflow ID to analyze"},"lookback_days":{"type":"number","description":"Days of history to analyze (default: 30)","default":30}},"required":["workflow_id"]}
            ),
            Tool(
                name="analyze_drift_pattern",
                description="🔬 Deep analysis of a specific drift pattern. Finds when drift started, whether it was gradual, and potential causes.",
                inputSchema={"type":"object","properties":{"workflow_id":{"type":"string","description":"Workflow ID"},"pattern_type":{"type":"string","description":"Pattern type: success_rate_drift, performance_drift, new_error_pattern, error_frequency_drift"}},"required":["workflow_id","pattern_type"]}
            ),
            Tool(
                name="get_drift_root_cause",
                description="🎯 Determine root cause of detected drift. Analyzes patterns and provides evidence-based root cause with confidence score.",
                inputSchema={"type":"object","properties":{"workflow_id":{"type":"string","description":"Workflow ID"},"lookback_days":{"type":"number","description":"Days of history (default: 30)","default":30}},"required":["workflow_id"]}
            ),
            Tool(
                name="get_drift_fix_suggestions",
                description="💡 Get actionable fix suggestions for detected drift. Provides specific changes to apply, with confidence scores and testing recommendations.",
                inputSchema={"type":"object","properties":{"workflow_id":{"type":"string","description":"Workflow ID"}},"required":["workflow_id"]}
            ),
            Tool(
                name="explain_workflow",
                description="📖 Generate comprehensive workflow explanation: purpose, data flow, dependencies, risks. Perfect for audit, onboarding, and documentation.",
                inputSchema={"type":"object","properties":{"workflow_id":{"type":"string","description":"Workflow ID to explain"},"format":{"type":"string","description":"Output format: markdown, json, or text (default: markdown)","default":"markdown"},"include_analysis":{"type":"boolean","description":"Include semantic analysis and execution history (default: true)","default":True}},"required":["workflow_id"]}
            ),
            Tool(
                name="get_workflow_purpose",
                description="🎯 Quick analysis of workflow purpose and business domain. Identifies what the workflow does and why it exists.",
                inputSchema={"type":"object","properties":{"workflow_id":{"type":"string","description":"Workflow ID"}},"required":["workflow_id"]}
            ),
            Tool(
                name="trace_data_flow",
                description="🔄 Trace data movement through workflow: sources, transformations, destinations. Identifies critical data paths.",
                inputSchema={"type":"object","properties":{"workflow_id":{"type":"string","description":"Workflow ID"}},"required":["workflow_id"]}
            ),
            Tool(
                name="map_dependencies",
                description="🔗 Map all workflow dependencies: internal workflows, external services, credentials. Identifies single points of failure.",
                inputSchema={"type":"object","properties":{"workflow_id":{"type":"string","description":"Workflow ID"}},"required":["workflow_id"]}
            ),
            Tool(
                name="analyze_workflow_risks",
                description="⚠️ Comprehensive risk assessment: data loss, security, performance, availability, compliance risks with mitigation plan.",
                inputSchema={"type":"object","properties":{"workflow_id":{"type":"string","description":"Workflow ID"},"include_analysis":{"type":"boolean","description":"Include semantic analysis and execution history (default: true)","default":True}},"required":["workflow_id"]}
            ),
            Tool(
                name="simulate_workflow_changes",
                description="🔮 Terraform-style change preview: compare old vs new workflow, analyze impact, detect breaking changes. Shows color-coded diff with recommendations.",
                inputSchema={
                    "type":"object",
                    "properties":{
                        "workflow_id":{"type":"string","description":"Current workflow ID"},
                        "new_workflow":{"type":"object","description":"New workflow JSON structure"}
                    },
                    "required":["workflow_id","new_workflow"]
                }
            ),
            Tool(
                name="compare_workflows",
                description="📊 Side-by-side workflow comparison: detailed diff of nodes, connections, settings. Identifies added/removed/modified elements.",
                inputSchema={
                    "type":"object",
                    "properties":{
                        "workflow_id_1":{"type":"string","description":"First workflow ID"},
                        "workflow_id_2":{"type":"string","description":"Second workflow ID"}
                    },
                    "required":["workflow_id_1","workflow_id_2"]
                }
            ),
            Tool(
                name="analyze_change_impact",
                description="⚡ Multi-dimensional impact analysis: data flow, execution, dependencies, triggers, downstream workflows. Calculates overall risk score (0-10).",
                inputSchema={
                    "type":"object",
                    "properties":{
                        "workflow_id":{"type":"string","description":"Current workflow ID"},
                        "new_workflow":{"type":"object","description":"Proposed workflow changes"},
                        "include_downstream":{"type":"boolean","description":"Check impact on workflows that call this one","default":True}
                    },
                    "required":["workflow_id","new_workflow"]
                }
            ),
            Tool(
                name="create_change_request",
                description="📝 Create change request for approval workflow: documents changes, requester, reason. Returns request ID for tracking.",
                inputSchema={
                    "type":"object",
                    "properties":{
                        "workflow_id":{"type":"string","description":"Workflow ID"},
                        "workflow_name":{"type":"string","description":"Workflow name"},
                        "changes":{"type":"object","description":"Proposed changes"},
                        "reason":{"type":"string","description":"Why this change is needed"},
                        "requester":{"type":"string","description":"Person requesting change"}
                    },
                    "required":["workflow_id","workflow_name","changes","reason","requester"]
                }
            ),
            Tool(
                name="review_change_request",
                description="✅ Approve or reject change request: adds reviewer, comments, updates status.",
                inputSchema={
                    "type":"object",
                    "properties":{
                        "request_id":{"type":"string","description":"Change request ID"},
                        "action":{"type":"string","enum":["approve","reject"],"description":"Review decision"},
                        "reviewer":{"type":"string","description":"Person reviewing"},
                        "comments":{"type":"string","description":"Review comments/reason"}
                    },
                    "required":["request_id","action","reviewer"]
                }
            ),
            Tool(
                name="get_change_history",
                description="📜 Get change request history for workflow: all past changes, approvals, rejections with timestamps.",
                inputSchema={
                    "type":"object",
                    "properties":{
                        "workflow_id":{"type":"string","description":"Workflow ID"}
                    },
                    "required":["workflow_id"]
                }
            ),
            Tool(
                name="find_templates_by_intent",
                description="🎯 Smart template matching: Describe your goal → get template suggestions with match explanation. Uses intent-based semantic matching.",
                inputSchema={
                    "type":"object",
                    "properties":{
                        "description":{"type":"string","description":"Natural language description of what you want to build"},
                        "top_k":{"type":"integer","description":"Number of suggestions (default: 5)","default":5}
                    },
                    "required":["description"]
                }
            ),
            Tool(
                name="extract_template_intent",
                description="🧠 Extract template intent: purpose, assumptions, risks, data flow, external systems. Makes templates 'thinkable'.",
                inputSchema={
                    "type":"object",
                    "properties":{
                        "template_id":{"type":"string","description":"Template ID"}
                    },
                    "required":["template_id"]
                }
            ),
            Tool(
                name="adapt_template",
                description="🔧 Adapt template for production: replace placeholders, abstract credentials, modernize deprecated nodes, add error handling.",
                inputSchema={
                    "type":"object",
                    "properties":{
                        "template_id":{"type":"string","description":"Template ID"},
                        "replacements":{"type":"object","description":"Placeholder replacements {\"API_URL\": \"https://...\"}"},
                        "add_error_handling":{"type":"boolean","description":"Add error handling (default: true)","default":True},
                        "modernize_nodes":{"type":"boolean","description":"Replace deprecated nodes (default: true)","default":True}
                    },
                    "required":["template_id"]
                }
            ),
            Tool(
                name="get_template_provenance",
                description="📊 Get template provenance: source, author, success rate, usage stats, trust score. Shows template reliability.",
                inputSchema={
                    "type":"object",
                    "properties":{
                        "template_id":{"type":"string","description":"Template ID"}
                    },
                    "required":["template_id"]
                }
            ),
            Tool(
                name="get_template_requirements",
                description="📋 Get template requirements: placeholders to fill, credentials needed, external systems. Pre-deployment checklist.",
                inputSchema={
                    "type":"object",
                    "properties":{
                        "template_id":{"type":"string","description":"Template ID"}
                    },
                    "required":["template_id"]
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

            elif name == "create_workflow":
                name_arg = arguments["name"]
                nodes = arguments["nodes"]
                connections = arguments["connections"]
                settings = arguments.get("settings", {})

                # Build workflow object
                # Note: 'active' is read-only and cannot be set during creation
                workflow_data = {
                    "name": name_arg,
                    "nodes": nodes,
                    "connections": connections,
                    "settings": settings
                }

                # Create workflow via API
                created_workflow = await n8n_client.create_workflow(workflow_data)

                # Set as current workflow and log
                workflow_id = created_workflow["id"]
                state_manager.set_current_workflow(workflow_id, name_arg)
                state_manager.log_action("create_workflow", {
                    "workflow_id": workflow_id,
                    "workflow_name": name_arg,
                    "node_count": len(nodes)
                })

                # Format result
                is_active = created_workflow.get("active", False)
                result = f"# ✅ Workflow Created: {name_arg}\n\n"
                result += f"**ID**: `{workflow_id}`\n"
                result += f"**Status**: {'🟢 Active' if is_active else '⚪ Inactive (default)'}\n"
                result += f"**Nodes**: {len(nodes)}\n"
                result += f"**Connections**: {len(connections)} source nodes\n\n"

                result += "## Nodes:\n\n"
                for node in nodes:
                    result += f"- **{node['name']}** (`{node['type']}`)\n"

                result += "\n---\n\n"
                result += f"💡 **Next Steps**:\n"
                result += f"- Execute with: `execute_workflow(workflow_id=\"{workflow_id}\")`\n"
                result += f"- Monitor with: `watch_workflow_execution(workflow_id=\"{workflow_id}\")`\n"
                if not is_active:
                    result += f"- Activate in n8n UI if needed (workflows are inactive by default)\n"

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

            elif name == "delete_workflow":
                workflow_id = arguments["workflow_id"]

                # Get workflow name before deletion for better feedback
                try:
                    workflow = await n8n_client.get_workflow(workflow_id)
                    workflow_name = workflow.get('name', 'Unknown')
                except:
                    workflow_name = "Unknown"

                # Delete the workflow
                result_data = await n8n_client.delete_workflow(workflow_id)

                state_manager.log_action("delete_workflow", {"workflow_id": workflow_id, "workflow_name": workflow_name})

                result = f"# Workflow Deleted Successfully\n\n"
                result += f"**ID:** {workflow_id}\n"
                result += f"**Name:** {workflow_name}\n\n"
                result += "⚠️ The workflow has been removed from n8n."

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

            elif name == "add_node_intent":
                workflow_id = arguments["workflow_id"]
                node_name = arguments["node_name"]
                reason = arguments["reason"]
                assumption = arguments.get("assumption")
                risk = arguments.get("risk")
                alternative = arguments.get("alternative")
                dependency = arguments.get("dependency")

                # Fetch workflow
                workflow = await n8n_client.get_workflow(workflow_id)

                # Find node
                node = None
                for n in workflow.get("nodes", []):
                    if n["name"] == node_name:
                        node = n
                        break

                if not node:
                    return [TextContent(
                        type="text",
                        text=f"❌ Node '{node_name}' not found in workflow"
                    )]

                # Create intent
                intent = intent_manager.create_intent(
                    reason=reason,
                    assumption=assumption,
                    risk=risk,
                    alternative=alternative,
                    dependency=dependency
                )

                # Add intent to node
                intent_manager.add_intent_to_node(node, intent)

                # Update workflow
                updated_workflow = await n8n_client.update_workflow(workflow_id, {
                    "nodes": workflow["nodes"]
                })

                # Log action
                state_manager.log_action("add_node_intent", {
                    "workflow_id": workflow_id,
                    "node_name": node_name
                })

                result = f"✅ Intent added to node: **{node_name}**\n\n"
                result += f"**Reason:** {reason}\n"
                if assumption:
                    result += f"**Assumption:** {assumption}\n"
                if risk:
                    result += f"**Risk:** {risk}\n"
                if alternative:
                    result += f"**Alternative:** {alternative}\n"
                if dependency:
                    result += f"**Dependency:** {dependency}\n"

                return [TextContent(type="text", text=result)]

            elif name == "get_workflow_intents":
                workflow_id = arguments["workflow_id"]
                format_type = arguments.get("format", "report")

                # Fetch workflow
                workflow = await n8n_client.get_workflow(workflow_id)

                # Log action
                state_manager.log_action("get_workflow_intents", {
                    "workflow_id": workflow_id,
                    "format": format_type
                })

                if format_type == "json":
                    intents = intent_manager.get_workflow_intents(workflow)
                    result = json.dumps(intents, indent=2)
                else:
                    result = intent_manager.generate_intent_report(workflow)

                return [TextContent(type="text", text=result)]

            elif name == "analyze_intent_coverage":
                workflow_id = arguments["workflow_id"]

                # Fetch workflow
                workflow = await n8n_client.get_workflow(workflow_id)

                # Analyze coverage
                analysis = intent_manager.analyze_intent_coverage(workflow)

                # Log action
                state_manager.log_action("analyze_intent_coverage", {
                    "workflow_id": workflow_id,
                    "coverage": analysis["coverage_percentage"]
                })

                # Format result
                result = f"# Intent Coverage Analysis: {workflow['name']}\n\n"
                result += f"**Coverage**: {analysis['coverage_percentage']}%\n"
                result += f"**Nodes with Intent**: {analysis['nodes_with_intent']} / {analysis['total_nodes']}\n"
                result += f"**Nodes without Intent**: {analysis['nodes_without_intent']}\n\n"

                if analysis['critical_without_intent']:
                    result += "## ⚠️ Critical Nodes Missing Intent:\n\n"
                    for node_name in analysis['critical_without_intent']:
                        result += f"- {node_name}\n"
                    result += "\n"

                result += "## Node Breakdown:\n\n"
                result += f"- Triggers: {analysis['node_breakdown']['triggers']}\n"
                result += f"- Logic nodes: {analysis['node_breakdown']['logic']}\n"
                result += f"- Action nodes: {analysis['node_breakdown']['actions']}\n\n"

                result += f"## 💡 Recommendation\n\n{analysis['recommendation']}"

                return [TextContent(type="text", text=result)]

            elif name == "suggest_node_intent":
                workflow_id = arguments["workflow_id"]
                node_name = arguments["node_name"]

                # Fetch workflow
                workflow = await n8n_client.get_workflow(workflow_id)

                # Find node
                node = None
                for n in workflow.get("nodes", []):
                    if n["name"] == node_name:
                        node = n
                        break

                if not node:
                    return [TextContent(
                        type="text",
                        text=f"❌ Node '{node_name}' not found in workflow"
                    )]

                # Generate suggestion
                suggestion = intent_manager.suggest_intent_for_node(node, workflow)

                # Log action
                state_manager.log_action("suggest_node_intent", {
                    "workflow_id": workflow_id,
                    "node_name": node_name
                })

                return [TextContent(type="text", text=suggestion)]

            elif name == "update_node_intent":
                workflow_id = arguments["workflow_id"]
                node_name = arguments["node_name"]

                # Fetch workflow
                workflow = await n8n_client.get_workflow(workflow_id)

                # Find node
                node = None
                for n in workflow.get("nodes", []):
                    if n["name"] == node_name:
                        node = n
                        break

                if not node:
                    return [TextContent(
                        type="text",
                        text=f"❌ Node '{node_name}' not found in workflow"
                    )]

                # Build updates
                updates = {}
                if "reason" in arguments:
                    updates["reason"] = arguments["reason"]
                if "assumption" in arguments:
                    updates["assumption"] = arguments["assumption"]
                if "risk" in arguments:
                    updates["risk"] = arguments["risk"]
                if "alternative" in arguments:
                    updates["alternative"] = arguments["alternative"]
                if "dependency" in arguments:
                    updates["dependency"] = arguments["dependency"]

                if not updates:
                    return [TextContent(
                        type="text",
                        text="No updates provided. Specify at least one field to update."
                    )]

                # Update intent
                intent_manager.update_node_intent(node, updates)

                # Update workflow
                updated_workflow = await n8n_client.update_workflow(workflow_id, {
                    "nodes": workflow["nodes"]
                })

                # Log action
                state_manager.log_action("update_node_intent", {
                    "workflow_id": workflow_id,
                    "node_name": node_name,
                    "fields_updated": list(updates.keys())
                })

                result = f"✅ Intent updated for node: **{node_name}**\n\n"
                result += "**Updated fields:**\n"
                for key, value in updates.items():
                    result += f"- {key}: {value}\n"

                return [TextContent(type="text", text=result)]

            elif name == "remove_node_intent":
                workflow_id = arguments["workflow_id"]
                node_name = arguments["node_name"]

                # Fetch workflow
                workflow = await n8n_client.get_workflow(workflow_id)

                # Find node
                node = None
                for n in workflow.get("nodes", []):
                    if n["name"] == node_name:
                        node = n
                        break

                if not node:
                    return [TextContent(
                        type="text",
                        text=f"❌ Node '{node_name}' not found in workflow"
                    )]

                # Check if node has intent
                if not intent_manager.get_node_intent(node):
                    return [TextContent(
                        type="text",
                        text=f"ℹ️ Node '{node_name}' has no intent metadata to remove"
                    )]

                # Remove intent
                intent_manager.remove_intent_from_node(node)

                # Update workflow
                updated_workflow = await n8n_client.update_workflow(workflow_id, {
                    "nodes": workflow["nodes"]
                })

                # Log action
                state_manager.log_action("remove_node_intent", {
                    "workflow_id": workflow_id,
                    "node_name": node_name
                })

                return [TextContent(
                    type="text",
                    text=f"✅ Intent metadata removed from node: **{node_name}**"
                )]

            elif name == "watch_workflow_execution":
                workflow_id = arguments["workflow_id"]
                execution_id = arguments.get("execution_id")

                # Fetch workflow
                workflow = await n8n_client.get_workflow(workflow_id)

                # Get execution - either specific ID or most recent
                if execution_id:
                    execution = await n8n_client.get_execution(execution_id)
                else:
                    # Get most recent execution for this workflow
                    executions = await n8n_client.get_executions(workflow_id, limit=1)
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
                state_manager.log_action("watch_workflow_execution", {
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

            elif name == "get_execution_error_context":
                execution_id = arguments["execution_id"]
                workflow_id = arguments["workflow_id"]

                # Fetch workflow and execution
                workflow = await n8n_client.get_workflow(workflow_id)
                execution = await n8n_client.get_execution(execution_id)

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
                state_manager.log_action("get_execution_error_context", {
                    "execution_id": execution_id,
                    "workflow_id": workflow_id,
                    "error_node": error_node_name,
                    "error_type": simplified_error["error_type"]
                })

                return [TextContent(type="text", text=result)]

            elif name == "analyze_execution_errors":
                workflow_id = arguments["workflow_id"]
                limit = arguments.get("limit", 10)

                # Fetch workflow
                workflow = await n8n_client.get_workflow(workflow_id)

                # Get recent executions
                executions = await n8n_client.get_executions(workflow_id, limit=limit)

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
                state_manager.log_action("analyze_execution_errors", {
                    "workflow_id": workflow_id,
                    "executions_analyzed": len(executions),
                    "failed_count": failed_count,
                    "error_patterns": len(error_patterns)
                })

                return [TextContent(type="text", text=result)]

            elif name == "detect_workflow_drift":
                workflow_id = arguments["workflow_id"]
                lookback_days = arguments.get("lookback_days", 30)

                # Fetch workflow and executions
                workflow = await n8n_client.get_workflow(workflow_id)
                executions = await n8n_client.get_executions(workflow_id, limit=100)

                if not executions or len(executions) < 2:
                    return [TextContent(
                        type="text",
                        text=f"ℹ️ Insufficient execution history for drift detection (need at least 2 executions)"
                    )]

                # Analyze drift
                drift_analysis = DriftDetector.analyze_execution_history(executions)

                # Log action
                state_manager.log_action("detect_workflow_drift", {
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

            elif name == "analyze_drift_pattern":
                workflow_id = arguments["workflow_id"]
                pattern_type = arguments["pattern_type"]

                # Fetch workflow and executions
                workflow = await n8n_client.get_workflow(workflow_id)
                executions = await n8n_client.get_executions(workflow_id, limit=100)

                # Get drift analysis first
                drift_analysis = DriftDetector.analyze_execution_history(executions)

                # Find matching pattern
                patterns = drift_analysis.get("patterns", [])
                target_pattern = None
                for p in patterns:
                    if p["type"] == pattern_type:
                        target_pattern = p
                        break

                if not target_pattern:
                    return [TextContent(
                        type="text",
                        text=f"⚠️ Pattern type '{pattern_type}' not found in current drift analysis"
                    )]

                # Analyze pattern
                analysis = DriftPatternAnalyzer.analyze_pattern(target_pattern, executions)

                # Format result
                result = f"# Pattern Analysis: {pattern_type}\n\n"
                result += f"**Severity**: {target_pattern.get('severity', 'unknown').upper()}\n\n"

                if analysis.get("started_around"):
                    result += f"**Started Around**: {analysis.get('started_around')}\n"
                result += f"**Change Type**: {'Gradual' if analysis.get('change_was_gradual') else 'Sudden'}\n\n"

                result += "## Potential Causes\n\n"
                causes = analysis.get("potential_causes", [])
                for cause in causes:
                    result += f"- {cause}\n"

                result += f"\n## 💡 Recommendation\n\n{analysis.get('recommendation')}\n"

                return [TextContent(type="text", text=result)]

            elif name == "get_drift_root_cause":
                workflow_id = arguments["workflow_id"]
                lookback_days = arguments.get("lookback_days", 30)

                # Fetch workflow and executions
                workflow = await n8n_client.get_workflow(workflow_id)
                executions = await n8n_client.get_executions(workflow_id, limit=100)

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

            elif name == "get_drift_fix_suggestions":
                workflow_id = arguments["workflow_id"]

                # Fetch workflow and executions
                workflow = await n8n_client.get_workflow(workflow_id)
                executions = await n8n_client.get_executions(workflow_id, limit=100)

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

            elif name == "explain_workflow":
                workflow_id = arguments["workflow_id"]
                format_type = arguments.get("format", "markdown")
                include_analysis = arguments.get("include_analysis", True)

                # Fetch workflow
                workflow = await n8n_client.get_workflow(workflow_id)
                # Handle if API returns list instead of dict
                if isinstance(workflow, list):
                    workflow = workflow[0] if workflow else {}

                all_workflows = await n8n_client.get_workflows()

                # Optional: Fetch semantic analysis and execution history
                semantic_analysis = None
                drift_analysis = None
                execution_history = None

                if include_analysis:
                    try:
                        semantic_analysis = semantic_analyzer.analyze_workflow(workflow)
                    except Exception as e:
                        logger.warning(f"Could not get semantic analysis: {e}")

                    try:
                        execution_history = await n8n_client.get_executions(workflow_id, limit=100)
                        if execution_history:
                            drift_analysis = DriftDetector.analyze_execution_history(execution_history)
                    except Exception as e:
                        logger.warning(f"Could not get execution history: {e}")

                # Fetch intent metadata for documentation coverage
                intent_metadata = None
                try:
                    workflow_intents = intent_manager.get_workflow_intents(workflow)
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

            elif name == "get_workflow_purpose":
                workflow_id = arguments["workflow_id"]

                # Fetch workflow
                workflow = await n8n_client.get_workflow(workflow_id)

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

                return [TextContent(type="text", text=result)]

            elif name == "trace_data_flow":
                workflow_id = arguments["workflow_id"]

                # Fetch workflow
                workflow = await n8n_client.get_workflow(workflow_id)
                # Handle if API returns list instead of dict
                if isinstance(workflow, list):
                    workflow = workflow[0] if workflow else {}

                # Trace data flow
                data_flow = DataFlowTracer.trace_data_flow(workflow)

                # Format result
                result = f"# Data Flow: {workflow['name']}\n\n"
                result += f"**Summary**: {data_flow.get('summary')}\n\n"

                # Input Sources
                input_sources = data_flow.get("input_sources", [])
                if input_sources:
                    result += "## Input Sources\n\n"
                    for source in input_sources:
                        result += f"- **{source['node_name']}**: {source['source_type']}\n"
                        details = source.get('details', {})
                        if details.get('url'):
                            result += f"  - URL: `{details['url']}`\n"
                    result += "\n"

                # Transformations
                transformations = data_flow.get("transformations", [])
                if transformations:
                    result += "## Transformations\n\n"
                    for trans in transformations:
                        result += f"- **{trans['node_name']}**: {trans['transformation_type']}\n"
                    result += "\n"

                # Output Destinations
                output_destinations = data_flow.get("output_destinations", [])
                if output_destinations:
                    result += "## Output Destinations\n\n"
                    for dest in output_destinations:
                        result += f"- **{dest['node_name']}**: {dest['sink_type']}\n"
                    result += "\n"

                # Critical Paths
                critical_paths = data_flow.get("critical_paths", [])
                if critical_paths:
                    result += "## Critical Data Paths\n\n"
                    for idx, path in enumerate(critical_paths[:5], 1):
                        path_str = " → ".join(path['path'])
                        result += f"{idx}. {path_str}\n"

                return [TextContent(type="text", text=result)]

            elif name == "map_dependencies":
                workflow_id = arguments["workflow_id"]

                # Fetch workflow and all workflows (for cross-workflow deps)
                workflow = await n8n_client.get_workflow(workflow_id)
                all_workflows = await n8n_client.get_workflows()

                # Map dependencies
                dependencies = DependencyMapper.map_dependencies(workflow, all_workflows)

                # Format result
                result = f"# Dependencies: {workflow['name']}\n\n"
                result += f"**Summary**: {dependencies.get('summary')}\n\n"

                # Internal Dependencies
                internal_deps = dependencies.get("internal_dependencies", [])
                if internal_deps:
                    result += "## Internal Dependencies\n\n"
                    for dep in internal_deps:
                        if dep["type"] == "workflow_call":
                            result += f"- Calls workflow: **{dep['target_workflow_name']}**\n"
                            result += f"  - Node: `{dep['node_name']}`\n"
                            result += f"  - Criticality: {dep['criticality']}\n"
                    result += "\n"

                # External Dependencies
                external_deps = dependencies.get("external_dependencies", [])
                if external_deps:
                    result += "## External Dependencies\n\n"
                    for dep in external_deps:
                        result += f"- **{dep['service_name']}** ({dep.get('service_type', 'unknown')})\n"
                        if dep.get('endpoint'):
                            result += f"  - Endpoint: `{dep['endpoint']}`\n"
                    result += "\n"

                # Credentials
                credentials = dependencies.get("credentials", [])
                if credentials:
                    result += "## Credentials\n\n"
                    for cred in credentials:
                        result += f"- **{cred['credential_name']}** ({cred['credential_type']})\n"
                        result += f"  - Criticality: {cred['criticality']}\n"
                        result += f"  - Used by: {', '.join(cred['used_by_nodes'])}\n"
                    result += "\n"

                # Single Points of Failure
                spofs = dependencies.get("single_points_of_failure", [])
                if spofs:
                    result += "## ⚠️ Single Points of Failure\n\n"
                    for spof in spofs:
                        result += f"- **{spof.get('type')}** (Severity: {spof.get('severity')})\n"
                        result += f"  - {spof.get('impact')}\n"

                return [TextContent(type="text", text=result)]

            elif name == "analyze_workflow_risks":
                workflow_id = arguments["workflow_id"]
                include_analysis = arguments.get("include_analysis", True)

                # Fetch workflow
                workflow = await n8n_client.get_workflow(workflow_id)

                # Optional: Fetch semantic analysis and execution history
                semantic_analysis = None
                drift_analysis = None
                execution_history = None

                if include_analysis:
                    try:
                        semantic_analysis = semantic_analyzer.analyze_workflow(workflow)
                    except Exception as e:
                        logger.warning(f"Could not get semantic analysis: {e}")

                    try:
                        execution_history = await n8n_client.get_executions(workflow_id, limit=100)
                        if execution_history:
                            drift_analysis = DriftDetector.analyze_execution_history(execution_history)
                    except Exception as e:
                        logger.warning(f"Could not get execution history: {e}")

                # Fetch intent metadata for documentation coverage
                intent_metadata = None
                try:
                    workflow_intents = intent_manager.get_workflow_intents(workflow)
                    if workflow_intents:
                        intent_metadata = {"nodes": workflow_intents}
                except Exception as e:
                    logger.debug(f"Could not get intent metadata: {e}")

                # Analyze risks
                risk_analysis = WorkflowExplainer.analyze_risks(
                    workflow,
                    semantic_analysis=semantic_analysis,
                    drift_analysis=drift_analysis,
                    execution_history=execution_history,
                    intent_metadata=intent_metadata
                )

                # Format result
                result = f"# Risk Assessment: {workflow['name']}\n\n"
                result += f"**Overall Risk Level**: {risk_analysis.get('risk_level', 'low').upper()}\n"
                result += f"**Risk Score**: {risk_analysis.get('overall_risk_score', 0):.1f}/10\n\n"
                result += f"**Summary**: {risk_analysis.get('risk_summary')}\n\n"

                # Risk Categories
                risk_categories = [
                    ("🔴 Data Loss Risks", "data_loss_risks"),
                    ("🔐 Security Risks", "security_risks"),
                    ("⚡ Performance Risks", "performance_risks"),
                    ("🚨 Availability Risks", "availability_risks"),
                    ("📋 Compliance Risks", "compliance_risks"),
                ]

                for category_name, category_key in risk_categories:
                    category_risks = risk_analysis.get(category_key, [])
                    if category_risks:
                        result += f"## {category_name}\n\n"
                        for risk in category_risks[:5]:  # Top 5 per category
                            severity = risk.get('severity', 'low')
                            result += f"- **[{severity.upper()}]** {risk.get('description')}\n"
                            if risk.get('node'):
                                result += f"  - Node: `{risk['node']}`\n"
                        result += "\n"

                # Mitigation Plan
                mitigation_plan = risk_analysis.get("mitigation_plan", [])
                if mitigation_plan:
                    result += "## 🛠️ Mitigation Plan\n\n"
                    for item in mitigation_plan[:10]:  # Top 10
                        priority = item.get('priority', '?')
                        severity = item.get('severity', 'low')
                        action = item.get('action', '')
                        result += f"{priority}. **[{severity.upper()}]** {action}\n"

                return [TextContent(type="text", text=result)]

            elif name == "simulate_workflow_changes":
                workflow_id = arguments["workflow_id"]
                new_workflow = arguments["new_workflow"]

                # Fetch old workflow
                old_workflow = await n8n_client.get_workflow(workflow_id)

                # Run dry-run simulation
                simulation = DryRunSimulator.simulate(
                    new_workflow,
                    validator=workflow_validator,
                    semantic_analyzer=semantic_analyzer
                )

                # Generate diff
                diff = WorkflowDiffEngine.compare_workflows(old_workflow, new_workflow)

                # Analyze impact
                all_workflows = await n8n_client.list_workflows()
                impact = ChangeImpactAnalyzer.analyze_impact(
                    diff, old_workflow, new_workflow, all_workflows
                )

                # Format as terraform-style plan
                plan_output = ChangeFormatter.format_plan(diff, impact)

                # Add simulation results
                result = plan_output + "\n\n"
                result += "=" * 80 + "\n"
                result += "DRY-RUN SIMULATION\n"
                result += "=" * 80 + "\n\n"

                if simulation["simulation_passed"]:
                    result += "✅ Simulation PASSED - Workflow is valid\n\n"
                else:
                    result += "❌ Simulation FAILED - Workflow has errors\n\n"

                if simulation["errors"]:
                    result += "**Errors:**\n"
                    for error in simulation["errors"]:
                        result += f"  - {error}\n"
                    result += "\n"

                if simulation.get("estimated_performance"):
                    perf = simulation["estimated_performance"]
                    result += "**Estimated Performance:**\n"
                    result += f"  - Node Count: {perf['node_count']}\n"
                    result += f"  - Duration: ~{perf['estimated_duration_seconds']}s\n"
                    result += f"  - Memory: ~{perf['estimated_memory_mb']}MB\n"
                    result += f"  - Complexity: {perf['complexity'].upper()}\n"

                return [TextContent(type="text", text=result)]

            elif name == "compare_workflows":
                workflow_id_1 = arguments["workflow_id_1"]
                workflow_id_2 = arguments["workflow_id_2"]

                # Fetch both workflows
                workflow_1 = await n8n_client.get_workflow(workflow_id_1)
                workflow_2 = await n8n_client.get_workflow(workflow_id_2)

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
                        result += f"  + {node['name']} ({node.get('type', 'unknown')})\n"
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

            elif name == "analyze_change_impact":
                workflow_id = arguments["workflow_id"]
                new_workflow = arguments["new_workflow"]
                include_downstream = arguments.get("include_downstream", True)

                # Fetch old workflow
                old_workflow = await n8n_client.get_workflow(workflow_id)

                # Generate diff
                diff = WorkflowDiffEngine.compare_workflows(old_workflow, new_workflow)

                # Analyze impact
                all_workflows = []
                if include_downstream:
                    all_workflows = await n8n_client.list_workflows()

                impact = ChangeImpactAnalyzer.analyze_impact(
                    diff, old_workflow, new_workflow, all_workflows
                )

                # Format result
                result = "# Change Impact Analysis\n\n"
                result += f"**Overall Risk Score**: {impact['overall_risk_score']}/10\n"
                result += f"**Risk Level**: {impact['risk_level'].upper()}\n\n"

                # Impact dimensions
                dimensions = [
                    ("🔄 Data Flow Impact", "data_flow_impact"),
                    ("⚡ Execution Impact", "execution_impact"),
                    ("🔗 Dependency Impact", "dependency_impact"),
                    ("🔔 Trigger Impact", "trigger_impact"),
                    ("⚙️ Downstream Impact", "downstream_impact"),
                ]

                for dim_name, dim_key in dimensions:
                    dim_impact = impact[dim_key]
                    if dim_impact["impacts"]:
                        result += f"## {dim_name}\n\n"
                        result += f"**Summary**: {dim_impact['summary']}\n"
                        result += f"**Breaking Changes**: {'Yes' if dim_impact['has_breaking_changes'] else 'No'}\n\n"

                        for imp in dim_impact["impacts"][:5]:
                            severity = imp.get("severity", "unknown")
                            result += f"- **[{severity.upper()}]** {imp['description']}\n"
                            if imp.get("node"):
                                result += f"  - Node: `{imp['node']}`\n"
                            if imp.get("affected_paths"):
                                result += f"  - Affected: {len(imp['affected_paths'])} path(s)\n"
                        result += "\n"

                # Recommendations
                if impact["recommendations"]:
                    result += "## 💡 Recommendations\n\n"
                    for rec in impact["recommendations"]:
                        result += f"- {rec}\n"

                return [TextContent(type="text", text=result)]

            elif name == "create_change_request":
                workflow_id = arguments["workflow_id"]
                workflow_name = arguments["workflow_name"]
                changes = arguments["changes"]
                reason = arguments["reason"]
                requester = arguments["requester"]

                # Create request
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

            elif name == "review_change_request":
                request_id = arguments["request_id"]
                action = arguments["action"]
                reviewer = arguments["reviewer"]
                comments = arguments.get("comments", "")

                # Perform action
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

            elif name == "get_change_history":
                workflow_id = arguments["workflow_id"]

                # Get history
                history = approval_workflow.get_workflow_history(workflow_id)

                if not history:
                    return [TextContent(type="text", text=f"No change history found for workflow {workflow_id}")]

                result = f"# Change History\n\n"
                result += f"**Total Requests**: {len(history)}\n\n"

                # Group by status
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

                # Show recent requests
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

            elif name == "find_templates_by_intent":
                description = arguments["description"]
                top_k = arguments.get("top_k", 5)

                # Fetch all templates
                all_templates = await template_registry.fetch_all_templates()

                # Create matcher and find matches
                matcher = TemplateMatcher(all_templates)
                matches = matcher.match(description, top_k=top_k)

                # Format results
                result = f"# Template Suggestions for: \"{description}\"\n\n"
                result += f"Found {len(matches)} matches:\n\n"

                for i, (template, score, reason) in enumerate(matches, 1):
                    result += f"## {i}. {template.name} ({int(score * 100)}% match)\n\n"
                    result += f"**Why**: {reason}\n\n"

                    # Template details
                    result += f"- **Category**: {template.category}\n"
                    result += f"- **Complexity**: {template.complexity}\n"
                    result += f"- **Source**: {template.source}\n"

                    if template.trigger_type:
                        result += f"- **Trigger**: {template.trigger_type}\n"

                    if template.data_flow:
                        result += f"- **Data Flow**: {template.data_flow}\n"

                    if template.external_systems:
                        result += f"- **External Systems**: {', '.join(template.external_systems[:3])}\n"

                    result += f"- **Node Count**: {template.node_count}\n"
                    result += f"- **Setup Time**: ~{template.estimated_setup_time}\n"

                    if template.description:
                        result += f"\n**Description**: {template.description}\n"

                    result += "\n"

                    # Track usage
                    provenance_tracker.record_usage(template.id)

                return [TextContent(type="text", text=result)]

            elif name == "extract_template_intent":
                template_id = arguments["template_id"]

                # Get template
                template = await template_registry.get_template(template_id)

                if not template:
                    # Try from old template engine
                    from .templates.recommender import WORKFLOW_TEMPLATES
                    if template_id in WORKFLOW_TEMPLATES:
                        template_dict = WORKFLOW_TEMPLATES[template_id]
                        from .templates.sources.base import TemplateMetadata

                        # Convert node names to full node objects
                        full_nodes = []
                        for node_info in template_dict["nodes"]:
                            full_nodes.append({
                                "name": node_info["name"],
                                "type": node_info["type"],
                                "position": [0, 0],
                                "parameters": {}
                            })

                        template = TemplateMetadata(
                            id=template_id,
                            source="n8n_official",
                            name=template_dict["name"],
                            description=template_dict["description"],
                            category=template_dict["category"],
                            tags=template_dict["tags"],
                            n8n_version=">=1.0",
                            template_version="1.0.0",
                            nodes=full_nodes,
                            connections={},
                            settings={},
                            complexity=template_dict.get("complexity", template_dict.get("difficulty", "intermediate")),
                            node_count=len(full_nodes),
                            estimated_setup_time=template_dict["estimated_time"]
                        )

                if not template:
                    return [TextContent(type="text", text=f"Template {template_id} not found")]

                # Extract intent
                intent_data = TemplateIntentExtractor.extract_intent(template)

                # Format result
                result = f"# Template Intent Analysis: {template.name}\n\n"

                result += f"## 🎯 Purpose\n{intent_data['intent']}\n\n"

                result += f"## 📋 Classification\n"
                result += f"- **Type**: {intent_data['purpose']}\n"
                result += f"- **Trigger**: {intent_data['trigger_type'] or 'N/A'}\n"
                result += f"- **Data Flow**: {intent_data['data_flow']}\n\n"

                if intent_data['external_systems']:
                    result += f"## 🔗 External Systems\n"
                    for system in intent_data['external_systems']:
                        result += f"- {system}\n"
                    result += "\n"

                if intent_data['assumptions']:
                    result += f"## 💭 Assumptions\n"
                    for assumption in intent_data['assumptions']:
                        result += f"- {assumption}\n"
                    result += "\n"

                if intent_data['risks']:
                    result += f"## ⚠️  Risks\n"
                    for risk in intent_data['risks']:
                        result += f"- {risk}\n"
                    result += "\n"

                result += f"## 📊 Template Metadata\n"
                result += f"- **Source**: {template.source}\n"
                result += f"- **Category**: {template.category}\n"
                result += f"- **Complexity**: {template.complexity}\n"
                result += f"- **Node Count**: {template.node_count}\n"
                result += f"- **Error Handling**: {'✅ Yes' if template.has_error_handling else '❌ No'}\n"
                result += f"- **Documentation**: {'✅ Yes' if template.has_documentation else '❌ No'}\n"

                return [TextContent(type="text", text=result)]

            elif name == "adapt_template":
                template_id = arguments["template_id"]
                replacements = arguments.get("replacements", {})
                add_error_handling = arguments.get("add_error_handling", True)
                modernize_nodes = arguments.get("modernize_nodes", True)

                # Get template
                template = await template_registry.get_template(template_id)

                if not template:
                    return [TextContent(type="text", text=f"Template {template_id} not found")]

                # Adapt template
                adapted_workflow = template_adapter.adapt_template(
                    template,
                    replacements=replacements,
                    add_error_handling=add_error_handling,
                    modernize_nodes=modernize_nodes
                )

                # Get adaptation log
                adaptation_log = template_adapter.get_adaptation_log()

                # Format result
                result = f"# Template Adapted: {template.name}\n\n"

                result += f"## ✅ Adaptation Complete\n\n"
                result += f"**Changes Applied**:\n"
                for log_entry in adaptation_log:
                    result += f"- {log_entry}\n"
                result += "\n"

                result += f"## 📋 Next Steps\n\n"
                result += f"1. Review the adapted workflow JSON below\n"
                result += f"2. Configure required credentials\n"
                result += f"3. Test in a safe environment\n"
                result += f"4. Deploy to production\n\n"

                result += f"## 🔧 Adapted Workflow\n\n"
                result += f"```json\n{json.dumps(adapted_workflow, indent=2)}\n```\n"

                # Track adaptation
                provenance_tracker.record_adaptation(template_id, ", ".join(adaptation_log))

                return [TextContent(type="text", text=result)]

            elif name == "get_template_provenance":
                template_id = arguments["template_id"]

                # Get template
                template = await template_registry.get_template(template_id)

                if not template:
                    return [TextContent(type="text", text=f"Template {template_id} not found")]

                # Get or create provenance record
                record = provenance_tracker.get_record(template_id)

                if not record:
                    record = provenance_tracker.track_template(
                        template_id,
                        template.name,
                        template.source,
                        template.author
                    )

                # Format result
                result = f"# Template Provenance: {template.name}\n\n"

                result += f"## 📊 Trust Metrics\n"
                result += f"- **Overall Trust Score**: {record.overall_trust_score:.0%}\n"
                result += f"- **Reliability Score**: {record.reliability_score:.0%}\n"
                result += f"- **Security Score**: {record.security_score:.0%}\n"
                result += f"- **Success Rate**: {record.success_rate:.0%} ({record.successful_executions}/{record.total_executions} executions)\n\n"

                result += f"## 📈 Usage Statistics\n"
                result += f"- **Total Usage**: {record.usage_count} times\n"
                result += f"- **Deployments**: {record.deployment_count}\n"
                result += f"- **Adaptations**: {record.adaptation_count}\n"
                result += f"- **Last Used**: {record.last_used_at.strftime('%Y-%m-%d %H:%M') if record.last_used_at else 'Never'}\n\n"

                result += f"## 🏷️  Source Info\n"
                result += f"- **Source**: {template.source}\n"
                result += f"- **Author**: {template.author or 'Unknown'}\n"
                result += f"- **Created**: {template.created_at.strftime('%Y-%m-%d') if template.created_at else 'Unknown'}\n"

                if template.source_url:
                    result += f"- **URL**: {template.source_url}\n"

                result += "\n"

                result += f"## ✅ Quality Indicators\n"
                result += f"- **Error Handling**: {'✅ Yes' if record.has_error_handling else '❌ No'}\n"
                result += f"- **Documentation**: {'✅ Yes' if record.has_documentation else '❌ No'}\n"
                result += f"- **Tests**: {'✅ Yes' if record.has_tests else '❌ No'}\n"
                result += f"- **Best Practices**: {'✅ Yes' if record.uses_best_practices else '❌ No'}\n\n"

                if record.rating:
                    result += f"## ⭐ User Rating\n"
                    result += f"- **Average**: {record.rating:.1f}/5.0 ({record.rating_count} ratings)\n\n"

                return [TextContent(type="text", text=result)]

            elif name == "get_template_requirements":
                template_id = arguments["template_id"]

                # Get template
                template = await template_registry.get_template(template_id)

                if not template:
                    return [TextContent(type="text", text=f"Template {template_id} not found")]

                # Get requirements
                placeholders = template_adapter.get_placeholders(template)
                credentials = template_adapter.get_required_credentials(template)

                # Format result
                result = f"# Template Requirements: {template.name}\n\n"

                if placeholders:
                    result += f"## 📝 Placeholders to Fill ({len(placeholders)})\n\n"
                    for placeholder in placeholders:
                        result += f"### {placeholder['key']}\n"
                        result += f"- **Placeholder**: `{placeholder['placeholder']}`\n"
                        result += f"- **Node**: {placeholder['node']}\n"
                        result += f"- **Required**: {'✅ Yes' if placeholder['required'] else '❌ No'}\n\n"
                else:
                    result += f"## ✅ No Placeholders\nThis template is ready to use without placeholder replacement.\n\n"

                if credentials:
                    result += f"## 🔑 Credentials Needed ({len(credentials)})\n\n"
                    for cred in credentials:
                        result += f"### {cred['name']}\n"
                        result += f"- **Type**: {cred['type']}\n"
                        result += f"- **Used by**: {cred['node']}\n"
                        result += f"- **Required**: {'✅ Yes' if cred['required'] else '❌ No'}\n\n"
                else:
                    result += f"## ✅ No Credentials\nThis template doesn't require credential configuration.\n\n"

                if template.external_systems:
                    result += f"## 🌐 External Systems ({len(template.external_systems)})\n\n"
                    for system in template.external_systems:
                        result += f"- {system}\n"
                    result += "\n"

                result += f"## 📋 Pre-Deployment Checklist\n\n"
                result += f"- [ ] Fill all placeholders ({len(placeholders)} total)\n"
                result += f"- [ ] Configure credentials ({len(credentials)} total)\n"
                result += f"- [ ] Verify access to external systems ({len(template.external_systems or [])} total)\n"
                result += f"- [ ] Test in staging environment\n"
                result += f"- [ ] Review error handling\n"
                result += f"- [ ] Deploy to production\n"

                return [TextContent(type="text", text=result)]

            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]
        
        except Exception as e:
            import traceback
            logger.error(f"Error in tool {name}: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return [TextContent(type="text", text=f"Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}")]

    print("DEBUG: All tool handlers registered", file=sys.stderr, flush=True)

    return server


async def main():
    """Main entry point"""
    import sys

    print("DEBUG: main() started", file=sys.stderr, flush=True)

    # Get configuration from environment
    api_url = os.getenv("N8N_API_URL")
    api_key = os.getenv("N8N_API_KEY")

    print(f"DEBUG: Got env vars: API_URL={api_url is not None}, API_KEY={api_key is not None}", file=sys.stderr, flush=True)

    if not api_url or not api_key:
        logger.error("N8N_API_URL and N8N_API_KEY environment variables must be set")
        print("ERROR: Missing env vars", file=sys.stderr, flush=True)
        sys.exit(1)

    logger.info(f"Starting n8n Workflow Builder MCP Server... (API: {api_url})")
    print(f"DEBUG: Starting server initialization", file=sys.stderr, flush=True)

    try:
        server = create_n8n_server(api_url, api_key)
        print("DEBUG: Server created successfully", file=sys.stderr, flush=True)
        logger.info("Server initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize server: {e}", exc_info=True)
        print(f"ERROR: Server init failed: {e}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

    # Run the server
    from mcp.server.stdio import stdio_server

    print("DEBUG: About to start stdio_server", file=sys.stderr, flush=True)

    async with stdio_server() as (read_stream, write_stream):
        print("DEBUG: stdio_server started, calling server.run()", file=sys.stderr, flush=True)
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )
        print("DEBUG: server.run() completed", file=sys.stderr, flush=True)


if __name__ == "__main__":
    asyncio.run(main())
