# Changelog

All notable changes to the n8n Workflow Builder MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.22.0] - 2025-01-09

### 🎉 Added - n8n 2.2.6 Compatibility

**Major Update**: Full compatibility with n8n version 2.2.6 including all breaking changes from n8n 2.0+

#### Compatibility Database Updates
- **Version Coverage**: Now tracks n8n versions 0.180.0 through 2.2.6
- **n8n 2.0 Breaking Changes**:
  - Start node removed (use Manual Trigger or Execute Workflow Trigger)
  - Execute Command and LocalFileTrigger nodes disabled by default
  - Code node security changes (task runners, env var blocking, Python Pyodide removed)
  - MySQL/MariaDB support dropped (PostgreSQL/SQLite only)
  - SQLite legacy driver removed (pooling driver only)
  - OAuth callback authentication required by default
- **n8n 2.1-2.2 Changes**:
  - Data Table Node CRUD enhancements
  - AI Agent Node message handling updates
  - CORS and path validation improvements

#### Enhanced Node Tracking
- Added 4 new nodes to compatibility database:
  - `n8n-nodes-base.start` (removed in 2.0)
  - `n8n-nodes-base.executeCommand` (disabled by default)
  - `n8n-nodes-base.localFileTrigger` (disabled by default)
  - `n8n-nodes-base.dataTable` (enhanced in 2.2)
- Updated Code node with version 2.1 security tracking
- Updated AI Agent node with version 1.10 tracking

#### Database Stats
- Total nodes tracked: 34 (was 30)
- Core nodes: 18 (was 14)
- Version milestones: 13 (was 9)
- Compatibility issues documented: 100+

### 📝 Changed
- Updated `pyproject.toml` version to 1.22.0
- Enhanced compatibility database metadata with n8n version support range
- Updated README.md with n8n 2.2.6 support information

### 📚 Documentation
- Added complete [v1.22.0 release notes](releases/v1.22.0.md)
- Updated README with n8n 2.0+ migration guidance
- Added Python 3.11+ requirement clarification

### ✅ Verified
- ✅ REST API unchanged in n8n 2.0+ (no client.py updates needed)
- ✅ All existing MCP server functionality remains compatible
- ✅ Migration engine detects all n8n 2.0+ breaking changes

## [1.21.0] - 2025-12-23

### 🔧 Fixed
- **`get_workflow_details`** now returns complete node details including:
  - All node parameters (including Code Node scripts in `parameters.code` field)
  - Parameters displayed as formatted JSON for better readability
  - Node position information
- Previous version only showed node names and types without their configuration details

### 📝 Changed
- Enhanced workflow details output format with better structure and markdown formatting
- Node information now includes comprehensive parameter data for debugging and analysis

## [1.19.0] - 2025-12-17

### 🎉 Added - Node Discovery System

**Major Feature**: Workflow-based learning system that discovers n8n nodes and provides intelligent recommendations.

#### New MCP Tools
- **`discover_nodes`** - Analyze workflows to discover node types
  - Scans all workflows via n8n API
  - Extracts node types, parameters, credentials
  - Tracks usage statistics and popularity
  - Infers parameter types from real data
  - Persists to SQLite (~/.n8n-mcp/node_discovery.db)

- **`get_node_schema`** - Get detailed schema for discovered nodes
  - Parameter names and inferred types
  - Credential requirements
  - Usage count across workflows
  - Real-world configuration examples

- **`search_nodes`** - Search nodes by keyword
  - Keyword matching in node type and name
  - Category classification (trigger, data_source, transform, notification, http, logic, utility)
  - Icon-based visual categorization (⚡📊🔄📬🌐🔀🔧)
  - Sorted by popularity

- **`recommend_nodes_for_task`** - AI-powered node recommendations
  - Natural language task descriptions
  - Advanced scoring algorithm (exact: 5pts, synonym: 2.5pts, parameter: +1pt)
  - Bidirectional synonym matching (40+ terms)
  - Popularity boost (max 3pts)
  - Detailed reason generation

#### Advanced Features

**Synonym Matching (Bidirectional)**
- `slack` ↔ telegram, discord, mattermost, matrix, chat, message
- `excel` ↔ sheets, spreadsheet, airtable, table
- `database` ↔ postgres, mysql, mongodb, sql, db
- `send` ↔ post, push, publish, transmit
- `read` ↔ get, fetch, retrieve, load
- `cloud` ↔ drive, dropbox, s3, storage
- 40+ comprehensive synonym mappings

