# 🛠️ MCP Tools Reference

Complete reference of all available tools in the n8n Workflow Builder MCP Server.

## 📋 Table of Contents

1. [Workflow Management](#-workflow-management) - Core CRUD operations
2. [Workflow Design](#-workflow-design) - AI-powered design assistance
3. [Workflow Analysis](#-workflow-analysis) - Quality & security analysis
4. [Workflow Execution](#-workflow-execution) - Execution & monitoring
5. [Template System](#-template-system) - Template discovery & recommendations
6. [Intent Metadata](#-intent-metadata) - Document workflow reasoning
7. [Session Management](#-session-management) - Context & state tracking
8. [Validation](#-validation) - Pre-deployment validation
9. [RBAC & Security](#-rbac--security) - Role-based access control
10. [Drift Detection](#-drift-detection) - Change tracking & analysis

---

## 📊 Workflow Management

Complete CRUD operations for n8n workflows.

### `list_workflows`
List all workflows with filtering options.

**Usage:**
```
"Show me all my workflows"
"List active workflows"
```

**Returns:** List of workflows with ID, name, active status, and node count.

---

### `get_workflow_details`
Get detailed information about a specific workflow.

**Parameters:**
- `workflow_id` (required): Workflow ID

**Usage:**
```
"Show details for workflow abc123"
"Get workflow details for 'Daily Report'"
```

**Returns:** Complete workflow structure including nodes, connections, settings.

---

### `create_workflow`
Create a new workflow from scratch or from a template.

**Parameters:**
- `name` (required): Workflow name
- `nodes` (optional): Array of nodes
- `connections` (optional): Connection object
- `settings` (optional): Workflow settings

**Usage:**
```
"Create a new workflow called 'API Handler'"
```

**Returns:** Created workflow with ID and structure.

---

### `update_workflow` ⚡ **v1.13.2 - Smart Merge**
Update an existing workflow with intelligent merging.

**Parameters:**
- `workflow_id` (required): Workflow ID
- `name` (optional): New name
- `nodes` (optional): Nodes to update/add
- `connections` (optional): Connections to merge
- `settings` (optional): Settings to update

**Smart Merge Features:**
- ✅ Updates existing nodes by name
- ✅ Preserves other nodes
- ✅ Merges connections instead of replacing
- ✅ Prevents accidental data loss

**Usage:**
```
"Update workflow abc123 - change HTTP node URL to https://api.example.com"
"Rename workflow to 'Production API'"
```

**Returns:** Updated workflow with change summary.

---

### `delete_workflow` 🆕 **v1.14.0**
Delete (archive) a workflow from n8n.

**Parameters:**
- `workflow_id` (required): Workflow ID

**Usage:**
```
"Delete workflow abc123"
"Remove the test workflow"
```

**Returns:** Confirmation with workflow name and ID.

⚠️ **Warning:** Deletion may be irreversible depending on n8n configuration.

---

## 🧠 Workflow Design

AI-powered tools to help design workflows.

### `suggest_workflow_nodes`
Get AI-powered node suggestions based on your description.

**Parameters:**
- `description` (required): What you want to build

**Usage:**
```
"Suggest nodes for a workflow that fetches data from Postgres and sends via Slack"
```

**Returns:** Recommended nodes with configuration tips.

---

### `generate_workflow_template`
Generate a complete workflow template from natural language.

**Parameters:**
- `description` (required): Workflow description
- `template_type` (optional): Type of template (api_endpoint, scheduled_report, etc.)

**Usage:**
```
"Generate a workflow template for an API that validates and stores user data"
```

**Returns:** Complete workflow structure ready to deploy.

---

### `explain_node`
Get detailed explanation of a specific n8n node type.

**Parameters:**
- `node_type` (required): Node type (e.g., "HTTP Request", "Postgres", "IF")

**Usage:**
```
"Explain the HTTP Request node"
"How does the Postgres node work?"
```

**Returns:** Node description, use cases, best practices, examples.

---

## 🔍 Workflow Analysis

Analyze workflows for issues, security, and optimization.

### `analyze_workflow`
Comprehensive workflow analysis for issues and optimization.

**Parameters:**
- `workflow_id` (required): Workflow ID

**Usage:**
```
"Analyze workflow abc123"
"Check my 'Daily Report' workflow for issues"
```

**Returns:** Analysis report with issues, security findings, and recommendations.

---

### `analyze_workflow_semantics`
Deep semantic analysis detecting 12+ anti-patterns.

**Parameters:**
- `workflow_id` (required): Workflow ID

**Usage:**
```
"Run semantic analysis on workflow abc123"
```

**Returns:** Detailed anti-pattern report with severity levels and fixes.

**Checks:**
- HTTP retry logic
- Loop completion
- Timezone configuration
- IF node paths
- Webhook security
- Infinite loops
- Hardcoded credentials
- N+1 queries
- Rate limiting
- Data validation
- Error handling
- And more...

---

### `get_workflow_improvement_suggestions`
Get AI-powered improvement suggestions.

**Parameters:**
- `workflow_id` (required): Workflow ID

**Usage:**
```
"How can I improve workflow abc123?"
```

**Returns:** Specific, actionable improvement recommendations.

---

### `debug_workflow_error`
Debug a specific workflow error.

**Parameters:**
- `error_message` (required): Error message
- `workflow_id` (optional): Workflow ID
- `execution_id` (optional): Execution ID

**Usage:**
```
"Debug error: 'Connection timeout'"
```

**Returns:** Root cause analysis and fix suggestions.

---

## ⚡ Workflow Execution

Execute and monitor workflow runs.

### `execute_workflow`
Manually trigger a workflow execution.

**Parameters:**
- `workflow_id` (required): Workflow ID
- `input_data` (optional): Input data for the workflow

**Usage:**
```
"Execute workflow abc123"
"Run 'Daily Report' with test data"
```

**Returns:** Execution ID and initial status.

---

### `get_executions`
List workflow execution history.

**Parameters:**
- `workflow_id` (optional): Filter by workflow
- `limit` (optional): Number of executions to return

**Usage:**
```
"Show executions for workflow abc123"
"List last 10 executions"
```

**Returns:** Execution list with status, timestamps, and error info.

---

### `get_execution_details`
Get detailed information about a specific execution.

**Parameters:**
- `execution_id` (required): Execution ID

**Usage:**
```
"Show details for execution xyz789"
"What happened in the last execution?"
```

**Returns:** Complete execution data including node outputs, errors, timing.

---

### `watch_workflow_execution`
Monitor a workflow execution in real-time.

**Parameters:**
- `execution_id` (required): Execution ID

**Usage:**
```
"Watch execution xyz789"
```

**Returns:** Real-time execution progress and status updates.

---

### `get_execution_error_context`
Get detailed error context for failed executions.

**Parameters:**
- `execution_id` (required): Execution ID

**Usage:**
```
"Get error context for execution xyz789"
```

**Returns:** Error details, affected nodes, stack traces, and context.

---

### `analyze_execution_errors`
Analyze patterns in execution failures.

**Parameters:**
- `workflow_id` (required): Workflow ID
- `limit` (optional): Number of executions to analyze

**Usage:**
```
"Analyze errors for workflow abc123"
```

**Returns:** Error pattern analysis with AI-powered root cause detection.

---

## 📚 Template System

Intelligent Template System v2.0 with AI-powered recommendations.

### `recommend_templates` 🆕 **v1.13.0**
Get AI-powered template recommendations based on your description.

**Parameters:**
- `description` (required): What you want to build
- `limit` (optional): Number of recommendations

**Usage:**
```
"Recommend templates for building a customer notification system"
```

**Returns:** Ranked template recommendations with relevance scores and reasoning.

**Features:**
- Multi-source template aggregation
- Semantic matching beyond keywords
- Intent-based recommendations
- Quality scoring

---

### `get_template_library`
Browse all available templates.

**Usage:**
```
"Show me the template library"
```

**Returns:** Complete list of templates from all sources (n8n official, GitHub, local).

---

### `search_templates`
Search templates by keyword.

**Parameters:**
- `query` (required): Search query

**Usage:**
```
"Search templates for 'email automation'"
```

**Returns:** Matching templates with relevance scores.

---

### `get_templates_by_category`
Get templates filtered by category.

**Parameters:**
- `category` (required): Category (API, Reporting, Integration, etc.)

**Usage:**
```
"Show me all API templates"
```

**Returns:** Templates in the specified category.

---

### `get_templates_by_difficulty`
Get templates filtered by difficulty level.

**Parameters:**
- `difficulty` (required): Difficulty (beginner, intermediate, advanced)

**Usage:**
```
"Show me beginner templates"
```

**Returns:** Templates matching the difficulty level.

---

### `get_template_details`
Get detailed information about a specific template.

**Parameters:**
- `template_id` (required): Template ID

**Usage:**
```
"Show details for template 'email-campaign'"
```

**Returns:** Complete template documentation, structure, and implementation guide.

---

## 💭 Intent Metadata

Document the "why" behind workflow design decisions.

### `add_node_intent`
Add intent metadata to a node.

**Parameters:**
- `workflow_id` (required): Workflow ID
- `node_name` (required): Node name
- `intent` (required): Intent metadata object
  - `reason`: Why does this node exist?
  - `assumption`: What assumptions were made?
  - `risk`: What could go wrong?
  - `alternative`: What other options were considered?
  - `dependency`: What does this depend on?

**Usage:**
```
"Add intent to HTTP node: reason='Fetch user data from API'"
```

**Returns:** Confirmation with updated intent.

---

### `get_workflow_intents`
Get all intent metadata for a workflow.

**Parameters:**
- `workflow_id` (required): Workflow ID

**Usage:**
```
"Show intents for workflow abc123"
```

**Returns:** Complete intent metadata for all nodes.

---

### `analyze_intent_coverage`
Analyze how well workflow intents are documented.

**Parameters:**
- `workflow_id` (required): Workflow ID

**Usage:**
```
"Analyze intent coverage for workflow abc123"
```

**Returns:** Coverage report showing which nodes have intents.

---

### `suggest_node_intent`
Get AI-powered intent suggestions for a node.

**Parameters:**
- `workflow_id` (required): Workflow ID
- `node_name` (required): Node name

**Usage:**
```
"Suggest intent for HTTP Request node"
```

**Returns:** AI-generated intent metadata suggestions.

---

### `update_node_intent`
Update existing intent metadata.

**Parameters:**
- `workflow_id` (required): Workflow ID
- `node_name` (required): Node name
- `intent` (required): Updated intent metadata

**Usage:**
```
"Update intent for HTTP node: risk='API rate limiting'"
```

**Returns:** Confirmation with updated intent.

---

### `remove_node_intent`
Remove intent metadata from a node.

**Parameters:**
- `workflow_id` (required): Workflow ID
- `node_name` (required): Node name

**Usage:**
```
"Remove intent from HTTP node"
```

**Returns:** Confirmation of removal.

---

## 🔄 Session Management

Track context and state across conversations.

### `get_session_state`
Get complete session overview.

**Usage:**
```
"What's my current session state?"
```

**Returns:** Active workflow, recent workflows, recent actions, last execution.

---

### `set_active_workflow`
Set a workflow as active/current.

**Parameters:**
- `workflow_id` (required): Workflow ID

**Usage:**
```
"Set workflow abc123 as active"
```

**Returns:** Confirmation with workflow name.

---

### `get_active_workflow`
Get the currently active workflow.

**Usage:**
```
"What's the active workflow?"
```

**Returns:** Active workflow name and ID.

---

### `get_recent_workflows`
List recently accessed workflows.

**Usage:**
```
"Show recent workflows"
```

**Returns:** Last 10 workflows with timestamps.

---

### `get_session_history`
View action history.

**Usage:**
```
"Show my session history"
```

**Returns:** Complete action timeline with timestamps.

---

### `clear_session_state`
Clear session state and start fresh.

**Usage:**
```
"Clear my session state"
```

**Returns:** Confirmation of cleared state.

---

## ✅ Validation

Pre-deployment validation for workflows.

### `validate_workflow`
Comprehensive workflow validation.

**Parameters:**
- `workflow_id` (required): Workflow ID

**Usage:**
```
"Validate workflow abc123"
```

**Returns:** Validation report with schema, semantic, and parameter checks.

**Validation Layers:**
1. **Schema Validation:** Structure and required fields
2. **Semantic Validation:** Logical rules (triggers, connections, etc.)
3. **Parameter Validation:** Node-specific configuration checks

---

### `validate_workflow_json`
Validate workflow JSON before deployment.

**Parameters:**
- `workflow_json` (required): Workflow JSON object

**Usage:**
```
"Validate this workflow JSON: {...}"
```

**Returns:** Validation report for the provided JSON.

---

## 🔒 RBAC & Security

Role-based access control and approval workflows.

### `rbac_get_status`
Check if RBAC is enabled.

**Usage:**
```
"Is RBAC enabled?"
```

**Returns:** RBAC status and configuration.

---

### `rbac_add_user`
Add a user with role and permissions.

**Parameters:**
- `user_id` (required): User ID
- `role` (required): Role (admin, editor, viewer, etc.)
- `tenant_id` (optional): Tenant ID for multi-tenancy

**Usage:**
```
"Add user john@example.com as editor"
```

**Returns:** Confirmation with user details.

---

### `rbac_get_user_info`
Get user role and permissions.

**Parameters:**
- `user_id` (required): User ID

**Usage:**
```
"Get user info for john@example.com"
```

**Returns:** User role, permissions, and tenant info.

---

### `rbac_check_permission`
Check if user has specific permission.

**Parameters:**
- `user_id` (required): User ID
- `action` (required): Action (create_workflow, update_workflow, etc.)
- `resource_id` (optional): Resource ID

**Usage:**
```
"Can john@example.com update workflow abc123?"
```

**Returns:** Permission check result (allowed/denied).

---

### `rbac_create_approval_request`
Create approval request for workflow changes.

**Parameters:**
- `workflow_id` (required): Workflow ID
- `user_id` (required): Requesting user ID
- `changes` (required): Proposed changes
- `reason` (required): Reason for changes

**Usage:**
```
"Create approval request for workflow changes"
```

**Returns:** Approval request ID and status.

---

### `rbac_approve_request`
Approve a pending approval request.

**Parameters:**
- `request_id` (required): Request ID
- `approver_id` (required): Approver user ID

**Usage:**
```
"Approve request req123"
```

**Returns:** Confirmation of approval.

---

### `rbac_reject_request`
Reject a pending approval request.

**Parameters:**
- `request_id` (required): Request ID
- `approver_id` (required): Approver user ID
- `reason` (required): Rejection reason

**Usage:**
```
"Reject request req123: 'Security concerns'"
```

**Returns:** Confirmation of rejection.

---

### `rbac_get_pending_approvals`
List pending approval requests.

**Parameters:**
- `user_id` (optional): Filter by user

**Usage:**
```
"Show pending approvals"
```

**Returns:** List of pending requests.

---

### `rbac_create_tenant`
Create a new tenant for multi-tenancy.

**Parameters:**
- `tenant_id` (required): Tenant ID
- `name` (required): Tenant name

**Usage:**
```
"Create tenant for customer ABC"
```

**Returns:** Tenant details.

---

### `rbac_get_audit_log`
Get audit log of actions.

**Parameters:**
- `limit` (optional): Number of entries
- `user_id` (optional): Filter by user
- `action` (optional): Filter by action

**Usage:**
```
"Show audit log for john@example.com"
```

**Returns:** Audit log entries with timestamps and details.

---

## 🔍 Drift Detection

Track and analyze workflow changes over time.

### `detect_workflow_drift`
Detect changes in workflow compared to baseline.

**Parameters:**
- `workflow_id` (required): Workflow ID
- `baseline_version` (optional): Baseline version to compare

**Usage:**
```
"Detect drift in workflow abc123"
```

**Returns:** Drift report showing all changes since baseline.

---

## 📝 Version Information

- **Latest Version:** v1.14.0
- **Last Updated:** 2025-12-16

### Recent Updates:
- **v1.14.0:** Added `delete_workflow` tool
- **v1.13.2:** Fixed `update_workflow` with smart merge
- **v1.13.1:** Intent metadata integration fixes
- **v1.13.0:** Intelligent Template System v2.0

---

## 🔗 Related Documentation

- [Quick Start Guide](QUICKSTART.md)
- [Examples & Use Cases](EXAMPLES.md)
- [Validation System](VALIDATION.md)
- [State Management](STATE_MANAGEMENT.md)
- [RBAC & Security](RBAC_SECURITY.md)
- [AI Feedback](AI_FEEDBACK.md)

---

**Need Help?** Just ask Claude! 😉
