# 🚀 n8n Workflow Builder MCP Server

An **awesome** MCP server for n8n that helps you build, optimize, and debug workflows - directly from Claude! 🎯

## 🌟 Features

### 🧠 AI-Powered Workflow Design
- **Smart Node Suggestions**: Simply describe what you want to build, and the server suggests the perfect nodes
- **Template Generator**: Generates complete workflow structures from natural language
- **Best Practices**: Knows n8n best practices and warns you about common mistakes

### 🔍 Workflow Analysis & Debugging
- **Workflow Analyzer**: Scans your workflows for issues and optimization potential
- **Error Debugger**: Helps you understand and fix workflow errors
- **Security Checker**: Finds hardcoded credentials and other security problems

### 📊 Workflow Management
- **List & Filter**: Overview of all workflows with status and info
- **Details View**: Detailed information about each workflow
- **Execution Tracking**: View past executions with status and errors
- **Workflow Editing**: Edit workflows - change names, modify nodes, adjust settings
  - ⚠️ Note: `active` and `tags` fields are read-only and can only be changed in the n8n UI

### ⚡ Workflow Execution & Monitoring
- **Manual Trigger**: Start workflows directly from Claude (only for workflows with Manual/Webhook triggers)
- **Custom Input Data**: Pass dynamic data to your workflows
- **Execution Details**: Retrieve complete node input/output data for each execution
- **Execution History**: List of all past executions with status

### 🔄 Session State & Context Management
- **Active Workflow Tracking**: Automatically tracks which workflow you're currently working on
- **Session History**: Logs all your actions (analyze, execute, update, etc.)
- **Recent Workflows**: Quick access to your last 10 workflows
- **Persistent State**: Context survives between Claude conversations
- **Smart Context**: Reference workflows by "current" or "last workflow" instead of IDs

### ✅ Workflow Validation & Quality Assurance
- **Pre-Deployment Validation**: Comprehensive checks before deploying workflows
- **Schema Validation**: Ensures workflow structure is correct (required fields, types, etc.)
- **Semantic Validation**: Checks logical rules (trigger nodes, connections, duplicates)
- **Parameter Validation**: Node-specific parameter checks (webhooks, HTTP, databases, etc.)
- **Security Checks**: Detects hardcoded credentials, missing authentication
- **Best Practices**: Warns about default names, missing error handling, complexity

### 🤖 AI Feedback & Error Analysis
- **Intelligent Error Analysis**: Analyzes failed executions and identifies root causes
- **Pattern Recognition**: Detects common failure types (auth, network, data, SQL, rate limiting)
- **AI-Friendly Feedback**: Structured guidance for AI agents generating workflows
- **Fix Examples**: Wrong vs. Correct code comparisons
- **Improvement Suggestions**: Node-specific recommendations for fixing failures
- **Learning Loop**: AI agents learn from errors and generate better workflows

### 📚 Knowledge Base
- **Node Encyclopedia**: Detailed explanations of all important n8n nodes
- **Use Cases & Examples**: Practical examples for each node type
- **Configuration Tips**: How to optimally configure each node

### 🔬 Semantic Workflow Analysis (NEW!)
- **Deep Logic Analysis**: Goes beyond schema validation to understand workflow semantics
- **12 Anti-Pattern Checks**: HTTP retry, loop completion, timezone config, IF paths, webhook security, infinite loops, credentials, N+1 queries, rate limiting, data validation, and more
- **LLM-Friendly Fixes**: Copy-paste ready code fixes for AI agents
- **Severity Levels**: Critical, High, Medium, Low prioritization
- **Detailed Explanations**: Why each issue matters and how it impacts workflows
- **Security Scanning**: Detects hardcoded credentials with regex patterns
- **Performance Analysis**: Identifies bottlenecks like N+1 queries
- **Formatted Reports**: Structured output optimized for AI consumption

### 🎯 Template Library & AI Recommendations
- **10+ Pre-Built Templates**: Ready-to-use workflow templates for common use cases
- **AI-Powered Recommendations**: Get intelligent template suggestions based on your description
- **Smart Relevance Scoring**: Advanced algorithm matches templates to your requirements (70-90% accuracy)
- **Category Browse**: Templates organized by category (API, Reporting, Integration, etc.)
- **Difficulty Levels**: Beginner, Intermediate, and Advanced templates
- **Full-Text Search**: Search across names, descriptions, tags, and use cases
- **Template Details**: Complete implementation guides with estimated time and node structure