**Parameter-Based Scoring**
- Bonus points for nodes with relevant parameters
- "email" task → finds nodes with "email" parameter
- Helps distinguish similar nodes by capabilities

**Category Tagging**
- 7 categories: trigger, data_source, transform, notification, http, logic, utility
- Auto-categorization based on node_type keywords
- Persisted in database for consistency
- Visual icons in search results

**Stopword Filtering**
- Filters 23 common English words (and, to, from, the, etc.)
- Filters words < 3 characters
- Improves matching relevance

#### Architecture

**Database Persistence**
- Location: `~/.n8n-mcp/node_discovery.db`
- SQLite with discovered_nodes table
- Stores node types, parameters, types, credentials, usage counts
- Auto-loads on server start
- Survives restarts

**Performance**
- Discovery: 10 workflows (~2s), 100 workflows (~15s)
- Recommendations: < 200ms for 100 nodes
- In-memory caching for fast queries

### 🐛 Fixed

**Synonym Matching Fixes**
- Fixed synonyms not appearing in recommendation reasons
- Fixed bidirectional synonym mapping
- Show original user keywords in "Similar:" section (not found synonyms)
- Example: User says "slack" → Telegram shows "Similar: slack" ✅

**Scope Fixes**
- Fixed `NameError: name 'node_recommender' is not defined`
- Changed `global` to `nonlocal` for proper nested function scope

### 🔄 Improved

**Scoring Algorithm**
- Increased exact keyword match from +2 to +5 points
- Added synonym match at +2.5 points (0.5x weight)
- Reduced popularity boost from +5 to +3 max
- Popularity only added if keywords match (prevents irrelevant popular nodes)
- Parameter matching adds +1 point bonus

**Recommendation Reasons**
- Shows exact keyword matches: "Matches: send, message"
- Shows synonym matches: "Similar: slack"
- Shows popularity: "highly popular" or "commonly used"
- Clear explanation of why node was recommended

### 📚 Documentation

**New Files**
- `docs/NODE_DISCOVERY.md` - Complete 850+ line guide
  - Overview and features
  - Architecture and data flow
  - Usage examples
  - Advanced features (synonyms, parameters, categories)
  - Best practices
  - Troubleshooting
  - Performance metrics
  - API reference

- `releases/v1.19.0.md` - Detailed release notes
  - Feature descriptions
  - Usage examples
  - Migration guide
  - Performance stats
  - Future roadmap

### ✅ Testing

Comprehensive testing with 42 real workflows:
- ✅ Discovery: 66 node types, 1644 instances
- ✅ Schema extraction: Full parameter schemas with types
- ✅ Search: Category-based filtering with icons
- ✅ Recommendations: Synonym matching verified
  - "send slack message" → Telegram with "Similar: slack"
  - "read excel spreadsheet" → Sheets with "Similar: excel"
  - "store files in cloud" → Drive with "Similar: cloud"

### 🔮 Future Enhancements

Planned for upcoming releases:
- Usage pattern analysis (common node combinations)
- Parameter value learning (suggest defaults)
- Workflow template mining (extract reusable patterns)
- Node deprecation detection (migration suggestions)
- Custom synonym dictionaries (user-defined, domain-specific)

---

## [1.18.1] - 2025-12-17

### 🐛 Fixed - Template System Bugfixes

**Critical fixes for template generation and details tools**

#### Fixed UnboundLocalError in generate_workflow_template
- **Issue**: Tool was throwing `UnboundLocalError: cannot access local variable 'WORKFLOW_TEMPLATES'`
- **Root Cause**: Duplicate local import caused Python to treat WORKFLOW_TEMPLATES as local variable
- **Fix**: Removed redundant import since WORKFLOW_TEMPLATES is already imported at module level
- **Commit**: `bb2b6fc`

#### Fixed UnboundLocalError in get_template_details
- **Issue**: Same UnboundLocalError when retrieving template details
- **Root Cause**: Direct access to WORKFLOW_TEMPLATES without proper fallback logic
- **Fix**: Refactored to use template registry with backward compatibility fallback
- **Commit**: `e85f877`

#### Enhanced get_template_details Output
- **Added**: Source, complexity, node count, purpose, external systems
- **Added**: Quality indicators (error handling, documentation)
- **Added**: Trust metrics (success rate, usage count)
- **Backward Compatible**: Old templates still work via fallback

### 📝 Technical Details
- Python scope issue: Local imports later in function make variables local throughout entire scope
- Solution: Import at module level, avoid local imports of module-level variables
- All template tools now verified working correctly

