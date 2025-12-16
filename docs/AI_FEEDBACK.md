# AI Feedback & Error Analysis System

The n8n Workflow Builder includes an intelligent **AI Feedback System** that analyzes workflow execution failures and provides structured, actionable feedback specifically designed for AI agents and developers.

## 🎯 Problem Statement

When workflows fail, AI agents generating workflows often face:
- ❌ **Blind JSON Generation** - No feedback loop from execution errors
- 🤷 **Unknown Root Causes** - Generic error messages without context
- 🔁 **Repeated Mistakes** - Same errors happen again because AI doesn't learn
- 📝 **Manual Debugging** - Humans have to manually analyze and fix issues

## 💡 Solution: AI Feedback Loop

The AI Feedback System creates a **learning loop**:

```
AI generates workflow → Execute → Fails → Analyze errors →
Generate structured feedback → AI learns → Generate better workflow
```

## 🔍 How It Works

### 1. Error Analysis
Analyzes execution failures and extracts:
- Error messages from failed nodes
- Node types and configurations
- Root cause identification
- Error patterns (auth, network, data, SQL, rate limiting, etc.)

### 2. Root Cause Detection
Identifies common failure patterns:
- 🔒 **Authentication/Authorization** (401, 403, unauthorized)
- 🌐 **Network/Connection** (timeout, ECONNREFUSED, unreachable)
- 📊 **Data/Type** (undefined, null, invalid JSON)
- 💾 **Database/SQL** (syntax error, query failed)
- ⏱️ **Rate Limiting** (429, too many requests)
- ⚙️ **Missing/Invalid Parameters**

### 3. AI-Friendly Guidance
Generates structured feedback with:
- **Root Cause**: What went wrong
- **Suggestions**: How to fix it
- **AI Guidance**: How to generate better workflows next time
- **Fix Examples**: Wrong vs. Correct code examples

### 4. Improvement Recommendations
Suggests specific workflow improvements:
- **Nodes to Modify**: Which nodes need changes and why
- **Nodes to Add**: Missing features (error handlers, delays, etc.)
- **Parameter Changes**: Specific field updates

## 🛠️ Available Tools

### `analyze_execution_errors`
Analyzes a failed execution and provides comprehensive error feedback.

**Use Case:**
```
You: "Analyze execution 12345 - it failed"

Claude uses: analyze_execution_errors
→ Comprehensive error analysis with root cause and fixes
```

**Output Example:**
```markdown
# 🔍 Execution Error Analysis: API Data Sync

❌ Status: Execution failed
🎯 Root Cause: Authentication/Authorization Error

## 🔴 Errors Detected:

**1. Node: `Fetch User Data`**
   - Type: HTTPError
   - Message: 401 Unauthorized

## 📍 Affected Nodes: Fetch User Data

## 💡 Suggested Fixes:

1. Check if credentials are correctly configured
2. Verify API key/token is valid and not expired
3. Ensure correct authentication method is used

## 🤖 AI Guidance (for workflow generation):

The workflow failed due to authentication issues. When generating workflows, ensure:
1. Use credential references: {{$credentials.credentialName}} instead of hardcoded values
2. Specify correct authentication type (Bearer, Basic, OAuth, etc.)
3. Include proper headers (Authorization, API-Key, etc.)
4. Test credentials before deploying workflow

## 📝 Fix Examples:

### Use credentials instead of hardcoded API key

**❌ Wrong:**
```json
{
  "parameters": {
    "headerParameters": {
      "parameters": [
        {"name": "Authorization", "value": "Bearer sk-abc123"}
      ]
    }
  }
}
```

**✅ Correct:**
```json
{
  "parameters": {
    "authentication": "predefinedCredentialType",
    "nodeCredentialType": "apiKey"
  }
}
```
```

### `get_workflow_improvement_suggestions`
Generates specific improvement recommendations for a failed workflow.

**Use Case:**
```
You: "Get improvement suggestions for execution 12345 of workflow abc-456"

Claude uses: get_workflow_improvement_suggestions
→ Detailed node-by-node fix recommendations
```

