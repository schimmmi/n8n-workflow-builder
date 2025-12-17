# 📁 Example Workflows

This directory contains ready-to-use n8n workflow examples that demonstrate common patterns and best practices.

## 🚀 Available Examples

### 1. Simple API Endpoint
**File:** `01_simple_api_endpoint.json`

A basic webhook-based API endpoint that responds with JSON.

**Use Case:**
- Quick API prototyping
- Webhook testing
- Simple data responses

**Nodes:**
- Webhook (trigger)
- Set (prepare response)
- Respond to Webhook

**How to use:**
```bash
# Import via CLI
n8n import:workflow --input=examples/01_simple_api_endpoint.json

# Or use the n8n Workflow Builder
"Import workflow from examples/01_simple_api_endpoint.json"
```

---

### 2. Daily Sales Report
**File:** `02_scheduled_report.json`

Automated daily report that fetches sales data from PostgreSQL and sends it to Slack.

**Use Case:**
- Scheduled reporting
- Database queries
- Team notifications

**Nodes:**
- Schedule Trigger (daily at 9 AM)
- Postgres (fetch data)
- Function (format report)
- Slack (send message)

**Configuration needed:**
- Postgres credentials
- Slack credentials
- Update SQL query for your schema

---

### 3. User Registration API with Validation
**File:** `03_data_validation_api.json`

Complete user registration API with input validation, database storage, and proper error handling.

**Use Case:**
- API with validation
- Data persistence
- Error handling patterns
- HTTP status codes

**Nodes:**
- Webhook (POST endpoint)
- IF (validate email, name, age)
- Set (prepare data)
- Postgres (save user)
- Respond to Webhook (success/error)

**Features:**
- ✅ Email format validation
- ✅ Age requirement (18+)
- ✅ Required field checks
- ✅ Proper HTTP status codes (201, 400)
- ✅ SQL injection protection

---

## 💡 How to Use These Examples

### Method 1: Via n8n Workflow Builder MCP Tool

```
"Import the simple API endpoint example workflow"
"Create a workflow based on example 02"
"Show me how to use example 03"
```

The MCP server can read these files and help you understand or modify them.

### Method 2: Direct Import to n8n

1. Copy the JSON content
2. Go to n8n UI
3. Click "Add workflow" → "Import from File/URL"
4. Paste the JSON
5. Configure credentials if needed
6. Activate workflow

### Method 3: CLI Import

```bash
n8n import:workflow --input=examples/01_simple_api_endpoint.json
```

---

## 🔧 Customization Tips

### Credentials
Most examples use placeholder credentials. You'll need to:
1. Create credentials in n8n (Settings → Credentials)
2. Update credential references in the workflow
3. Test the connections

### SQL Queries
Database examples assume a generic schema. Adapt queries to your tables:
```sql
-- Example schema for 02_scheduled_report.json
CREATE TABLE orders (
  id SERIAL PRIMARY KEY,
  amount DECIMAL(10,2),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Example schema for 03_data_validation_api.json
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255),
  email VARCHAR(255) UNIQUE,
  age INTEGER,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Webhook URLs
After importing, n8n will generate production webhook URLs like:
```
https://your-n8n-instance.com/webhook/abc123
```

---

## 📚 Learning Resources

- **[n8n Documentation](https://docs.n8n.io/)**
- **[Workflow Templates](https://n8n.io/workflows/)**
- **[MCP Tools Documentation](../docs/TOOLS.md)**

---

## 🤝 Contributing Examples

Have a great workflow example? Create a PR with:
1. The workflow JSON file (numbered: `04_your_example.json`)
2. Update this README with description
3. Include any required setup steps

---

## ⚠️ Important Notes

- **Credentials**: Never commit real credentials to Git
- **Testing**: Test workflows in a dev environment first
- **Security**: Enable webhook authentication for production APIs
- **Rate Limiting**: Add rate limiting for public endpoints
- **Error Handling**: These are basic examples - add more robust error handling for production

---

**Happy Automating! 🎉**
