# 📖 n8n Workflow Builder - Examples & Use Cases

Concrete examples of how to use the MCP Server! 🎯

## 🎬 Scenario 1: Create API Endpoint

### What you want:
REST API endpoint that validates user data and saves it to Postgres

### How to do it:

**You ask Claude:**
```
"I need an n8n workflow for an API endpoint.
The endpoint should:
- Receive POST requests
- Validate user data (name, email, age)
- Save to Postgres
- Return success/error response"
```

**Claude uses:** `suggest_workflow_nodes` + `generate_workflow_template`

**You get:**
```markdown
# Workflow: User Registration API

## Suggested Structure:

1. **Webhook**
   - Receives POST requests
   - Path: /api/users/register
   - Authentication: Header Auth recommended

2. **IF Node**
   - Validation: email present?
   - Validation: age > 18?
   - True → continue, False → Error Response

3. **Set Node**
   - Format data for DB
   - Add timestamp
   - Sanitize inputs

4. **Postgres Node**
   - INSERT INTO users
   - Handle duplicates

5. **Respond to Webhook**
   - Success: 201 Created
   - Error: 400 Bad Request

## Best Practices:
- Enable Webhook Authentication!
- Input sanitization against SQL Injection
- Use prepared statements
- Return proper HTTP Status Codes
```

---

## 🎬 Scenario 2: Daily Report

### What you want:
Every day at 9 AM fetch sales metrics from DB and send via Slack

### How to do it:

**You ask Claude:**
```
"Create a workflow that runs daily at 9 AM and:
- Fetches sales data from Postgres (last 24h)
- Calculates metrics (total revenue, orders, avg order value)
- Formats as nice report
- Sends via Slack to #sales-team"
```

**Claude uses:** `generate_workflow_template` (Type: `scheduled_report`)

**You get:**
```markdown
# Workflow: Daily Sales Report

## Template: Daily Report Generator

1. Schedule Trigger (Daily at 9AM)
   - Cron: 0 9 * * *
   - Timezone: Europe/Berlin

2. Postgres (Fetch Data)
   - Query: SELECT * FROM orders
           WHERE created_at > NOW() - INTERVAL '24 hours'
   - Return data as JSON

3. Function (Calculate Metrics)
   ```javascript
   const orders = $input.all();
   const total_revenue = orders.reduce((sum, o) => sum + o.amount, 0);
   const order_count = orders.length;
   const avg_value = total_revenue / order_count;

   return [{
     json: {
       revenue: total_revenue,
       orders: order_count,
       avg_order: avg_value
     }
   }];
   ```

4. Set (Format Report)
   - message: "📊 Daily Sales Report\n💰 Revenue: {{$json.revenue}}€\n..."

5. Slack (Send to Slack)
   - Channel: #sales-team
   - Message: {{$json.message}}

## Best Practices:
✅ Add error handling!
✅ Notify admin on errors
✅ Mind the timezone!
```

---

## 🎬 Scenario 3: Debug Workflow

### What you have:
Workflow throws error "Error: getaddrinfo ENOTFOUND api.example.com"

### How to solve it:

**You ask Claude:**
```
"My workflow throws this error:
'Error: getaddrinfo ENOTFOUND api.example.com'

The HTTP Request Node cannot reach the API."
```

**Claude uses:** `debug_workflow_error`

**You get:**
```markdown
# Workflow Error Debug

## Probable Cause: DNS/Network Error

The error "getaddrinfo ENOTFOUND" means the hostname
cannot be resolved.

**Possible Causes:**

1. **URL Typo**
   - Check: Is "api.example.com" spelled correctly?
   - Common mistake: https://api.example.com vs http://

2. **Network/Firewall**
   - Can n8n access external APIs?
   - Proxy config needed?
   - Firewall rule blocking traffic?

3. **DNS Problem**
   - Is the domain name valid?
   - DNS server reachable?

**Solution Steps:**

1. Test in browser: Open https://api.example.com
2. Check URL in HTTP Request Node (typos?)
3. Test with curl: `curl https://api.example.com`
4. Check n8n network settings
5. For self-hosted: Check Docker networking

**Quick Fix:**
- Use IP address instead of hostname (temporary)
- Check n8n logs: Settings > Log Streaming
```

---

## 🎬 Scenario 4: Optimize Workflow

### What you have:
Existing workflow that is slow and has many nodes

### How to improve it:

**You ask Claude:**
```
"Analyze my workflow 'Customer Onboarding' (ID: abc-123)
and give me optimization suggestions"
```

**Claude uses:** `analyze_workflow`

**You get:**
```markdown
# Workflow Analysis: Customer Onboarding