**Output Example:**
```markdown
# 💡 Workflow Improvement Suggestions: API Data Sync

**Root Cause:** Network/Connection Error

## 🔴 Original Issues:

1. **HTTP Request Node**: Error: ETIMEDOUT - Connection timeout

## 🔧 Nodes to Modify:

### `Fetch User Data` (n8n-nodes-base.httpRequest)

**timeout:**
- Current: `Not set`
- Suggested: `30000`
- Reason: Prevent indefinite hanging

**retry:**
- Current: `Not set`
- Suggested: `{"maxRetries": 3}`
- Reason: Handle flaky connections

## ➕ Nodes to Add:

### `Error Handler` (n8n-nodes-base.errorTrigger)
- Reason: Catch and handle workflow errors gracefully

## 📋 Recommended Changes:

1. Check if the external service is reachable
2. Increase timeout settings
3. Add retry logic for flaky connections
```

## 📊 Error Pattern Recognition

### Authentication Errors
**Keywords:** `401`, `403`, `unauthorized`, `forbidden`, `authentication`

**AI Guidance:**
- Use credential references instead of hardcoded values
- Specify correct authentication type
- Include proper headers
- Test credentials before deployment

**Fix Example:**
```javascript
// ❌ Wrong
"authentication": "none",
"apiKey": "sk-abc123"

// ✅ Correct
"authentication": "predefinedCredentialType",
"nodeCredentialType": "apiKey"
```

### Network Errors
**Keywords:** `timeout`, `ECONNREFUSED`, `network`, `connection`, `unreachable`

**AI Guidance:**
- Set reasonable timeouts (30000ms)
- Add retry logic
- Validate URLs
- Use error handling nodes

**Fix Example:**
```json
{
  "url": "https://api.example.com",
  "timeout": 30000,
  "retry": {"maxRetries": 3}
}
```

### Data/Type Errors
**Keywords:** `undefined`, `null`, `cannot read property`, `type error`, `invalid json`

**AI Guidance:**
- Validate data exists: `{{$json.field ?? 'default'}}`
- Use IF nodes to check data
- Add default values
- Use Set nodes to normalize structure

**Fix Example:**
```javascript
// ❌ Wrong
{{$json.user.email}}

// ✅ Correct
{{$json.user?.email ?? 'no-email@example.com'}}
```

### Database Errors
**Keywords:** `sql`, `database`, `query`, `syntax error`, `relation`

**AI Guidance:**
- Use parameterized queries
- Validate table/column names
- Avoid SELECT *
- Use proper escaping

**Fix Example:**
```sql
-- ❌ Wrong
SELECT * FROM users WHERE id = '{{$json.id}}'

-- ✅ Correct
SELECT id, name, email FROM users WHERE id = $1
-- values: ={{[$json.id]}}
```

### Rate Limiting
**Keywords:** `429`, `rate limit`, `too many requests`

**AI Guidance:**
- Add Wait nodes (1000-2000ms delay)
- Implement exponential backoff
- Use batching
- Cache responses

**Fix Example:**
```json
{
  "type": "n8n-nodes-base.wait",
  "name": "Rate Limit Delay",
  "parameters": {"amount": 1000}
}
```

## 🎯 Feedback Structure

The feedback system returns structured data perfect for AI processing:

```json
{
  "has_errors": true,
  "errors": [
    {
      "node": "HTTP Request",
      "message": "401 Unauthorized",
      "type": "HTTPError",
      "stack": "..."
    }
  ],
  "root_cause": "Authentication/Authorization Error",
  "suggestions": [
    "Check if credentials are correctly configured",
    "Verify API key/token is valid"
  ],
  "affected_nodes": ["HTTP Request"],
  "ai_guidance": "When generating workflows, ensure...",
  "fix_examples": [
    {
      "description": "Use credentials",
      "wrong": {...},
      "correct": {...}
    }
  ]
}
```

## 🚀 Integration with AI Workflow Generation

### Before AI Feedback (Blind Generation)
```
User: "Create workflow for fetching user data"
AI: Generates workflow with hardcoded API key
→ Deploys
→ Fails with 401 error
→ User manually fixes
→ AI doesn't learn
```

### After AI Feedback (Learning Loop)
```
User: "Create workflow for fetching user data"
AI: Generates workflow
→ Deploys
→ Fails with 401 error
→ analyze_execution_errors identifies auth issue
→ AI receives structured feedback
→ AI regenerates with proper credentials
→ Works! ✅
→ AI learns for future workflows
```

## 💡 Best Practices

### 1. Always Analyze Failed Executions
```
User: "My workflow failed"
→ First: analyze_execution_errors
→ Then: Fix based on feedback
```