### ✅ Testing
- ✅ `generate_workflow_template` - Works correctly
- ✅ `get_template_details` - Works with enhanced metadata
- ✅ Backward compatibility - Old templates still accessible
- ✅ All other template tools - Verified safe

---

## [1.18.0] - 2025-12-17

### 🎯 Added - Drift Detection System

**Major Feature**: Proactive workflow quality monitoring that detects degradation before it becomes critical.

#### Drift Detection Tools
- **`detect_workflow_drift`** - Comprehensive drift analysis across all categories
  - General drift: Success rate, performance, error patterns
  - Schema drift: API response structure changes
  - Rate limit drift: 429 errors, throughput degradation
  - Data quality drift: Empty values, format violations
  - Root cause analysis with confidence scoring
  - Requires 20+ executions for reliable analysis

- **`analyze_drift_pattern`** - Deep dive into specific drift patterns
  - Change point detection (when drift started)
  - Gradual vs sudden classification
  - Pattern-specific potential causes
  - Actionable recommendations

- **`get_drift_fix_suggestions`** - Actionable fix recommendations
  - Node-specific suggestions
  - Severity-grouped fixes (Critical, Warning, Info)
  - Copy-paste ready code
  - Testing recommendations
  - Confidence scores (85-95%)

#### Drift Analysis Categories

**General Drift Detection:**
- Success rate drift (>15% threshold)
- Performance drift (>50% threshold)
- New error patterns
- Error frequency drift (2x threshold)

**Schema Drift Analysis:**
- Missing fields detection
- Type change tracking
- Null rate increase monitoring
- Structure change detection

**Rate Limit Drift Analysis:**
- 429 error tracking
- Retry frequency monitoring
- Throughput degradation detection
- Execution bunching pattern analysis
- Quota proximity warnings

**Data Quality Drift Analysis:**
- Empty value tracking
- Completeness monitoring
- Format validation (email, URL, date)
- Consistency scoring
- Output size tracking

#### Root Cause Detection

10+ evidence-based root causes with confidence scoring:
- `api_rate_limit_introduced` (85% confidence)
- `authentication_method_changed` (80% confidence)
- `api_response_format_changed` (75% confidence)
- `credential_expiration` (90% confidence)
- `rate_limit_tightened` (85% confidence)
- `external_service_slowdown` (75% confidence)
- `workflow_degradation` (70% confidence)
- And more...

#### Statistical Analysis
- Baseline vs Current period comparison (30% each)
- Change point detection algorithm
- Gradual vs sudden change classification
- Evidence collection and confidence scoring

#### Documentation
- Added `docs/DRIFT_DETECTION.md` - Complete 650+ line guide
- Added `releases/v1.18.0.md` - Detailed release notes
- Updated README with expanded drift detection section

### 🔬 Technical Details

**New Files:**
- `src/n8n_workflow_builder/drift/__init__.py`
- `src/n8n_workflow_builder/drift/detector.py` (763 lines)
- `src/n8n_workflow_builder/drift/analyzers/__init__.py`
- `src/n8n_workflow_builder/drift/analyzers/schema.py` (395 lines)
- `src/n8n_workflow_builder/drift/analyzers/rate_limit.py` (355 lines)
- `src/n8n_workflow_builder/drift/analyzers/quality.py` (410 lines)

**Modified Files:**
- `src/n8n_workflow_builder/server.py` - Added 3 MCP tools and handlers
- `README.md` - Expanded drift detection documentation

**Total Added**: ~2,100 lines of code + 650 lines documentation

### ✅ Testing
- Tested on production workflows with 50+ executions
- Successfully detected performance drift (+235%)
- Successfully detected success rate changes (+43%)
- Root cause analysis: 70-90% confidence scores
- All specialized analyzers fully functional

---

## [1.17.1] - 2025-12-16

### 🐛 Fixed - Security Detection
- Fixed Bearer Token detection regex to avoid false positives
- Fixed database URL detection to properly validate connection strings
- Improved secret detection accuracy

---

## [1.17.0] - 2025-12-15

### 🎯 Added - Enterprise Security & Governance

**Major Features:**
- Complete security audit system with 11 secret types
- Compliance validation (Basic, Strict, Enterprise standards)
- Role-Based Access Control (RBAC) with 5 roles
- Audit logging and approval workflows
- Critical findings filter

