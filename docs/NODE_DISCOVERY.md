# 📦 Node Discovery System

> **Workflow-based learning system that discovers available n8n nodes, their parameters, and usage patterns from existing workflows.**

## Overview

The Node Discovery system solves a critical challenge: **How do we know what n8n nodes are available without relying on API endpoints?**

Instead of querying the n8n API (which may not expose node schemas), this system **learns from your existing workflows** to build a comprehensive knowledge base of:
- Available node types
- Parameters each node accepts
- Credential requirements
- Real-world usage examples
- Node popularity and patterns

### Why Workflow-Based Learning?

✅ **Works on all n8n versions** - No API dependency
✅ **Real-world schemas** - Parameters from actual usage, not documentation
✅ **Persistent knowledge** - SQLite database survives restarts
✅ **Zero configuration** - Automatically learns as you use it

---

## Features

### 1. 🔍 **Node Discovery**
Analyzes all workflows to extract node types, parameters, and usage patterns.

```bash
discover_nodes()
→ Analyzes 42 workflows
→ Discovers 66 unique node types
→ Tracks 1644 node instances
→ Saves to ~/.n8n-mcp/node_discovery.db
```

**What it learns:**
- Node types used in your workflows
- Parameters each node accepts (with inferred types)
- Credential requirements
- Node popularity (usage count)
- Real-world configuration examples

### 2. 📊 **Schema Extraction**
Provides detailed schemas for discovered nodes with usage insights.

```bash
get_node_schema("n8n-nodes-base.googleSheets")
→ Type: n8n-nodes-base.googleSheets
→ Version: 4
→ Usage Count: 87 times
→ Parameters: 23 discovered
  - operation (string)
  - resource (string)
  - sheetId (string)
  - range (string)
  ...
```

**Schema includes:**
- All parameter names observed across workflows
- Inferred parameter types (string, number, boolean, object, array)
- Credential requirements
- Usage statistics

### 3. 🔎 **Smart Search**
Search for nodes by keyword with category tagging.

```bash
search_nodes("http")
→ 🌐 HTTP Request (http category)
→ ⚡ Webhook (trigger category)
→ 🌐 HTTP Request Node (http category)
```

**Features:**
- Keyword matching in node type and name
- Category icons (⚡📊🔄📬🌐🔀🔧)
- Sorted by popularity
- Shows parameter count and version

### 4. 💡 **Smart Recommendations**
Task-based node recommendations with advanced scoring.

```bash
recommend_nodes_for_task("send slack message")
→ 1. Telegram (16.4/10)
     Reason: Matches: send, message • highly popular
→ 2. chatTrigger (11.9/10)
     Reason: Similar: slack • commonly used
→ 3. Gmail (10.2/10)
     Reason: Matches: send, message
```

**Scoring Algorithm:**
- **Exact keyword match:** 5 points
- **Synonym match:** 2.5 points (0.5x weight)
- **Name match:** 3 points
- **Parameter match:** +1 point
- **Popularity boost:** max 3 points (if keywords match)

---

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────┐
│                   Node Discovery System                  │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐      ┌──────────────────┐            │
│  │ NodeDiscovery│◄─────┤  Workflows       │            │
│  │              │      │  (n8n API)       │            │
│  └──────┬───────┘      └──────────────────┘            │
│         │                                                │
│         │ Extracts                                       │
│         ▼                                                │
│  ┌──────────────┐      ┌──────────────────┐            │
│  │ Node Schemas │──────►│  SQLite DB       │            │
│  │ Parameters   │      │  ~/.n8n-mcp/     │            │
│  │ Usage Stats  │      │  node_discovery  │            │
│  └──────┬───────┘      └──────────────────┘            │
│         │                                                │
│         │ Feeds                                          │
│         ▼                                                │
│  ┌──────────────────┐                                   │
│  │ NodeRecommender  │                                   │
│  │ - Synonym Match  │                                   │
│  │ - Scoring        │                                   │
│  │ - Ranking        │                                   │
│  └──────────────────┘                                   │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

```
1. User calls discover_nodes()
   ↓
2. Fetch all workflows from n8n API
   ↓
3. For each workflow:
   - Extract node types
   - Collect parameters
   - Track credentials
   - Infer parameter types
   ↓
4. Aggregate & deduplicate
   ↓
5. Save to SQLite (~/.n8n-mcp/node_discovery.db)
   ↓
6. Return summary
```

### Database Schema

