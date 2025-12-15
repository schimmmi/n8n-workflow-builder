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

### 📚 Knowledge Base
- **Node Encyclopedia**: Detailed explanations of all important n8n nodes
- **Use Cases & Examples**: Practical examples for each node type
- **Configuration Tips**: How to optimally configure each node

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

### Edit Workflow
```
You: "Rename workflow abc-123 to 'Production Data Sync'"

Claude uses: update_workflow
→ Workflow is renamed
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

## 📝 License

MIT - Do whatever you want!

## 🙏 Credits

- Built for awesome n8n automation 🚀
- Powered by Claude MCP ⚡
- Made with ❤️ for DevOps Engineers

---

**Happy Automating!** 🎊

For questions or problems: Just ask Claude! 😉
