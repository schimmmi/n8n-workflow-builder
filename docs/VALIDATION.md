# Workflow Validation System

The n8n Workflow Builder includes a comprehensive **pre-deployment validation system** that checks workflows for errors, security issues, and best practice violations before they go live.

## 🎯 Why Validate?

Deploying broken workflows causes:
- ❌ Runtime errors in production
- 🔒 Security vulnerabilities
- 🐛 Hard-to-debug issues
- ⏱️ Wasted time troubleshooting

**Solution:** Validate before deployment!

## 🔍 Validation Layers

The validation system performs **3 types of checks**:

### 1. Schema Validation
Ensures the workflow structure is correct according to n8n's requirements.

**Checks:**
- ✅ Required workflow fields present (`name`, `nodes`, `connections`)
- ✅ Workflow name is not empty
- ✅ All nodes have required fields (`name`, `type`, `position`, `parameters`)
- ✅ Node positions are valid `[x, y]` arrays
- ✅ Connections object is properly structured

**Example Error:**
```
Node 'HTTP Request': Missing required field 'parameters'
```

### 2. Semantic Validation
Validates logical rules and workflow semantics.

**Checks:**
- ✅ At least one trigger node exists (Webhook/Schedule/Manual)
- ✅ No duplicate node names
- ✅ No orphaned nodes (disconnected from workflow)
- ✅ Nodes are properly connected
- ✅ No hardcoded sensitive data (passwords, API keys)
- ✅ Workflow complexity is reasonable (<30 nodes recommended)
- ✅ Error handling present for complex workflows

**Example Error:**
```
Workflow must have at least one trigger node (Webhook, Schedule, or Manual)
Duplicate node names found: HTTP Request, Set
```

### 3. Parameter Validation
Node-specific parameter checks for common node types.

**Checks per Node Type:**

#### Webhook Node
- ✅ Has `path` parameter
- ⚠️ Authentication enabled (security)

#### HTTP Request Node
- ✅ Has `url` parameter
- ⚠️ Timeout configured (prevents hanging)

#### Schedule Trigger Node
- ✅ Has schedule rule or cron expression

#### IF Node
- ⚠️ Has conditions defined

#### Postgres Node
- ⚠️ Not using `SELECT *` (bad practice)
- ⚠️ Uses parameterized queries (SQL injection prevention)

#### Set Node
- ⚠️ Has values configured

#### Code Node
- ✅ Has code defined
- ⚠️ Returns items array

**Example Warnings:**
```
Webhook node 'API Endpoint': No authentication enabled (security risk)
Postgres node 'Query': Using SELECT * (bad practice)
Code node 'Transform': Should return items array
```

## 🛠️ Usage

### Validate Existing Workflow

```
You: "Validate workflow abc-123"

Claude uses: validate_workflow
```

**Output:**
```markdown
# Workflow Validation: Production API

## ✅ Validation Passed
Status: Ready for deployment
Total Warnings: 2

### Validation Summary:
- Schema errors: 0
- Semantic errors: 0
- Parameter errors: 0

## ⚠️ Warnings (should fix):
1. Nodes with default names (should be renamed): HTTP Request, Set
2. Webhook node 'API Endpoint': No authentication enabled (security risk)
```

### Validate Before Creating

```
You: "Validate this workflow JSON before I create it"

Claude uses: validate_workflow_json
workflow: { ... }
```

**Use Case:** Validate a workflow you built programmatically before pushing to n8n.

## 📋 Validation Categories

### 🔴 Errors (MUST FIX)
Errors block deployment. The workflow will not work correctly.

**Common Errors:**
- Missing required fields
- Empty node names or types
- No trigger nodes
- Duplicate node names
- Invalid structure
- Missing required parameters (URL, path, code, etc.)

### ⚠️ Warnings (SHOULD FIX)
Warnings don't block deployment but indicate issues.

**Common Warnings:**
- Default node names (not renamed)
- No authentication on webhooks
- Missing timeouts on HTTP requests
- Hardcoded credentials
- Using `SELECT *` in SQL
- Missing error handling
- Orphaned nodes
- High complexity (>30 nodes)

## 📊 Validation Report Structure

```json
{
  "valid": true,
  "errors": [
    "Webhook node 'API': Missing 'path' parameter",
    "Duplicate node names found: Set"
  ],
  "warnings": [
    "Nodes with default names: HTTP Request",
    "Workflow lacks error handling"
  ],
  "summary": {
    "total_errors": 2,
    "total_warnings": 2,
    "schema_errors": 1,
    "semantic_errors": 1,
    "parameter_errors": 0
  }
}
```

## 🎯 Validation Rules Reference

### Schema Rules

| Rule | Type | Description |
|------|------|-------------|
| Required workflow fields | Error | `name`, `nodes`, `connections` must exist |
| Non-empty name | Error | Workflow name cannot be empty |
| Long name | Warning | Name > 200 chars |
| Nodes is array | Error | `nodes` must be an array |
| No nodes | Error | Workflow must have at least 1 node |
| Required node fields | Error | Each node needs `name`, `type`, `position`, `parameters` |
| Valid position | Error | Position must be `[x, y]` array |
| Connections is object | Error | `connections` must be a dictionary |

### Semantic Rules

| Rule | Type | Description |
|------|------|-------------|
| Has trigger node | Error | At least one Webhook/Schedule/Manual trigger |
| Unique names | Error | No duplicate node names |
| Connected nodes | Warning | No orphaned nodes (except triggers) |
| Default names | Warning | Nodes should be renamed from defaults |
| Missing credentials | Warning | Nodes requiring credentials should have them |
| Hardcoded secrets | Warning | No passwords/keys in parameters |
| High complexity | Warning | >30 nodes is complex |
| Missing error handling | Warning | >5 nodes should have Error Trigger |