```sql
CREATE TABLE discovered_nodes (
    node_type TEXT PRIMARY KEY,
    name TEXT,
    type_version INTEGER,
    usage_count INTEGER DEFAULT 0,
    parameters TEXT,           -- JSON: {param_name: param_value}
    parameter_types TEXT,      -- JSON: {param_name: inferred_type}
    credentials TEXT,          -- JSON: credential info
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Advanced Features

### 1. **Synonym Matching** 🔄

Bidirectional synonym support for 40+ common terms:

| User Says | Also Matches |
|-----------|--------------|
| `slack` | telegram, discord, mattermost, matrix, chat, message |
| `excel` | sheets, spreadsheet, airtable, table |
| `database` | postgres, mysql, mongodb, sql, db |
| `send` | post, push, publish, transmit |
| `read` | get, fetch, retrieve, load |
| `cloud` | drive, dropbox, s3, storage |

**Example:**
```bash
recommend_nodes_for_task("send slack notification")
→ Finds Telegram node with "Similar: slack" reason
```

**How it works:**
1. User says "slack"
2. System expands to: slack + [telegram, discord, chat, message]
3. Matches nodes containing any of these terms
4. Shows "Similar: slack" if matched via synonym

### 2. **Parameter-Based Scoring** 🎯

Nodes with relevant parameters get bonus points:

```bash
Task: "send email with attachment"
→ Gmail node has "attachments" parameter → +1 point
→ SMTP node has "attachments" parameter → +1 point
→ Helps distinguish similar nodes by capabilities
```

### 3. **Category Tagging** 🏷️

Automatic categorization based on node type:

| Category | Icon | Keywords |
|----------|------|----------|
| `trigger` | ⚡ | trigger, webhook, schedule, cron, manual |
| `data_source` | 📊 | sheets, airtable, database, postgres, drive |
| `transform` | 🔄 | code, function, set, merge, split, filter |
| `notification` | 📬 | telegram, slack, email, gmail, sms |
| `http` | 🌐 | http, webhook, request, api |
| `logic` | 🔀 | if, switch, router, compare, condition |
| `utility` | 🔧 | wait, sticky, note, error, stop |

**Usage in search:**
```bash
search_nodes("trigger")
→ ⚡ Webhook Trigger (trigger category)
→ ⚡ Schedule Trigger (trigger category)
→ ⚡ Manual Trigger (trigger category)
```

### 4. **Stopword Filtering** 🚫

Common English words are filtered to improve matching:

```
Filtered: a, an, and, are, as, at, be, by, for, from, has, in, is, it,
          of, on, that, the, to, was, will, with

Also filtered: Words < 3 characters
```

**Example:**
```
"read data from Google Sheets"
→ Keywords: [read, data, google, sheets]  (from, the filtered)
```

---

## Usage Examples

### Example 1: Discover All Nodes

```javascript
// Analyze all workflows and build node knowledge
await discover_nodes()
```

**Output:**
```
📦 Node Discovery Complete

Analyzed: 42 workflows
Discovered: 66 unique node types
Total Usage: 1644 node instances

🔥 Most Popular Nodes
- stickyNote: 222 uses
- httpRequest: 180 uses
- code: 105 uses
- googleSheets: 87 uses
- telegram: 76 uses

💡 Next Steps:
- Use get_node_schema(node_type) to see parameters
- Use search_nodes(keyword) to find nodes
- Use recommend_nodes_for_task(task) to get recommendations

✅ Knowledge saved to: /Users/you/.n8n-mcp/node_discovery.db
```

### Example 2: Get Node Schema

```javascript
// Get detailed schema for a specific node
await get_node_schema("n8n-nodes-base.telegram")
```

**Output:**
```
🔍 Node Schema: Telegram

Type: n8n-nodes-base.telegram
Version: 1
Usage Count: 76 times in workflows

Parameters (18)
Discovered from real workflow usage:

- chatId (type: string)
- text (type: string)
- operation (type: string)
- resource (type: string)
- replyMarkup (type: object)
- parseMode (type: string)
- disableWebPagePreview (type: boolean)
...

Credentials
{
  "telegramApi": {
    "displayName": "Telegram API",
    "name": "telegramApi",
    "required": true
  }
}

📊 Usage Insights
This node has been used 76 times across analyzed workflows.
Total parameters observed: 18

💡 Tip: These schemas are learned from real workflows.
Run discover_nodes periodically to update knowledge.
```

### Example 3: Search Nodes

```javascript
// Search for nodes by keyword
await search_nodes("google")
```

**Output:**
```
🔎 Search Results for 'google' (8 matches)

## 📊 Google Sheets
- Type: n8n-nodes-base.googleSheets
- Category: data_source
- Usage Count: 87 times
- Parameters: 23 discovered
- Version: 4

