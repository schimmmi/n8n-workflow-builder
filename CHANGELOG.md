# Changelog

All notable changes to the n8n Workflow Builder MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
