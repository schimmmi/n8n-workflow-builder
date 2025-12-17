# 💬 Prompt Examples

This guide shows you how to effectively communicate with Claude using the n8n Workflow Builder MCP tools.

## 📋 Table of Contents

1. [Basic Operations](#-basic-operations)
2. [Workflow Creation](#-workflow-creation)
3. [Workflow Analysis](#-workflow-analysis)
4. [Debugging & Troubleshooting](#-debugging--troubleshooting)
5. [Templates & Discovery](#-templates--discovery)
6. [Advanced Operations](#-advanced-operations)
7. [Best Practices](#-best-practices)

---

## 🔧 Basic Operations

### List Workflows
```
"Show me all my workflows"
"List all active workflows"
"What workflows do I have?"
```

### Get Workflow Details
```
"Show me the details of workflow abc123"
"Get the structure of my 'Daily Report' workflow"
"What does workflow xyz789 look like?"
```

### Create Simple Workflow
```
"Create a new workflow called 'Test API'"
"Make a workflow named 'Customer Sync'"
```

### Update Workflow
```
"Update workflow abc123 - change the name to 'Production API'"
"In workflow xyz789, update the HTTP node URL to https://api.example.com"
"Add a Slack notification to the end of my 'Daily Report' workflow"
```

### Delete Workflow
```
"Delete workflow abc123"
"Remove the test workflow with ID xyz789"
"Delete all workflows that start with '[TEST]'"
```

---

## 🎨 Workflow Creation

### From Natural Language Description
```
"Create a workflow that:
- Triggers every day at 9 AM
- Fetches sales data from Postgres for the last 24 hours
- Calculates total revenue and order count
- Sends a formatted report to Slack channel #sales"
```

```
"Build an API endpoint that:
- Receives POST requests with user data
- Validates email format and required fields
- Saves valid data to Postgres
- Returns appropriate status codes (201 success, 400 error)"
```

```
"I need a workflow for monitoring:
- Check website uptime every 5 minutes
- If status code is not 200, send alert to Slack
- Track response time and log to database"
```

### From Template
```
"Show me templates for customer notifications"
"Recommend templates for building a reporting system"
"What templates do you have for API integrations?"
```

```
"Use the 'Email Campaign' template and customize it for:
- Product launch announcements
- Send to customer list in Postgres
- Track opens and clicks"
```

### Node Suggestions
```
"What nodes do I need for fetching data from Shopify and syncing to Google Sheets?"
"Suggest nodes for an authentication workflow with JWT tokens"
"I want to process images, what nodes should I use?"
```

---

## 🔍 Workflow Analysis

### General Analysis
```
"Analyze workflow abc123 for issues"
"Check my 'Production API' workflow for problems"
"Is there anything wrong with workflow xyz789?"
```

### Security Analysis
```
"Check workflow abc123 for security issues"
"Are there any hardcoded credentials in my workflows?"
"Analyze the 'Customer API' workflow for security vulnerabilities"
```

### Performance Analysis
```
"How can I optimize workflow abc123?"
"My workflow is slow, can you find bottlenecks?"
"Suggest performance improvements for the 'Data Sync' workflow"
```

### Semantic Analysis
```
"Run semantic analysis on workflow abc123"
"Check for anti-patterns in my 'API Handler' workflow"
"Analyze workflow xyz789 for best practice violations"
```

---

## 🐛 Debugging & Troubleshooting

### Execution Errors
```
"My workflow failed with error: 'Connection timeout'. What does this mean?"
"Debug the last execution of workflow abc123"
"Why is my 'Daily Report' workflow failing?"
```

```
"Show me the error details for execution xyz789"
"What went wrong in the last run of my API workflow?"
"Analyze execution errors for workflow abc123"
```

### Error Patterns
```
"My workflow has failed 5 times with authentication errors. What's the pattern?"
"Analyze error trends for the 'Customer Sync' workflow"
"Why does workflow abc123 keep timing out?"
```

### Specific Node Issues
```
"The HTTP Request node is returning 401. How do I fix this?"
"My Postgres node says 'connection refused'. Help!"
"The webhook isn't triggering my workflow. What's wrong?"
```

---

## 📚 Templates & Discovery

### Browse Templates
```
"Show me all available templates"
"What templates do you have for e-commerce?"
"List templates by difficulty level"
```

### Smart Recommendations
```
"I need to build a customer notification system. What template should I use?"
"Recommend templates for automated reporting"
"What's the best template for webhook-based integrations?"
```

### Template Details
```
"Show me details for the 'Email Campaign' template"
"How does the 'Scheduled Report' template work?"
"What nodes are in the 'API Endpoint' template?"
```

### Import Examples
```
"Import the simple API endpoint example"
"Create a workflow from example 02"
"Show me how to use the data validation example"
```

---

## 🚀 Advanced Operations

### Batch Operations
```
"List all workflows, then analyze each one for security issues"
"Find all workflows with 'test' in the name and delete them"
"Get execution history for all workflows from the last 24 hours"
```

### Workflow Comparison
```
"Compare workflow abc123 with xyz789"
"What's different between 'Production API' and 'Staging API' workflows?"
"Show me the changes between the current and previous version"
```

### Intent Management
```
"Add intent metadata to the HTTP node in workflow abc123:
reason: 'Fetch customer data from CRM'
risk: 'API rate limiting may occur'
alternative: 'Could use webhook push instead of polling'"
```

```
"Show me all intent metadata for workflow abc123"
"What's the coverage of intent documentation in my workflows?"
```

### Change Simulation
```
"Simulate changes to workflow abc123 if I update the HTTP endpoint"
"Show me the impact of adding a new node to my workflow"
"Preview changes before I deploy to production"
```

### Validation
```
"Validate workflow abc123 before deployment"
"Check if my workflow is ready for production"
"Run all validation checks on the 'Customer API' workflow"
```

---

## 💡 Best Practices

### ✅ Good Prompts

**Be Specific:**
```
✅ "Update the HTTP Request node in workflow abc123 to use POST instead of GET"
❌ "Change something in my workflow"
```

**Include Context:**
```
✅ "My workflow failed with error 'ECONNREFUSED'. It's trying to connect to localhost:5432"
❌ "My workflow doesn't work"
```

**State Your Goal:**
```
✅ "I need a workflow that syncs Shopify orders to Google Sheets every hour"
❌ "Make a Shopify thing"
```

**Reference Workflows Clearly:**
```
✅ "Analyze workflow abc123" or "Analyze my 'Daily Report' workflow"
❌ "Check that workflow"
```

---

### 🎯 Multi-Step Workflows

**Discovery → Creation → Testing:**
```
1. "Recommend templates for customer notifications"
2. "Use the Email Campaign template and customize it for my use case"
3. "Validate the workflow before deployment"
4. "Create a test execution with sample data"
```

**Problem → Analysis → Fix:**
```
1. "My workflow abc123 is failing with authentication errors"
2. "Analyze the last 10 executions for error patterns"
3. "Show me the HTTP Request node configuration"
4. "Update the authentication to use API key instead of basic auth"
5. "Test the workflow again"
```

**Monitoring → Optimization:**
```
1. "Show me execution history for workflow abc123"
2. "Analyze performance bottlenecks"
3. "Suggest optimizations"
4. "Implement the suggested changes"
5. "Compare execution times before and after"
```

---

### 🔄 Iterative Development

**Start Simple:**
```
1. "Create a basic webhook endpoint"
2. "Add validation for email and name fields"
3. "Add database storage"
4. "Add error handling"
5. "Add rate limiting"
6. "Validate the final workflow"
```

**Refine Gradually:**
```
1. "Generate a workflow for data processing"
2. "Now add error notifications to Slack"
3. "Add retry logic for failed API calls"
4. "Optimize the database queries"
5. "Add monitoring and logging"
```

---

### 🎓 Learning Patterns

**Understand Before Modifying:**
```
1. "Explain what workflow abc123 does"
2. "Show me the data flow through the nodes"
3. "What are the potential failure points?"
4. "Now help me add a new feature..."
```

**Learn from Examples:**
```
1. "Show me the data validation API example"
2. "Explain how the validation logic works"
3. "Create a similar workflow for product validation"
```

**Study Best Practices:**
```
1. "What are best practices for webhook authentication?"
2. "Show me examples of proper error handling"
3. "How should I structure a production API workflow?"
```

---

## 📝 Complex Example: End-to-End Workflow

Here's a complete conversation flow for building a production-ready workflow:

```
User: "I need to build a workflow that processes customer orders"

Claude: [Asks clarifying questions about requirements]

User: "It should:
- Trigger when new orders arrive via webhook
- Validate order data (amount, email, product ID)
- Check inventory in our database
- If in stock: process payment via Stripe and send confirmation email
- If out of stock: add to waitlist and notify warehouse
- Log all transactions to Postgres
- Send error alerts to Slack if anything fails"

Claude: "I'll create this workflow step by step..."

User: "Great! Now analyze it for issues"

Claude: [Runs comprehensive analysis]

User: "Fix the security issues you found"

Claude: [Implements fixes]

User: "Add intent metadata explaining why each node exists"

Claude: [Adds documentation]

User: "Validate everything before we deploy"

Claude: [Runs validation]

User: "Perfect! Now create test executions with sample data"

Claude: [Creates test scenarios]

User: "Deploy to production - update the webhook URL to the production endpoint"

Claude: [Makes final updates]
```

---

## 🔗 Related Resources

- **[Tools Documentation](../docs/TOOLS.md)** - Complete reference of all available tools
- **[Examples](README.md)** - Ready-to-use workflow examples
- **[Quick Start Guide](../docs/QUICKSTART.md)** - Getting started tutorial
- **[Use Cases](../docs/EXAMPLES.md)** - Detailed scenario walkthroughs

---

## 💬 Tips for Effective Communication

1. **Be Clear**: State exactly what you want to achieve
2. **Provide Context**: Include workflow IDs, error messages, and relevant details
3. **Ask Questions**: If unsure, ask Claude to explain or suggest options
4. **Iterate**: Start simple and gradually add complexity
5. **Validate**: Always validate before deploying to production
6. **Document**: Use intent metadata to explain your design decisions
7. **Monitor**: Check execution history regularly
8. **Optimize**: Ask for performance improvements periodically

---

**Remember:** Claude has access to all your workflows and can help you understand, modify, and optimize them. Don't hesitate to ask questions or request explanations!

**Happy Automating! 🎉**