### 💭 Intent Metadata & AI Context (NEW!)
- **"Why" Documentation**: Attach reasoning, assumptions, and risks to each node
- **AI Context Continuity**: LLMs remember why nodes exist across iterations
- **5 Intent Fields**: reason, assumption, risk, alternative, dependency
- **Coverage Analysis**: Track which nodes have intent metadata
- **AI-Generated Suggestions**: Get intent templates for undocumented nodes
- **Workflow Understanding**: Understand existing workflows faster
- **Learning Loop**: AI agents learn from past decisions

### 🔄 Execution-Aware Feedback Loop (NEW!)
- **Real-Time Monitoring**: Watch workflow executions and get instant error feedback
- **Error Simplification**: Complex n8n errors simplified for AI agents
- **Context Extraction**: Get full error context (node, input, output, error details)
- **Pattern Analysis**: Analyze error patterns across multiple executions
- **Success Rate Tracking**: Monitor workflow reliability over time
- **Fix Suggestions**: Specific recommendations for fixing failed nodes
- **LLM-Optimized Output**: Structured feedback designed for AI consumption

### 📊 Drift Detection & Degradation Analysis (NEW!)
- **Temporal Analysis**: Compare baseline vs current execution patterns
- **4 Drift Patterns**: Success rate drift, performance drift, new error patterns, error frequency drift
- **Change Point Detection**: Find exactly when workflows started breaking
- **Gradual vs Sudden**: Classify changes as gradual degradation or sudden breaks
- **Root Cause Analysis**: Evidence-based determination of why workflows fail
- **Confidence Scoring**: 0.0-1.0 confidence for all analysis results
- **Actionable Fixes**: Error-type specific suggestions with concrete node changes
- **7 Root Causes**: API rate limits, external dependency failures, data schema changes, credential expiry, resource exhaustion, logic bugs, configuration drift
- **Testing Recommendations**: Specific testing steps before and after fixes

### 📖 Explainability Layer (NEW!)
- **Comprehensive Documentation**: Automatic, audit-ready workflow documentation
- **Purpose Analysis**: Explains WHY workflows exist with business domain classification (10 domains)
- **Data Flow Tracing**: Complete data lineage from sources → transformations → destinations
- **Dependency Mapping**: Maps internal workflows + 25+ external services (Slack, Stripe, AWS, etc.)
- **Risk Assessment**: 5 risk categories (data loss, security, performance, availability, compliance)
- **Mitigation Plans**: Prioritized, actionable recommendations with confidence scores
- **Multi-Format Export**: Markdown (docs), JSON (APIs), Plain Text (console)
- **AI-Native**: Designed for LLM consumption with structured, consistent output
- **Zero Configuration**: Works instantly with any n8n workflow

## 🎯 Use Cases

### 1. From Workflow Idea to Finished Structure
```
You: "I need a workflow that fetches data from our Postgres DB daily at 9am,
     calculates metrics, and sends a report via Slack"

Claude + MCP: Generates complete workflow structure with:
- Schedule Trigger (daily at 9am)
- Postgres Node (with query example)
- Function Node (metric calculation)
- Set Node (report formatting)
- Slack Node (with best practices)
```

### 2. Workflow Debugging
```
You: "My workflow throws 'timeout exceeded' errors"

Claude + MCP: Analyzes and suggests:
- Increase timeout settings
- Add retry logic
- Process data in batches
- Check external service performance
```

### 3. Workflow Optimization
```
You: "Analyze my workflow 'Daily Report Generator'"

Claude + MCP: Finds:
- 3 hardcoded API Keys (Security Issue!)
- Workflow could be split into 2 sub-workflows
- Missing error handling
- Node "HTTP Request" should be renamed
```