### Parameter Rules (Node-Specific)

| Node Type | Parameter | Type | Rule |
|-----------|-----------|------|------|
| Webhook | `path` | Error | Must be present |
| Webhook | `authentication` | Warning | Should not be 'none' |
| HTTP Request | `url` | Error | Must be present |
| HTTP Request | `timeout` | Warning | Should be set |
| Schedule Trigger | `rule` or `cronExpression` | Error | One must be present |
| IF | `conditions` | Warning | Should have conditions |
| Postgres | Query | Warning | Avoid `SELECT *` |
| Postgres | Query | Warning | Use parameterized values |
| Set | `values` | Warning | Should have values |
| Code | `jsCode` | Error | Must have code |
| Code | Return statement | Warning | Should return items array |

## 🔒 Security Checks

The validator performs automatic security checks:

### 1. Hardcoded Credentials Detection
Scans node parameters for keywords:
- `password`
- `apikey` / `api_key`
- `secret`
- `token`

**Warning if found outside expressions (`{{...}}`):**
```
Node 'API Call' may contain hardcoded sensitive data
```

**✅ Correct:**
```json
{
  "parameters": {
    "headerParameters": {
      "parameters": [
        {
          "name": "Authorization",
          "value": "={{$credentials.apiKey}}"
        }
      ]
    }
  }
}
```

**❌ Wrong:**
```json
{
  "parameters": {
    "authentication": "none",
    "apiKey": "sk-abc123xyz..."
  }
}
```

### 2. Missing Authentication
Warns when Webhook nodes have no authentication:
```
Webhook node 'Public API': No authentication enabled (security risk)
```

### 3. SQL Injection Prevention
Warns about non-parameterized database queries:
```
Postgres node 'Update User': Query should use parameterized values
```

## 💡 Best Practices

### Always Validate Before:
1. ✅ Deploying to production
2. ✅ Activating a workflow
3. ✅ Making major changes
4. ✅ Creating from templates

### Use Validation to:
1. 🐛 Catch errors early (dev, not production)
2. 🔒 Prevent security issues
3. 📈 Maintain code quality
4. 🎓 Learn best practices

### Integration Workflow:
```
1. Build workflow in n8n UI
2. Save (but don't activate)
3. Validate via Claude: "Validate workflow abc-123"
4. Fix all errors
5. Address warnings
6. Activate workflow ✅
```

## 🚀 Pro Tips

### 1. Fix Errors First, Then Warnings
```
Errors = Broken functionality
Warnings = Suboptimal but working
```

### 2. Rename Default Names
Before:
```
- HTTP Request
- Set
- IF
```

After:
```
- Fetch User Data
- Format Response
- Check User Status
```

### 3. Add Error Handling
For workflows >5 nodes, add:
- Error Trigger node
- Notification on errors (Slack/Email)
- Logging

### 4. Use Credentials, Not Hardcoded Values
```
❌ "apiKey": "sk-123..."
✅ "apiKey": "={{$credentials.myApi}}"
```

### 5. Set Timeouts
Always set timeouts on:
- HTTP Request nodes
- Database queries
- External API calls

**Default:** 30 seconds (often too long!)

### 6. Validate Templates
Even if using a template, validate it:
```
You: "Generate workflow for daily reports"
You: "Validate the workflow JSON before creating"
```

## 🎯 Validation Examples

### Example 1: Perfect Workflow ✅
```markdown
# Workflow Validation: Production Data Sync

## ✅ Validation Passed
Status: Ready for deployment
Total Warnings: 0

🎉 Perfect! No errors or warnings found.
```

### Example 2: Needs Fixes ❌
```markdown
# Workflow Validation: API Endpoint

## ❌ Validation Failed
Status: Cannot deploy - fix errors first
Total Errors: 3
Total Warnings: 2

### Validation Summary:
- Schema errors: 1
- Semantic errors: 1
- Parameter errors: 1

## 🔴 Errors (must fix):
1. Node 'HTTP Request': Missing 'url' parameter
2. Duplicate node names found: Set, Set
3. Webhook node 'API': Missing 'path' parameter

## ⚠️ Warnings (should fix):
1. Nodes with default names (should be renamed): HTTP Request, Set
2. Webhook node 'API': No authentication enabled (security risk)
```

## 🔧 Extending the Validator

The validator is extensible. To add custom rules:

### Add Node Type Validation
Edit `WorkflowValidator.validate_node_parameters()`:

```python
# Slack node validation
elif node_type == 'n8n-nodes-base.slack':
    if not params.get('channel'):
        errors.append(f"Slack node '{node_name}': Missing 'channel' parameter")
```

### Add Custom Semantic Rules
Edit `WorkflowValidator.validate_workflow_semantics()`:

```python
# Check for minimum number of nodes
if len(nodes) < 3:
    warnings.append("Workflow is very simple (<3 nodes)")
```

### Add Security Rules
```python
# Check for test/dummy credentials
for node in nodes:
    creds = node.get('credentials', {})
    if 'test' in str(creds).lower():
        warnings.append(f"Node '{node['name']}' uses test credentials")
```

## 📚 Summary

The validation system provides:
- ✅ **3-layer validation**: Schema, Semantics, Parameters
- 🔒 **Security checks**: Credentials, authentication, SQL injection
- 📋 **Comprehensive rules**: 20+ validation rules
- 🎯 **Pre-deployment safety**: Catch issues before production
- 📈 **Quality enforcement**: Learn and enforce best practices

**Remember:** A validated workflow is a reliable workflow! 🚀