**Security Auditing:**
- Hardcoded secret detection (API keys, tokens, passwords, AWS keys, etc.)
- Entropy analysis for encrypted/encoded secrets
- Authentication auditing (missing/weak auth, insecure protocols)
- Exposure analysis (public webhooks, PII leaks, CORS issues)
- Security scoring (0-100) with risk levels

**RBAC System:**
- 5 roles: admin, developer, operator, viewer, auditor
- Multi-tenant support
- Granular permissions
- Approval workflows for sensitive operations

**New Tools:**
- `audit_workflow_security` - Complete security audit
- `get_security_summary` - Quick security overview
- `check_compliance` - Compliance standard validation
- `get_critical_findings` - Critical/high severity issues only
- RBAC management tools (add user, create tenant, request approval, etc.)

---

## [1.16.0] - 2025-12-10

### 🎯 Added - Template System v2

**Template Discovery:**
- GitHub repository template discovery
- Full repository import with validation
- Template intent-based search
- Match explanation with confidence scores

**Template Management:**
- Template registry with caching
- Intent extraction from descriptions
- Similarity-based matching
- Provenance tracking

**New Tools:**
- `discover_github_templates` - Find templates in GitHub repos
- `import_github_repo` - Import entire template repositories
- `search_templates_by_intent` - Intent-based template search
- `explain_template_match` - Match confidence explanation

---

## [1.15.0] - 2025-12-05

### 🎯 Added - Explainability Layer

**Workflow Understanding:**
- Comprehensive workflow documentation
- Purpose analysis with business domain classification
- Data flow tracing
- Dependency mapping
- Risk analysis

**Documentation:**
- Automatic audit-ready documentation generation
- Plain language explanations
- Technical documentation for developers
- Business-focused summaries

**New Tools:**
- `explain_workflow` - Complete workflow explanation
- `analyze_workflow_purpose` - Business purpose analysis
- `trace_data_flow` - Data transformation tracking
- `map_dependencies` - Dependency graph generation
- `analyze_risks` - Risk assessment

---

## [1.14.0] - 2025-11-28

### 🎯 Added - Workflow Deletion
- Safe workflow deletion with confirmation
- Archive option for soft deletion
- State cleanup on deletion

**New Tools:**
- `delete_workflow` - Delete workflows safely

---

## [1.13.2] - 2025-11-20

### 🐛 Fixed - Workflow Update
- Intelligent node merging prevents accidental data loss
- Preserves existing node configurations during updates
- Better handling of credential assignments

---

## [1.13.0] - 2025-11-15

### 🎯 Added - Intent Metadata System

**AI Context Continuity:**
- "Why" documentation for each node
- 5 intent fields: reason, assumption, risk, alternative, dependency
- Coverage analysis and tracking
- AI-generated intent suggestions

**New Tools:**
- `add_intent_metadata` - Add intent to nodes
- `get_intent_coverage` - Check documentation coverage
- `suggest_intent_metadata` - AI-powered intent suggestions
- `explain_workflow_intent` - Overall workflow reasoning

---

## [1.12.0] - 2025-11-10

### 🎯 Added - Execution Monitoring

**Real-Time Feedback:**
- Execution monitoring with error analysis
- Error simplification for AI agents
- Context extraction (node, input, output)
- Pattern analysis across executions
- Success rate tracking

**New Tools:**
- `monitor_execution` - Watch executions in real-time
- `analyze_execution_errors` - Error analysis
- `get_workflow_improvement_suggestions` - Fix recommendations

---

## [1.11.0] - 2025-11-05

### 🎯 Added - Semantic Analysis

**Deep Logic Validation:**
- 12 anti-pattern checks
- LLM-friendly fix suggestions
- Security scanning
- Performance analysis

**Anti-Pattern Detection:**
- HTTP retry patterns
- Loop completion
- Timezone configuration
- IF node paths
- Webhook security
- Infinite loops
- Credential usage
- N+1 queries
- Rate limiting
- Data validation

**New Tools:**
- `analyze_semantic_issues` - Deep workflow analysis
- `get_fix_suggestions` - Copy-paste ready fixes

---

## [1.10.0] - 2025-10-28

### 🎯 Added - Template Library

**Pre-Built Templates:**
- 10+ workflow templates
- AI-powered recommendations
- Smart relevance scoring (70-90% accuracy)
- Category browsing
- Difficulty levels
- Full-text search

**New Tools:**
- `get_workflow_templates` - Browse templates
- `get_template_recommendations` - AI suggestions
- `search_templates` - Full-text search
- `get_template_by_id` - Template details

