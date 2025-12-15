# ⚡ Quick Start - n8n Workflow Builder

Get started in 5 minutes! 🚀

## 1️⃣ Get API Key (2 Min)

1. Go to your n8n instance (e.g., `https://your-n8n-instance.com`)
2. **Settings** (bottom left) > **API**
3. Click **"Create New API Key"**
4. Copy the key (looks like: `n8n_api_...`)

## 2️⃣ Setup (1 Min)

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
N8N_API_URL=https://your-n8n-instance.com
N8N_API_KEY=YOUR_KEY_HERE
EOF
```

## 3️⃣ Test (30 Sec)

```bash
python -m n8n_workflow_builder.server
# No errors? → Perfect!
# Errors? → Check .env
```

## 4️⃣ Claude Config (1 Min)

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "n8n-workflow-builder": {
      "command": "python",
      "args": ["-m", "n8n_workflow_builder.server"],
      "cwd": "/ABSOLUTE/PATH/TO/n8n-workflow-builder",
      "env": {
        "N8N_API_URL": "https://your-n8n-instance.com",
        "N8N_API_KEY": "YOUR_KEY_HERE"
      }
    }
  }
}
```

**IMPORTANT**: Use absolute path! Use `pwd` in terminal.

## 5️⃣ Ready! (30 Sec)

1. **Quit Claude Desktop completely**
2. **Restart**
3. **Test**:

```
You: "Show me all my n8n workflows"
```

## 🎉 That's it!

### First Steps:

**Node Suggestions:**
```
"Suggest nodes for a workflow that fetches daily sales data from Postgres and sends it via Telegram"
```

**Generate Workflow:**
```
"Generate a workflow template for an API endpoint that validates and stores data"
```

**Analyze Workflow:**
```
"Analyze my workflow 'Daily Report' for issues"
```

**Explain Node:**
```
"Explain the HTTP Request node with best practices"
```

---

## 💥 Troubleshooting

### Claude can't find the server
- **Completely quit** Claude (including background processes!)
- Check config file for **syntax errors** (valid JSON?)
- Use **absolute path**, not relative!
- Restart Claude

### Authentication Error
- **Generate a new** API key in n8n
- No **spaces** in the key
- `.env` file correctly formatted?

### Server crashed
```bash
# Check logs
python -m n8n_workflow_builder.server

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

**Happy n8n Building! 🚀**