**Complexity:** High
**Total Nodes:** 23

## ⚠️ Issues Found:

- Node 'HTTP Request 3' contains hardcoded API key
- Node 'Set 1' contains hardcoded password
- No error handling detected

## 💡 Suggestions:

- Consider splitting into sub-workflows (23 nodes is complex!)
- Rename default node names: HTTP Request, Set, IF
- Add Error Trigger node for better error handling
- Move credentials to n8n Credential Manager
- Consider batching HTTP requests

## 🚀 Optimization Plan:

1. **Security First:**
   - Move ALL credentials to Credential Manager
   - Never hardcode API keys/passwords

2. **Split Workflow:**
   - Main Flow: "Customer Onboarding - Main"
   - Sub-Workflow 1: "Send Welcome Email"
   - Sub-Workflow 2: "Setup User Account"
   - Sub-Workflow 3: "Notify Teams"

3. **Performance:**
   - Batch HTTP requests where possible
   - Use Redis for caching
   - Reduce sequential dependencies

4. **Maintainability:**
   - Rename all nodes meaningfully
   - Add notes/documentation
   - Use consistent naming scheme
```

---

## 🎬 Scenario 5: Learn Node

### What you want:
Understand how to properly use the Redis Node

### How to do it:

**You ask Claude:**
```
"Explain the Redis node with use cases and best practices"
```

**Claude uses:** `explain_node`

**You get:**
```markdown
# Redis Node

**Description:** Redis key-value store integration for caching,
session storage and rate limiting

## Use Cases:

- **Caching**: Cache API responses for better performance
- **Rate Limiting**: Limit user requests
- **Session Storage**: Store user sessions
- **Temporary Data**: Store data with TTL
- **Pub/Sub**: Message queue for event-based workflows

## Best Practices:

✅ **Always set TTL**
   - Prevents memory overflow
   - Automatic cleanup
   ```javascript
   key: "user:123"
   value: {...}
   ttl: 3600  // 1 hour
   ```

✅ **Use appropriate data types**
   - String: Simple values
   - Hash: Object data
   - Set: Unique lists
   - Sorted Set: Ranked data

✅ **Error Handling**
   - Redis connection can fail
   - Implement fallback logic
   - Log Redis errors

✅ **Key Naming Convention**
   - Use prefixes: "user:123", "cache:api:endpoint"
   - Hierarchical: "app:feature:entity:id"
   - Stay consistent!

## Example: API Response Caching

```javascript
// Check cache first
GET key: "cache:api:users:{{$json.userId}}"

// If miss → fetch from API → cache result
SET key: "cache:api:users:{{$json.userId}}"
    value: {{$json}}
    ttl: 600  // 10 minutes
```

## Common Pitfalls:

❌ No TTL → Memory full
❌ Too long TTLs → Stale data
❌ No connection error handling
❌ Keys without structure → Chaos
```

---

## 🎯 Power Combos

### Combo 1: Create + Analyze workflow
```
1. "Generate workflow for XYZ"
2. → Build workflow in n8n
3. "Analyze workflow ABC"
4. → Implement optimizations
```

### Combo 2: Learn node + Generate template
```
1. "Explain Postgres node"
2. → Learn best practices
3. "Generate template with Postgres + Slack"
4. → Get optimal workflow
```

### Combo 3: Error → Debug → Fix
```
1. Workflow fails
2. "Debug error: [Error Message]"
3. → Get solution
4. → Implement fix
5. "Analyze workflow again"
6. → Confirm fix works
```

---

## 💡 Pro Tips from Practice

### Tip 1: Iterative Design
```
Start: "Suggest nodes for: Daily Report"
→ Get outline
→ Refine details: "Explain Postgres Node"
→ Generate template: "Create complete workflow"
→ After building analyze: "Analyze workflow"
```

### Tip 2: Template as Base
```
Use templates as starting point:
"Generate scheduled_report template for Sales Metrics"
→ Adapt to your needs
→ Extend with custom logic
```

### Tip 3: Security Check before Production
```
Before deployment ALWAYS:
"Analyze workflow XYZ for security issues"
→ Fix hardcoded credentials
→ Add authentication
→ Check input validation
```

---

**Happy Building! 🚀**

More questions? Just ask Claude! 😉
