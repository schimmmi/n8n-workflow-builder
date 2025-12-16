# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2025-12-16

### 🤖 Added - AI Feedback & Error Analysis System

#### New Features
- **AIFeedbackAnalyzer Class**: Intelligent error analysis for failed workflow executions
- **Pattern Recognition**: Automatically detects 6+ common failure types
- **Root Cause Identification**: Auth, Network, Data, SQL, Rate Limiting, Parameters
- **AI-Friendly Feedback**: Structured guidance specifically designed for AI agents
- **Fix Examples**: Wrong vs. Correct code comparisons for each error type
- **Workflow Improvements**: Node-specific recommendations for fixing failures
- **Learning Loop**: Enables AI agents to learn from errors and improve

#### Error Pattern Detection
**Detects and provides guidance for:**
1. **Authentication/Authorization** (401, 403, unauthorized) - Credential configuration issues
2. **Network/Connection** (timeout, ECONNREFUSED) - Connection and timeout problems
3. **Data/Type** (undefined, null, type errors) - Data structure and validation issues
4. **Database/SQL** (syntax, query errors) - SQL query and database problems
5. **Rate Limiting** (429, too many requests) - API rate limit violations
6. **Missing/Invalid Parameters** - Configuration and parameter issues

#### New MCP Tools
1. **`analyze_execution_errors`**: Analyze failed executions with AI-friendly feedback
   - Root cause identification
   - Structured suggestions
   - Fix examples with code
   - AI guidance for future workflow generation

2. **`get_workflow_improvement_suggestions`**: Generate specific improvement recommendations
   - Nodes to modify (with specific field changes)
   - Nodes to add (error handlers, delays, etc.)
   - Parameter updates
   - Configuration fixes

#### AI Guidance Features
**For each error type, provides:**
- Root cause explanation
- Step-by-step suggestions
- AI-specific guidance on how to generate better workflows
- Code examples (wrong vs. correct)
- Node configuration recommendations

**Example AI Guidance:**
```
Authentication Error:
1. Use {{$credentials.name}} instead of hardcoded values
2. Specify correct authentication type (Bearer, Basic, OAuth)
3. Include proper headers (Authorization, API-Key)
4. Test credentials before deploying
```

#### Improvement Suggestions
**Generates:**
- **Nodes to Modify**: Specific fields to change in failing nodes
- **Nodes to Add**: Missing nodes (error handlers, delays, validation)
- **Parameter Changes**: Exact values and reasons
- **Best Practices**: Context-aware recommendations

#### New Documentation
- Added `docs/AI_FEEDBACK.md` - Complete AI feedback system guide (450+ lines)
- Error pattern reference
- Integration examples
- Learning loop workflows
- Analytics & insights

### 🔧 Technical Implementation
- `AIFeedbackAnalyzer` class with pattern recognition
- Error extraction from execution data
- Structured feedback generation
- Node-specific improvement suggestions
- Formatted markdown reports for AI/humans

### 📚 Benefits
- **AI Learning**: AI agents learn from failures and improve workflow generation
- **Faster Debugging**: Root cause identification speeds up troubleshooting
- **Better Workflows**: Specific guidance leads to higher quality workflows
- **Prevents Repeated Errors**: AI remembers patterns and avoids same mistakes
- **Actionable Feedback**: Not just "what" failed, but "how" to fix it

### 🎯 Use Cases
- AI workflow generation with feedback loops
- Automated workflow debugging
- Learning from production failures
- Self-healing workflows
- Error pattern analytics
- Developer assistance and training

### 🔄 Integration with Existing Features
- Works seamlessly with validation system
- Integrates with state management (logs analysis actions)
- Complements error debugging tools
- Enhances workflow generation capabilities

## [1.2.0] - 2025-12-16

### ✨ Added - Workflow Validation System

#### New Features
- **WorkflowValidator Class**: Comprehensive pre-deployment validation middleware
- **3-Layer Validation**:
  1. Schema validation (structure, required fields, data types)
  2. Semantic validation (logic, connections, best practices)
  3. Parameter validation (node-specific checks)
- **Security Checks**: Detects hardcoded credentials, missing authentication, SQL injection risks
- **Quality Enforcement**: Warns about default names, missing error handling, high complexity

#### Validation Rules
**Schema Validation (20+ checks):**
- Required workflow fields (`name`, `nodes`, `connections`)
- Node structure validation (required fields, types, positions)
- Connection structure validation

**Semantic Validation (10+ checks):**
- At least one trigger node required
- No duplicate node names
- No orphaned nodes (disconnected)
- Hardcoded credentials detection
- Workflow complexity check (>30 nodes warning)
- Missing error handling warning

**Parameter Validation (Node-Specific):**
- Webhook: `path` required, authentication recommended
- HTTP Request: `url` required, timeout recommended
- Schedule Trigger: schedule/cron required
- IF: conditions should be defined
- Postgres: avoid `SELECT *`, use parameterized queries
- Set: values should be configured
- Code: code required, should return items array

#### New MCP Tools
1. **`validate_workflow`**: Validate existing workflow by ID before deployment
2. **`validate_workflow_json`**: Validate workflow JSON structure before creation

#### Security Features
- **Credential Detection**: Scans for `password`, `apikey`, `secret`, `token` keywords
- **Authentication Check**: Warns about unauthenticated webhooks
- **SQL Injection Prevention**: Warns about non-parameterized queries