## 📊 Google Drive
- Type: n8n-nodes-base.googleDrive
- Category: data_source
- Usage Count: 45 times
- Parameters: 19 discovered
- Version: 3

## ⚡ Google Sheets Trigger
- Type: n8n-nodes-base.googleSheetsTrigger
- Category: trigger
- Usage Count: 12 times
- Parameters: 8 discovered
- Version: 1

💡 Tip: Use get_node_schema('n8n-nodes-base.googleSheets') to see detailed parameters.
```

### Example 4: Get Recommendations

```javascript
// Get node recommendations for a specific task
await recommend_nodes_for_task("send slack message", 5)
```

**Output:**
```
💡 Node Recommendations for Task

Task: send slack message
Found: 5 matching nodes

1. Telegram
   - Type: n8n-nodes-base.telegram
   - Score: 16.4/10
   - Usage Count: 76 times
   - Reason: Matches: send, message • highly popular

2. chatTrigger
   - Type: n8n-nodes-base.chatTrigger
   - Score: 11.9/10
   - Usage Count: 34 times
   - Reason: Similar: slack • commonly used

3. Gmail
   - Type: n8n-nodes-base.gmail
   - Score: 10.2/10
   - Usage Count: 89 times
   - Reason: Matches: send, message • highly popular

4. telegramTrigger
   - Type: n8n-nodes-base.telegramTrigger
   - Score: 9.8/10
   - Usage Count: 23 times
   - Reason: Similar: message, slack

5. lmChatAnthropic
   - Type: n8n-nodes-base.lmChatAnthropic
   - Score: 8.4/10
   - Usage Count: 45 times
   - Reason: Similar: message, slack

💡 Next Steps:
- Use get_node_schema('n8n-nodes-base.telegram') to see parameters
- Use generate_workflow to create a workflow with these nodes
```

---

## MCP Tools

### `discover_nodes`

**Description:** Analyze all workflows to discover node types and build knowledge base.

**Parameters:** None

**Returns:** Summary with discovered nodes, usage stats, and most popular nodes

**Example:**
```javascript
{
  "name": "discover_nodes"
}
```

---

### `get_node_schema`

**Description:** Get detailed schema for a specific discovered node type.

**Parameters:**
- `node_type` (string, required): The node type to get schema for

**Returns:** Node schema with parameters, types, credentials, and usage insights

**Example:**
```javascript
{
  "name": "get_node_schema",
  "arguments": {
    "node_type": "n8n-nodes-base.telegram"
  }
}
```

---

### `search_nodes`

**Description:** Search discovered nodes by keyword.

**Parameters:**
- `query` (string, required): Keyword to search for in node types and names

**Returns:** List of matching nodes with categories, usage counts, and parameters

**Example:**
```javascript
{
  "name": "search_nodes",
  "arguments": {
    "query": "google"
  }
}
```

---

### `recommend_nodes_for_task`

**Description:** Get node recommendations for a specific task using advanced scoring.

**Parameters:**
- `task_description` (string, required): Natural language description of the task
- `top_k` (integer, optional): Number of recommendations to return (default: 5)

**Returns:** Ranked list of recommended nodes with scores and reasons

**Example:**
```javascript
{
  "name": "recommend_nodes_for_task",
  "arguments": {
    "task_description": "send email notifications when database updates",
    "top_k": 5
  }
}
```

---

## Best Practices

### 1. **Run Discovery Regularly**

Update node knowledge as your workflows evolve:

```javascript
// Weekly: Update node discovery
await discover_nodes()
```

**When to re-run:**
- After adding new workflows
- After updating n8n version
- When new nodes are installed
- Monthly as general maintenance

### 2. **Use Specific Task Descriptions**

Better task descriptions = better recommendations:

❌ **Bad:** "send message"
✅ **Good:** "send slack notification with attachment"

❌ **Bad:** "process data"
✅ **Good:** "transform JSON data and filter by date"

### 3. **Check Parameter Schemas Before Building**

Always verify node parameters before workflow generation:

```javascript
// 1. Get recommendations
const nodes = await recommend_nodes_for_task("send email")

// 2. Check schema for top recommendation
const schema = await get_node_schema(nodes[0].type)

// 3. Use schema to build workflow with correct parameters
```

### 4. **Leverage Categories**

Use category search to find nodes by purpose:

```javascript
// Find all trigger nodes
await search_nodes("trigger")

// Find all data sources
await search_nodes("sheets")