### 4. Smart Template Recommendations (NEW!)
```
You: "I need to send notifications to multiple channels when events occur"

Claude + MCP: Recommends:
1. Multi-Channel Notification System (85% match) - Beginner
   - Perfect for system alerts and status updates
   - Sends to Slack, Telegram, and Email simultaneously
   - Estimated time: 20 minutes

2. Global Error Handler (62% match) - Intermediate
   - Catches workflow errors and alerts team
   - Includes logging and notification features
   - Estimated time: 25 minutes

Use template 'notification_system' to get started!
```

### 5. Drift Detection (NEW!)
```
You: "My workflow was working fine last month, but now it keeps failing. What happened?"

Claude + MCP: Analyzes execution history with detect_workflow_drift:
📊 Drift Detected - Severity: CRITICAL

Metrics Comparison:
- Success Rate: 95% → 62% (-33%)
- Avg Duration: 1200ms → 1850ms (+54%)

Detected Patterns:
🔴 New Error Pattern: "429 Rate Limit Exceeded" (appeared 2 weeks ago)
⚠️ Performance Drift: Response times doubled gradually over 10 days

Next: Use get_drift_root_cause for detailed analysis
```

```
You: "What caused this drift?"

Claude + MCP: Uses get_drift_root_cause:
Root Cause: api_rate_limit_introduced
Confidence: 85%

Evidence:
- Rate limit errors appeared where none existed before
- Error started exactly 14 days ago
- Only affects HTTP Request nodes calling external API

Recommended Action:
Add request throttling or implement exponential backoff
```

```
You: "How do I fix it?"

Claude + MCP: Uses get_drift_fix_suggestions:
🔧 Suggested Fixes:

1. Add delay between requests (Node: Fetch User Data)
   - Add 'Wait' node with 1-2 second delay
   - Confidence: 85%

2. Implement retry logic with exponential backoff
   - Use 'HTTP Request' retry settings: 3 attempts, exponential delay
   - Confidence: 90%

Testing Recommendations:
✅ Test with rate-limited API first
✅ Monitor execution duration after changes
✅ Verify error rate drops below 5%
```

### 6. Workflow Explainability (NEW!)
```
You: "I need to document the 'Payment Processing' workflow for our SOC 2 audit"

Claude + MCP: Uses explain_workflow with markdown format

# Workflow Explanation: Payment Processing

## Executive Summary
Purpose: Automatically responds to events for e-commerce operations |
Business Domain: e-commerce | Type: event_driven |
Data flows from Webhook → 8 transformations → PostgreSQL, Slack, Email |
Depends on 4 external services | Risk Level: MEDIUM

## Purpose Analysis
**Primary Purpose**: Automatically responds to events for e-commerce operations
**Business Domain**: e-commerce
**Workflow Type**: event_driven
**Confidence**: 85%

## Data Flow
Input Sources: Order Webhook
Transformations: Validate Order → Calculate Totals → Check Inventory
Output Destinations: Save Order (PostgreSQL), Notify Team (Slack), Email Customer

## Dependencies
External Services:
- PostgreSQL (database)
- Slack (messaging)
- SendGrid (email)

⚠️ Single Points of Failure:
- Database used by 2 nodes
- High-criticality credential affects 2 nodes

## Risk Assessment
**Overall Risk Level**: MEDIUM (Score: 4.8/10)

🔴 Data Loss Risks:
- [HIGH] Database operation without transaction management (Save Order)

🔐 Security Risks:
- [HIGH] 3 high-criticality credentials in use

⚠️ Performance Risks:
- [MEDIUM] No rate limiting on external API calls (Check Inventory)

🛠️ Mitigation Plan:
1. [HIGH] Add error handling and retry logic
2. [HIGH] Ensure credentials are rotated regularly
3. [MEDIUM] Add rate limiting to API calls

Perfect for: Audit documentation, onboarding, risk assessment
```

```
You: "Which workflows will be affected if api.stripe.com goes down?"

Claude + MCP: Uses map_dependencies for all workflows

Affected Workflows (3):
1. Payment Processing
   - Nodes: Process Payment, Refund
   - Severity: CRITICAL

2. Subscription Manager
   - Nodes: Create Subscription, Cancel
   - Severity: HIGH

3. Invoice Generator
   - Nodes: Get Customer, Create Invoice
   - Severity: MEDIUM

Total Impact: 3 workflows, 6 nodes affected
Recommendation: Plan maintenance window and notify stakeholders
```

## 📦 Installation