### 2. Get Improvement Suggestions
```
User: "How do I fix my workflow?"
→ Use: get_workflow_improvement_suggestions
→ Get node-specific fixes
```

### 3. Learn from Feedback
```
AI generates workflow
→ If fails: Analyze
→ Apply suggestions
→ Regenerate workflow
→ Validate before deploy
```

### 4. Use with Validation
```
1. Generate workflow
2. Validate (validate_workflow_json)
3. Fix validation errors
4. Deploy
5. If execution fails: Analyze
6. Apply feedback
7. Re-validate
8. Deploy fixed version
```

## 🔄 Feedback Loop Example

```
# Iteration 1: Initial workflow
AI: Creates workflow with no timeout
→ Executes
→ Hangs indefinitely ❌

# Iteration 2: After feedback
analyze_execution_errors
→ Root Cause: "Network timeout"
→ Suggestion: "Set timeout to 30000ms"
→ AI adds timeout
→ Executes
→ Fails with 401 ❌

# Iteration 3: After more feedback
analyze_execution_errors
→ Root Cause: "Authentication Error"
→ Suggestion: "Use credentials, not hardcoded"
→ AI uses credential reference
→ Executes
→ Success! ✅
```

## 📚 Use Cases

### 1. AI Workflow Generation
```python
# AI generates workflow
workflow = ai_generate_workflow(prompt)

# Validate before deploy
validation = validate_workflow_json(workflow)
if not validation['valid']:
    # Fix validation errors first
    workflow = ai_fix_validation_errors(validation, workflow)

# Deploy and execute
execution = execute_workflow(workflow)

# If failed, analyze and improve
if execution['failed']:
    feedback = analyze_execution_errors(execution['id'])
    improved_workflow = ai_apply_feedback(feedback, workflow)

    # Validate improvements
    validation = validate_workflow_json(improved_workflow)

    # Deploy improved version
    execute_workflow(improved_workflow)
```

### 2. Debugging Assistance
```
User: "My workflow is failing with weird errors"
→ analyze_execution_errors
→ Shows root cause + suggestions
→ User fixes based on clear guidance
```

### 3. Learning from Production Failures
```
Workflow fails in production
→ analyze_execution_errors
→ Log feedback for future reference
→ Update workflow generation rules
→ Prevent same errors in future workflows
```

### 4. Automated Workflow Healing
```
Monitor executions
→ Detect failures
→ Auto-analyze with AI Feedback
→ Generate fixes
→ Validate fixes
→ Apply if safe
→ Self-healing workflows! 🤖
```

## 🔧 Extending Error Patterns

Add custom error patterns by extending `AIFeedbackAnalyzer._analyze_error_patterns()`:

```python
# Add custom error pattern
if 'your_custom_error' in all_errors:
    feedback["root_cause"] = "Custom Error Type"
    feedback["suggestions"] = [
        "Custom fix suggestion 1",
        "Custom fix suggestion 2"
    ]
    feedback["ai_guidance"] = (
        "When generating workflows for this scenario:\n"
        "1. Do X\n"
        "2. Do Y\n"
    )
    feedback["fix_examples"] = [
        {
            "description": "How to fix",
            "wrong": {...},
            "correct": {...}
        }
    ]
```

## 📊 Analytics & Insights

Track common failure patterns:
```python
# Analyze last 100 executions
executions = get_executions(limit=100)
failure_patterns = {}

for execution in executions:
    if execution['failed']:
        feedback = analyze_execution_errors(execution['id'])
        root_cause = feedback['root_cause']
        failure_patterns[root_cause] = failure_patterns.get(root_cause, 0) + 1

# Output: Most common failure types
# 1. Authentication: 45%
# 2. Network: 30%
# 3. Data/Type: 15%
# 4. Rate Limiting: 10%
```

## 🎓 Summary

The AI Feedback System provides:
- ✅ **Intelligent Error Analysis** - Pattern recognition & root cause detection
- ✅ **AI-Friendly Feedback** - Structured data perfect for AI processing
- ✅ **Actionable Suggestions** - Specific fixes, not generic advice
- ✅ **Code Examples** - Wrong vs. Correct comparisons
- ✅ **Learning Loop** - AI improves with each failure
- ✅ **Workflow Improvements** - Node-specific recommendations
- ✅ **Prevents Repeated Errors** - Learn from mistakes

**Transform failures into learning opportunities!** 🚀🤖