// Find all notification nodes
await search_nodes("telegram")
```

### 5. **Understand Scoring**

Recommendation scores explain node relevance:

- **15-20:** Perfect match (multiple exact keywords + popular)
- **10-15:** Strong match (keyword + synonyms + popular)
- **5-10:** Good match (synonyms or partial keywords)
- **< 5:** Weak match (popularity only, few keywords)

---

## Troubleshooting

### Issue: "No nodes discovered yet"

**Cause:** Discovery hasn't been run or database is empty

**Solution:**
```javascript
await discover_nodes()
```

---

### Issue: "Node type not found in discovered nodes"

**Cause:** Node hasn't been used in any analyzed workflows

**Solutions:**
1. Use the node in a workflow
2. Re-run `discover_nodes()`
3. Search for similar nodes with `search_nodes()`

---

### Issue: Recommendations not relevant

**Possible causes:**
- Task description too vague
- Synonyms not matching
- Node never used in workflows

**Solutions:**
1. Use more specific task descriptions
2. Check if synonyms exist for your terms
3. Add more workflows using those nodes
4. Use `search_nodes()` for direct keyword search

---

### Issue: Database file too large

**Cause:** Many workflows with many nodes

**Solution:**
```bash
# Database location
~/.n8n-mcp/node_discovery.db

# Check size
du -h ~/.n8n-mcp/node_discovery.db

# Reset if needed (will re-learn on next discover_nodes)
rm ~/.n8n-mcp/node_discovery.db
```

---

## Performance

### Discovery Performance

| Workflows | Nodes | Time | Database Size |
|-----------|-------|------|---------------|
| 10 | 150 | ~2s | 50 KB |
| 50 | 750 | ~8s | 200 KB |
| 100 | 1500 | ~15s | 400 KB |
| 500 | 7500 | ~60s | 2 MB |

### Recommendation Performance

| Discovered Nodes | Query Time |
|------------------|------------|
| 50 | < 100ms |
| 100 | < 200ms |
| 500 | < 500ms |

**Optimization tips:**
- Discovery is one-time per session (cached in memory)
- Database loads on server start
- Recommendations use in-memory data (fast)
- Re-run discovery only when needed

---

## Future Enhancements

### Planned Features

1. **Usage Pattern Analysis** 🔄
   - Track common node combinations
   - Suggest node sequences based on patterns
   - "Users who use X also use Y"

2. **Parameter Value Learning** 📊
   - Learn common parameter values
   - Suggest default configurations
   - Auto-fill based on context

3. **Workflow Template Mining** ⛏️
   - Extract reusable patterns from workflows
   - Generate templates from common structures
   - Suggest templates for tasks

4. **Node Deprecation Detection** ⚠️
   - Detect old node versions
   - Suggest migration paths
   - Track breaking changes

5. **Custom Synonym Dictionaries** 📖
   - User-defined synonyms
   - Domain-specific terminology
   - Multi-language support

---

## Technical Details

### Synonym Algorithm

```python
# Bidirectional synonym mapping
SYNONYMS = {
    'slack': ['telegram', 'discord', 'chat'],
    'telegram': ['slack', 'discord', 'chat'],
    # ... more mappings
}

# When user says "slack":
1. Forward match: Expand to [slack, telegram, discord, chat]
2. Reverse match: Find nodes containing any synonym
3. Score: Exact=5pts, Synonym=2.5pts, Popular=+3pts
4. Reason: Show original keyword ("slack") in "Similar:" section
```

### Parameter Type Inference

```python
def infer_type(value):
    if isinstance(value, bool): return 'boolean'
    if isinstance(value, int): return 'number'
    if isinstance(value, float): return 'number'
    if isinstance(value, list): return 'array'
    if isinstance(value, dict): return 'object'
    return 'string'
```

### Category Classification

```python
def categorize_node(node_type):
    node_lower = node_type.lower()

    # Check category keywords
    if 'trigger' in node_lower or 'webhook' in node_lower:
        return 'trigger'
    if 'sheets' in node_lower or 'database' in node_lower:
        return 'data_source'
    # ... more checks

    return 'other'
```

---

## Contributing

### Adding New Synonyms

Edit `src/n8n_workflow_builder/node_discovery.py`:

```python
SYNONYMS = {
    # Add your synonyms here
    'your_term': ['synonym1', 'synonym2', 'synonym3'],
}
```

### Adding New Categories

```python
NODE_CATEGORIES = {
    'your_category': ['keyword1', 'keyword2', 'keyword3'],
}
```

---

## License

Part of the n8n-workflow-builder MCP Server.

---

## Support

For issues, questions, or feature requests:
- GitHub Issues: https://github.com/schimmmi/n8n-workflow-builder/issues
- Documentation: https://github.com/schimmmi/n8n-workflow-builder/docs

---

**Last Updated:** 2025-12-17
**Version:** 1.19.0