### 1. Install Dependencies
```bash
cd n8n-workflow-builder
pip install -r requirements.txt
```

### 2. Configuration
```bash
# Create .env file
cp .env.example .env

# Get n8n API Key:
# 1. Go to your n8n instance: https://your-n8n-instance.com
# 2. Settings > API
# 3. "Create New API Key"
# 4. Copy key and paste into .env
```

**Your .env should look like this:**
```env
N8N_API_URL=https://your-n8n-instance.com
N8N_API_KEY=n8n_api_abc123xyz...
```

### 3. Test Server
```bash
# Quick Test
python server.py
# Should not throw errors - if it does, check your .env!
```

### 4. Claude Desktop Integration

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

#### Option 1: With Virtual Environment (Recommended)
```json
{
  "mcpServers": {
    "n8n-workflow-builder": {
      "command": "/ABSOLUTE/PATH/TO/n8n-workflow-builder/.venv/bin/python",
      "args": ["-m", "n8n_workflow_builder"],
      "env": {
        "N8N_API_URL": "https://your-n8n-instance.com",
        "N8N_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

#### Option 2: With Global Python
```json
{
  "mcpServers": {
    "n8n-workflow-builder": {
      "command": "python",
      "args": [
        "-m", "n8n_workflow_builder"
      ],
      "env": {
        "N8N_API_URL": "https://your-n8n-instance.com",
        "N8N_API_KEY": "your_api_key_here",
        "PYTHONPATH": "/ABSOLUTE/PATH/TO/n8n-workflow-builder/src"
      }
    }
  }
}
```

#### Option 3: Direct with server.py (Legacy)
```json
{
  "mcpServers": {
    "n8n-workflow-builder": {
      "command": "python",
      "args": [
        "/ABSOLUTE/PATH/TO/n8n-workflow-builder/src/n8n_workflow_builder/server.py"
      ],
      "env": {
        "N8N_API_URL": "https://your-n8n-instance.com",
        "N8N_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

#### Option 4: With .env File (Most Secure)
```json
{
  "mcpServers": {
    "n8n-workflow-builder": {
      "command": "/ABSOLUTE/PATH/TO/n8n-workflow-builder/.venv/bin/python",
      "args": ["-m", "n8n_workflow_builder"],
      "cwd": "/ABSOLUTE/PATH/TO/n8n-workflow-builder"
    }
  }
}
```
With this option, credentials are read from the `.env` file.

**IMPORTANT**:
- Replace `/ABSOLUTE/PATH/TO/` with your actual path!
- Windows users: Use `\\` or `/` as path separator
- Windows Python path: `.venv\Scripts\python.exe` instead of `.venv/bin/python`

### 5. Restart Claude Desktop
Completely quit and reopen - then the MCP server should be available! 🎉

## 🎮 Usage Examples

### Get Node Suggestions
```
You: "Suggest nodes for: API endpoint that validates data and writes to a database"

Claude uses: suggest_workflow_nodes
→ You get suggestions for Webhook, IF, HTTP Request, Postgres, etc.
```

### Generate Complete Workflow
```
You: "Generate a workflow for daily sales reports from Postgres to Slack"

Claude uses: generate_workflow_template
→ You get complete structure with all nodes, connections, and config tips
```

### Analyze Workflow
```
You: "Analyze my workflow with ID abc-123"

Claude uses: analyze_workflow
→ Finds issues, security problems, gives optimization suggestions
```

### Explore Node Details
```
You: "Explain the HTTP Request node"

Claude uses: explain_node
→ You get detailed explanation, use cases, best practices, examples
```

### Debug Errors
```
You: "My workflow throws: Error 401 Unauthorized"

Claude uses: debug_workflow_error
→ You get troubleshooting steps, likely causes, solutions
```

### List Workflows
```
You: "Show me all active workflows"

Claude uses: list_workflows
→ List of all workflows with status, node count, update date
```

### Execute Workflow
```
You: "Execute workflow 'Test API' with input {userId: 123}"

Claude uses: execute_workflow
→ Workflow is triggered, you see execution status
```

### Create Workflow
```
You: "Create a workflow called 'Test API' with a manual trigger and HTTP request node"

Claude uses: create_workflow
→ Workflow is created with all nodes and connections
→ Returns workflow ID and next steps
```

### Edit Workflow
```
You: "Rename workflow abc-123 to 'Production Data Sync'"

Claude uses: update_workflow
→ Workflow is renamed
```

### Get Template Recommendations (NEW!)
```
You: "Recommend templates for sending automated email notifications"

Claude uses: recommend_templates
→ Gets AI-powered recommendations with relevance scores:
  1. Email Automation & Processing (68% match) - Intermediate
  2. Multi-Channel Notification System (54% match) - Beginner
  3. Global Error Handler (42% match) - Intermediate
```

### Browse Template Library (NEW!)
```
You: "Show me all templates for API development"

Claude uses: get_templates_by_category (category: "api")
→ Lists:
  - Simple API Endpoint (Beginner)
  - API Rate Limiter & Queue (Advanced)
```

### Search Templates (NEW!)
```
You: "Find templates about database sync"

Claude uses: search_templates
→ Finds all templates containing 'database' or 'sync'
```

### Get Template Details (NEW!)
```
You: "Show me details for the notification_system template"

Claude uses: get_template_details
→ Complete template info:
  - Node structure
  - Implementation guide
  - Estimated time: 20 minutes
  - Use cases and best practices
```

### Semantic Workflow Analysis (NEW!)
```
You: "Analyze workflow 'Payment Processing' for logic issues"

Claude uses: analyze_workflow_semantics
→ Deep semantic analysis report:
  🚨 Critical Issues:
  - SplitInBatches without completion loop (Node: Split Orders)
  - Hardcoded API key detected (Node: Payment Gateway)

  ⚠️ High Priority:
  - HTTP Request without retry logic (Node: Payment Gateway)
  - IF node without false path (Node: Check Amount)
  - Webhook without authentication (Node: Webhook Trigger)

  💡 Recommendations:
  - Add error handling for external API calls
  - Consolidate 3 consecutive Set nodes for better performance

  🤖 LLM Fixes: Copy-paste ready code for each issue
```

### Get Execution Details
```
You: "Show me details for execution 47885"

Claude uses: get_execution_details
→ Shows complete node input/output data, errors, status, etc.
```

**Important:** To see execution data, the following options must be enabled in n8n Settings > Executions:
- ✅ Save manual executions
- ✅ Save execution progress

### Context & State Management
```
You: "What workflow was I working on?"

Claude uses: get_session_state
→ Shows active workflow, recent workflows, and action history
```

```
You: "Analyze the current workflow"

Claude: Uses the last active workflow automatically
```

```
You: "Show me my recent workflows"

Claude uses: get_recent_workflows
→ List of last 10 workflows with timestamps
```

```
You: "What did I do in this session?"

Claude uses: get_session_history
→ Timeline of all actions (analyze, execute, update, etc.)
```

### Workflow Validation
```
You: "Validate workflow abc-123 before deploying"

Claude uses: validate_workflow
→ Comprehensive validation report with errors and warnings
```

**Example Output:**
```
❌ Validation Failed

Errors (must fix):
1. Webhook node 'API Endpoint': No authentication enabled (security risk)
2. Node 'HTTP Request': Missing 'url' parameter
3. Duplicate node names found: Set

Warnings (should fix):
1. Nodes with default names (should be renamed): HTTP Request, Set
2. Postgres node 'Database Query': Using SELECT * (bad practice)
3. Workflow lacks error handling (Error Trigger node)
```

```
You: "Validate this workflow JSON before creating it"

Claude uses: validate_workflow_json
→ Validates structure before workflow creation
```

### Intent Metadata (NEW!)
```
You: "Add intent to node 'Process Payment' explaining why it exists"

Claude uses: add_node_intent
→ Adds reason, assumptions, risks, alternatives to node metadata
```

```
You: "Show me all intent metadata for this workflow"

Claude uses: get_workflow_intents
→ Markdown report showing "why" behind each node
```

```
You: "Analyze intent coverage for workflow abc-123"

Claude uses: analyze_intent_coverage
→ Coverage: 75% (6/8 nodes documented)
→ Critical nodes missing intent: Payment Gateway, Error Handler
```

### Execution Monitoring (NEW!)
```
You: "Watch the execution of workflow 'API Sync'"

Claude uses: watch_workflow_execution
→ Real-time status with simplified error messages if failed
```

```
You: "Get detailed error context for execution 47885"

Claude uses: get_execution_error_context
→ Full error context: node, input, output, error details
→ Simplified error message for AI consumption
→ Fix suggestions with confidence scores
```

```
You: "Analyze error patterns for workflow 'Payment Processing'"

Claude uses: analyze_execution_errors (with workflow_id)
→ Success rate: 78% (78/100 executions)
→ Most common errors:
  1. "Timeout Error" in node "External API" (12 occurrences)
  2. "401 Unauthorized" in node "Auth Check" (10 occurrences)
```

### AI Error Analysis & Feedback
```
You: "My workflow failed with execution 12345, what went wrong?"

Claude uses: analyze_execution_errors (with execution_id)
→ AI-friendly error analysis with root cause and fixes
```

**Example Output:**
```
🔍 Execution Error Analysis: API Data Sync

❌ Status: Execution failed
🎯 Root Cause: Authentication/Authorization Error

🔴 Errors Detected:
1. Node: `Fetch User Data` - 401 Unauthorized

🤖 AI Guidance:
When generating workflows, ensure:
1. Use credential references: {{$credentials.name}} not hardcoded values
2. Specify correct authentication type (Bearer, Basic, OAuth)
3. Test credentials before deploying

📝 Fix Examples:
❌ Wrong: "apiKey": "sk-abc123"
✅ Correct: "authentication": "predefinedCredentialType"
```

```
You: "Get improvement suggestions for failed workflow"

Claude uses: get_workflow_improvement_suggestions
→ Node-specific fix recommendations
```

### Explainability (NEW!)

```
You: "Explain the 'Payment Processing' workflow"

Claude uses: explain_workflow
→ Complete documentation: purpose, data flow, dependencies, risks
→ Available formats: markdown (default), json, text
```

```
You: "What is the purpose of workflow abc-123?"

Claude uses: get_workflow_purpose
→ Business domain, workflow type, trigger description, expected outcomes
```

```
You: "Trace the data flow in this workflow"

Claude uses: trace_data_flow
→ Input sources, transformations, output destinations, critical paths
```

```
You: "Show me all dependencies for this workflow"

Claude uses: map_dependencies
→ Internal workflows, external services, credentials, single points of failure
```

```
You: "Assess the risks in this workflow"

Claude uses: analyze_workflow_risks
→ 5 risk categories with mitigation plan
→ Overall risk score and level
```

## 🧠 Knowledge Base

The server knows these node categories:

### Triggers
- **Webhook**: API endpoints, external integrations
- **Schedule**: Cron jobs, periodic tasks
- **Manual**: Testing, manual interventions

### Logic Nodes
- **IF**: Conditional branching
- **Switch**: Multi-way branching
- **Merge**: Combine data streams
- **Code**: Custom JavaScript/Python

### Data Operations
- **HTTP Request**: API calls
- **Set**: Data transformation
- **Function**: Complex data processing

### Storage
- **Postgres**: Relational database
- **Redis**: Caching, session storage

### Integrations
- **Slack**: Messaging & notifications
- **Telegram**: Bot integration
- **Gmail**: Email automation

## 🛠️ Advanced Features

### Custom Templates
The server comes with predefined templates:
- `api_endpoint`: Simple REST API
- `scheduled_report`: Daily/hourly reports
- `data_sync`: Database synchronization

### Security Checks
- Finds hardcoded credentials
- Warns about missing authentication
- Checks for insecure patterns

### Performance Analysis
- Calculate workflow complexity
- Detect oversized workflows
- Suggest splits for better maintainability

## 💾 State File

The server stores session state in `~/.n8n_workflow_builder_state.json`. This file contains:
- Currently active workflow
- Recent workflows (last 10)
- Session history (last 50 actions)
- Timestamps

This allows the server to maintain context between Claude conversations!

**To reset state:** Use the `clear_session_state` tool or delete the file manually:
```bash
rm ~/.n8n_workflow_builder_state.json
```

## 🐛 Troubleshooting

### Server Won't Start
```bash
# Check Python version (should be 3.8+)
python --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check .env
cat .env
# Should contain N8N_API_URL and N8N_API_KEY
```

### "Authentication failed"
- Check if your API key is correct
- Go to n8n Settings > API and create a new key
- Make sure there are no spaces in the key

### "Connection refused"
- Is your n8n instance reachable?
- Check: `curl https://your-n8n-instance.com/healthz`
- Firewall/VPN might be blocking

### Claude Desktop Doesn't Recognize Server
1. Completely quit Claude (also in background!)
2. Check config file (valid JSON?)
3. Paths absolute (not relative!)
4. Restart Claude
5. Check in Claude: Settings > Developer > MCP Servers

## 💡 Pro Tips

### 1. Workflow Naming
- **Always** rename nodes! "HTTP Request 1" is bad, "Fetch User Data" is good
- Use prefixes for categories: "[API] Get Users", "[DB] Insert Record"

### 2. Error Handling
- **Always** add error handling for critical workflows
- Use "Error Trigger" node for global error handling
- Log errors in Slack/Telegram for monitoring

### 3. Testing
- Always develop with "Manual Trigger" instead of direct webhook
- Use "Pinned Data" for consistent tests
- Split production/development workflows

### 4. Performance
- Batch API calls where possible
- Use Redis for caching
- Avoid too many sequential HTTP requests

### 5. Security
- **NEVER** hardcode API keys - always use credentials
- Enable webhook authentication
- Only store sensitive data encrypted

## 🔄 State Management Deep Dive

For detailed information about the state management and context tracking system, see:
- **[State Management Documentation](docs/STATE_MANAGEMENT.md)** - Complete guide
- **[State File Example](docs/state_example.json)** - Example state file

**Quick summary:**
- Automatically tracks active workflow
- Remembers last 10 workflows
- Logs last 50 actions with timestamps
- Persists between Claude sessions
- Stored in `~/.n8n_workflow_builder_state.json`

## ✅ Workflow Validation Deep Dive

For detailed information about the validation system, see:
- **[Validation Documentation](docs/VALIDATION.md)** - Complete validation guide

**Quick summary:**
- 3-layer validation: Schema, Semantics, Parameters
- 30+ validation rules
- Security checks (credentials, authentication, SQL injection)
- Node-specific parameter validation
- Comprehensive error/warning reports
- Validates before deployment

## 🤖 AI Feedback Deep Dive

For detailed information about the AI feedback system, see:
- **[AI Feedback Documentation](docs/AI_FEEDBACK.md)** - Complete AI feedback guide

**Quick summary:**
- Intelligent error pattern recognition
- Root cause identification (6+ error types)
- AI-friendly structured feedback
- Fix examples (wrong vs. correct)
- Workflow improvement suggestions
- Learning loop for AI agents

## 🔒 RBAC & Multi-Tenant Security Deep Dive

For detailed information about the security system, see:
- **[RBAC & Security Documentation](docs/RBAC_SECURITY.md)** - Complete enterprise security guide

**Quick summary:**
- 5 role types (Admin, Developer, Operator, Viewer, Auditor)
- 20+ granular permissions
- Multi-tenant isolation (separate workflows per tenant)
- Approval workflows for critical operations
- Comprehensive audit logging (SOC2, ISO27001, GDPR ready)
- Cannot approve own requests (separation of duties)

### RBAC Usage Examples

```
You: "Show me the RBAC status"
Claude uses: rbac_get_status
→ Shows users, roles, tenants, pending approvals, audit log

You: "Add user 'bob' as developer in tenant 'acme-corp'"
Claude uses: rbac_add_user
→ Creates user with developer permissions

You: "Check if bob can delete workflows"
Claude uses: rbac_check_permission
→ Shows if developer role has workflow.delete permission

You: "Bob wants to delete workflow abc-123, create approval request"
Claude uses: rbac_create_approval_request
→ Creates pending request for admin approval

You: "Approve request approval-123 as alice"
Claude uses: rbac_approve_request
→ Admin approves, operation can proceed

You: "Show audit log for last 24 hours"
Claude uses: rbac_get_audit_log
→ Shows all security events with timestamps
```

### Enterprise Features

✅ **Role-Based Access Control**
- 5 built-in roles with predefined permissions
- Granular permission checks before operations
- Flexible role assignment per user

✅ **Multi-Tenant Isolation**
- Complete data segregation between tenants
- Separate workflows, users, audit logs per tenant
- Tenant-based access control

✅ **Approval Workflows**
- 4 critical operations require approval
- Cannot approve own requests
- Full audit trail of approval decisions

✅ **Audit Logging**
- Last 500 security events stored
- Filter by user, action, timestamp
- Compliance-ready (SOC2, ISO27001, GDPR)

✅ **Security by Design**
- Least privilege principle
- Separation of duties
- Immutable audit logs
- No self-approval

## 🔄 Updates & Extensions

### Add Custom Nodes to Knowledge Base
Edit `server.py` and extend `NODE_KNOWLEDGE`:

```python
NODE_KNOWLEDGE["integrations"]["notion"] = {
    "name": "Notion",
    "desc": "Notion database integration",
    "use_cases": ["Knowledge base", "Project management"],
    "best_practices": ["Use database IDs", "Batch updates"]
}
```

### Create Custom Templates
Edit `WORKFLOW_TEMPLATES` in `server.py`:

```python
WORKFLOW_TEMPLATES["my_template"] = {
    "name": "My Custom Template",
    "nodes": [...],
    "connections": "custom"
}
```

## 📊 API Reference

The server uses the official n8n REST API:
- Base URL: `https://your-n8n-instance.com/api/v1`
- Docs: https://docs.n8n.io/api/

Used endpoints:
- `GET /workflows` - List workflows
- `GET /workflows/{id}` - Get workflow details
- `POST /workflows` - Create workflow
- `PUT /workflows/{id}` - Update workflow
- `POST /workflows/{id}/run` - Execute workflow
- `GET /executions` - Get execution history
- `GET /executions/{id}` - Get execution details

## 🤝 Contributing

Ideas? Issues? PRs welcome! 🎉

## 📊 Drift Detection Deep Dive

For detailed information about the drift detection system, see:
- **[Drift Detection Documentation](releases/v1.10.0.md)** - Complete drift detection guide

**Quick summary:**
- Temporal comparison: baseline (first 30%) vs current (last 30%) execution periods
- 4 drift patterns: success rate, performance, new errors, error frequency
- Change point detection: finds when metrics changed significantly
- 7 root cause types: rate limits, dependency failures, schema changes, credentials, resource exhaustion, logic bugs, config drift
- Confidence scoring: 0.0-1.0 for all analysis
- Actionable fixes: error-type specific with testing recommendations

## 💭 Intent Metadata Deep Dive

For detailed information about the intent metadata system, see:
- **[Intent Metadata Documentation](releases/v1.8.0.md)** - Complete intent system guide

**Quick summary:**
- "Why" documentation for each workflow node
- 5 fields: reason, assumption, risk, alternative, dependency
- AI context continuity across iterations
- Coverage analysis and suggestions
- Stored in node metadata (n8n native field)

## 🔄 Execution Monitoring Deep Dive

For detailed information about execution monitoring, see:
- **[Execution Monitoring Documentation](releases/v1.9.0.md)** - Complete monitoring guide

**Quick summary:**
- Real-time execution watching with error detection
- Error simplification for AI consumption
- Context extraction (node, input, output, error)
- Pattern analysis across multiple executions
- Fix suggestions with confidence scores

## 📖 Explainability Layer Deep Dive

For detailed information about the explainability layer, see:
- **[Explainability Layer Documentation](releases/v1.11.0.md)** - Complete explainability guide

**Quick summary:**
- Automatic, audit-ready workflow documentation
- Purpose analysis with business domain classification (10 domains)
- Complete data flow tracing (sources → transformations → sinks)
- Dependency mapping (internal workflows + 25+ external services)
- 5-category risk assessment (data loss, security, performance, availability, compliance)
- Multi-format export (Markdown/JSON/Plain Text)
- Zero configuration, works with any workflow

## 📝 License

MIT - Do whatever you want!

## 🙏 Credits

- Built for awesome n8n automation 🚀
- Powered by Claude MCP ⚡
- Made with ❤️ for DevOps Engineers

---

**Happy Automating!** 🎊

For questions or problems: Just ask Claude! 😉