---

## [1.9.0] - 2025-10-20

### 🎯 Added - AI Feedback System

**Intelligent Error Analysis:**
- Pattern recognition (auth, network, data, SQL, rate limiting)
- AI-friendly structured feedback
- Fix examples (wrong vs correct)
- Node-specific recommendations
- Learning loop for AI agents

**New Tools:**
- `analyze_execution_errors` - Error analysis
- `get_workflow_improvement_suggestions` - Fix suggestions

---

## [1.8.0] - 2025-10-15

### 🎯 Added - Workflow Validation

**Pre-Deployment Checks:**
- Schema validation
- Semantic validation
- Parameter validation
- Security checks
- Best practices

**New Tools:**
- `validate_workflow` - Comprehensive validation
- `validate_workflow_schema` - Structure checks
- `validate_workflow_parameters` - Parameter checks

---

## [1.7.0] - 2025-10-10

### 🎯 Added - Session State Management

**Context Tracking:**
- Active workflow tracking
- Session history
- Recent workflows
- Persistent state
- Smart context references

---

## [1.6.0] - 2025-10-05

### 🎯 Added - Workflow Execution

**Execution Features:**
- Manual workflow triggering
- Custom input data
- Execution details
- Execution history

**New Tools:**
- `execute_workflow` - Run workflows
- `get_execution_details` - Detailed execution data

---

## [1.5.0] - 2025-09-28

### 🎯 Added - Workflow Management

**CRUD Operations:**
- Create workflows
- Update workflows (smart merge)
- Delete workflows
- List workflows
- Filter workflows

---

## [1.4.0] - 2025-09-20

### 🎯 Added - Workflow Analysis

**Analysis Features:**
- Complexity analysis
- Issue detection
- Optimization suggestions
- Security scanning

**New Tools:**
- `analyze_workflow` - Comprehensive analysis

---

## [1.3.0] - 2025-09-15

### 🎯 Added - Node Knowledge Base

**Node Documentation:**
- 20+ node types documented
- Use cases and examples
- Configuration tips
- Best practices

---

## [1.2.0] - 2025-09-10

### 🎯 Added - Workflow Templates

**Template Generation:**
- Natural language to workflow
- Template types (API, Reporting, Integration, etc.)
- Node structure recommendations

**New Tools:**
- `generate_workflow_template` - Template generation

---

## [1.1.0] - 2025-09-05

### 🎯 Added - Smart Suggestions

**AI-Powered Suggestions:**
- Node recommendations
- Workflow outlines
- Best practices

**New Tools:**
- `suggest_workflow_nodes` - Node suggestions
- `generate_workflow_outline` - Workflow planning

---

## [1.0.0] - 2025-09-01

### 🎯 Initial Release

**Core Features:**
- MCP server setup
- n8n API client
- Basic workflow operations
- Node knowledge base

**Tools:**
- `list_workflows` - List all workflows
- `get_workflow` - Get workflow details
- `search_node_knowledge` - Search node docs

---

## Legend

- 🎯 **Added** - New features
- 🔧 **Changed** - Changes in existing functionality
- 🐛 **Fixed** - Bug fixes
- 🗑️ **Removed** - Removed features
- 🔒 **Security** - Security improvements
- 📚 **Documentation** - Documentation updates

---

[1.18.0]: https://github.com/yourusername/n8n-workflow-builder/releases/tag/v1.18.0
[1.17.1]: https://github.com/yourusername/n8n-workflow-builder/releases/tag/v1.17.1
[1.17.0]: https://github.com/yourusername/n8n-workflow-builder/releases/tag/v1.17.0
[1.16.0]: https://github.com/yourusername/n8n-workflow-builder/releases/tag/v1.16.0
[1.15.0]: https://github.com/yourusername/n8n-workflow-builder/releases/tag/v1.15.0
[1.14.0]: https://github.com/yourusername/n8n-workflow-builder/releases/tag/v1.14.0
[1.13.2]: https://github.com/yourusername/n8n-workflow-builder/releases/tag/v1.13.2
[1.13.0]: https://github.com/yourusername/n8n-workflow-builder/releases/tag/v1.13.0
[1.12.0]: https://github.com/yourusername/n8n-workflow-builder/releases/tag/v1.12.0
[1.11.0]: https://github.com/yourusername/n8n-workflow-builder/releases/tag/v1.11.0
[1.10.0]: https://github.com/yourusername/n8n-workflow-builder/releases/tag/v1.10.0