#### New Documentation
- Added `docs/VALIDATION.md` - Complete validation system guide (350+ lines)
- Validation examples and use cases
- Security best practices
- Rule reference table
- Integration workflow guide

### 🔧 Technical Implementation
- `WorkflowValidator` class with static validation methods
- Comprehensive error/warning categorization
- Detailed validation reports with summary statistics
- Extensible validation architecture

### 📚 Benefits
- **Catch Errors Early**: Find issues in dev, not production
- **Security**: Prevent credential leaks and authentication issues
- **Quality**: Enforce n8n best practices automatically
- **Developer Experience**: Clear error messages with actionable fixes
- **Deployment Safety**: Validate before activating workflows

### 🎯 Use Cases
- Pre-deployment validation checks
- Template validation before creation
- Security audits of existing workflows
- Learning best practices (warnings are educational)
- CI/CD integration for workflow quality gates

## [1.1.0] - 2025-12-16

### ✨ Added - State Management & Context Tracking

#### New Features
- **StateManager Class**: Persistent state management across Claude sessions
- **Active Workflow Tracking**: Automatically tracks the workflow you're currently working on
- **Session History**: Logs all actions with timestamps and details (last 50 entries kept)
- **Recent Workflows**: Remembers your last 10 accessed workflows
- **Last Execution Tracking**: Automatically stores the last workflow execution ID

#### New MCP Tools
1. **`get_session_state`**: View complete session state (active workflow, recent workflows, history)
2. **`set_active_workflow`**: Manually set a workflow as the active one
3. **`get_active_workflow`**: Get the currently active workflow
4. **`get_recent_workflows`**: List of last 10 workflows with timestamps
5. **`get_session_history`**: View action history with details
6. **`clear_session_state`**: Reset all session state and history

#### Enhanced Existing Tools
- `get_workflow_details`: Now automatically sets workflow as active and logs the action
- `analyze_workflow`: Now automatically sets workflow as active and logs the action
- `execute_workflow`: Now stores execution ID and logs the action
- `update_workflow`: Now logs the update action

#### State Persistence
- State stored in `~/.n8n_workflow_builder_state.json`
- Survives Claude Desktop restarts and different chat sessions
- Automatic cleanup (FIFO for workflows/history)
- Error handling for corrupted state files with automatic reset

#### New Documentation
- Added `docs/STATE_MANAGEMENT.md` - Complete state management guide (240+ lines)
- Added `docs/state_example.json` - Example state file structure
- Updated README with state management section and usage examples
- Added CHANGELOG.md with version history

### 🔧 Technical Changes
- Added `pathlib.Path` import for cross-platform file handling
- New `STATE_FILE` constant pointing to `~/.n8n_workflow_builder_state.json`
- Enhanced logging for all state operations (set workflow, log action, etc.)
- Graceful degradation when state file is missing or corrupted

### 📚 Benefits
- **Context Awareness**: Reference workflows by "current workflow" instead of IDs
- **Better UX**: No need to remember workflow/execution IDs between sessions
- **Traceability**: See exactly what you did and when with full action history
- **Multi-Session Support**: Continue work seamlessly from where you left off
- **Privacy First**: All state stays local on your machine, no external sync

### 🎯 Use Cases Enabled
- "Analyze the current workflow" - uses automatically tracked active workflow
- "What was I working on?" - shows recent workflows and actions
- "Show the last execution" - uses stored execution ID
- "Continue where I left off" - loads previous session context

## [1.0.0] - 2024-12-14

### Added
- Initial release of n8n Workflow Builder MCP Server
- AI-powered workflow node suggestions based on natural language descriptions
- Workflow template generation for common use cases (API endpoints, scheduled reports, data sync)
- Workflow analysis for identifying issues and optimization opportunities
- Node explanation system with best practices and use cases
- Workflow error debugging with common solutions
- Complete MCP server implementation with 9 tools:
  - `suggest_workflow_nodes` - Get AI-powered node suggestions
  - `generate_workflow_template` - Generate complete workflow templates
  - `analyze_workflow` - Analyze workflows for issues
  - `list_workflows` - List all workflows with filtering
  - `get_workflow_details` - Get detailed workflow information
  - `execute_workflow` - Execute workflows manually
  - `get_executions` - View workflow execution history
  - `explain_node` - Get detailed node explanations
  - `debug_workflow_error` - Debug workflow errors
- Comprehensive knowledge base for n8n nodes covering:
  - Triggers (Webhook, Schedule, Manual)
  - Logic nodes (IF, Switch, Merge, Code)
  - Data operations (HTTP Request, Set, Function)
  - Storage (Postgres, Redis)
  - Integrations (Slack, Telegram, Gmail)
- Docker support with Dockerfile and docker-compose.yml
- Complete documentation in English:
  - README.md with setup instructions
  - QUICKSTART.md for quick 5-minute setup
  - EXAMPLES.md with practical use cases
- Python package structure with proper module organization
- Test suite for connection and workflow builder functionality
- Environment configuration with .env support
- Development tools configuration (black, ruff, pytest)

### Technical Details
- Built with Python 3.11+
- Uses MCP (Model Context Protocol) for Claude integration
- Async/await architecture with httpx for n8n API communication
- Comprehensive error handling and logging
- Support for n8n API v1

### Documentation
- Quick start guide for 5-minute setup
- 5 practical scenario examples
- Best practices and common pitfalls
- Troubleshooting guide
- Power combos for advanced usage

[1.0.0]: https://github.com/yourusername/n8n-workflow-builder/releases/tag/v1.0.0
