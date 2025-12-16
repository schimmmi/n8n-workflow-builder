# State Management & Context Tracking

The n8n Workflow Builder MCP Server includes a powerful state management system that tracks your workflow operations across multiple Claude conversations.

## 📍 Features

### 1. Active Workflow Tracking
When you work with a workflow (analyze, get details, etc.), the server **automatically** sets it as the "active workflow". This allows you to reference it later without remembering IDs.

**Example:**
```
You: "Analyze workflow abc-123"
→ Workflow "Production Sync" is now active

Later...
You: "Execute the current workflow"
→ Claude knows you mean "Production Sync" (abc-123)
```

### 2. Recent Workflows
The server remembers your last 10 workflows, ordered by most recent access.

**Use case:** "Show me my recent workflows" - quickly see what you've been working on.

### 3. Session History
Every action is logged with timestamp and details:
- `analyze_workflow`
- `execute_workflow`
- `get_workflow_details`
- `update_workflow`
- etc.

**Use case:** "What did I do in the last hour?" - see your complete action timeline.

### 4. Last Execution Tracking
When you execute a workflow, the execution ID is stored automatically.

**Use case:** "Show details for the last execution" - no need to remember execution IDs.

## 🔧 Available Tools

### `get_session_state`
Get a complete overview of the current session:
- Active workflow
- Last execution ID
- Recent workflows (top 5)
- Recent actions (top 5)

```
You: "What's my current state?"
→ Summary of everything you're working on
```

### `set_active_workflow`
Manually set a workflow as active:

```
You: "Set workflow abc-123 as active"
→ Workflow is now the "current workflow"
```

### `get_active_workflow`
Get the current active workflow:

```
You: "What's the active workflow?"
→ Name and ID of current workflow
```

### `get_recent_workflows`
List last 10 workflows:

```
You: "Show recent workflows"
→ List with names, IDs, and timestamps
```

### `get_session_history`
View action history:

```
You: "Show me what I did today"
→ Timeline of all operations
```

### `clear_session_state`
Reset all state:

```
You: "Clear my session"
→ All state is reset
```

## 💾 Storage

State is stored in: `~/.n8n_workflow_builder_state.json`

**Structure:**
```json
{
  "current_workflow_id": "abc-123",
  "current_workflow_name": "Production Sync",
  "last_execution_id": "exec-456",
  "recent_workflows": [...],
  "session_history": [...],
  "created_at": "2025-12-16T08:00:00",
  "last_updated": "2025-12-16T10:30:00"
}
```

### Benefits
- **Persistent**: Survives Claude restarts
- **Lightweight**: Only stores IDs and metadata
- **Privacy**: Stays local on your machine

## 🎯 Use Cases

### 1. Continuing Work
```
Session 1:
You: "Analyze workflow 'Daily Reports'"
→ Workflow is now active

Session 2 (later):
You: "Execute the current workflow"
→ Claude knows you mean 'Daily Reports'
```

### 2. Debugging
```
You: "Execute workflow abc-123"
→ Execution ID: exec-789

You: "Show the last execution details"
→ Claude shows exec-789 automatically
```

### 3. Context Awareness
```
You: "What workflows did I work on today?"
→ List of all recent workflows with timestamps

You: "Show me my action history"
→ Complete timeline of operations
```

### 4. Multiple Workflows
```
You: "Analyze workflow A"
You: "Analyze workflow B"
You: "Show recent workflows"
→ See both A and B with timestamps
```

## 🔄 Automatic Logging

These actions **automatically** update the state:

| Action | What's Tracked |
|--------|----------------|
| `get_workflow_details` | Sets as active workflow + logs action |
| `analyze_workflow` | Sets as active workflow + logs action |
| `execute_workflow` | Logs execution ID + action |
| `update_workflow` | Logs action |

## 📊 Example Workflow

```
# Start of session
You: "List my workflows"
→ Shows all workflows

You: "Analyze workflow 'Production Data Sync'"
→ Automatically set as active workflow
→ Logged: analyze_workflow action

You: "Execute the current workflow with {data: 123}"
→ Uses 'Production Data Sync'
→ Stores execution ID
→ Logged: execute_workflow action

You: "Show the last execution details"
→ Uses stored execution ID
→ Shows complete node data

# Later in session
You: "What have I been doing?"
→ Shows:
  - Active: Production Data Sync
  - Last execution: exec-456
  - Recent actions: analyze, execute
```

## 🛠️ Advanced Features

### Session Persistence
State survives between:
- Claude Desktop restarts
- Different chat sessions
- Multiple days

### Automatic Cleanup
- Recent workflows: Limited to 10
- Session history: Limited to 50 entries
- Old entries are automatically removed (FIFO)

### Error Handling
- If state file is corrupted → automatically reset
- Missing file → creates default state
- Invalid JSON → logs warning and resets

## 🔒 Privacy & Security

- **Local only**: State file stays on your machine
- **No secrets**: Only stores IDs and names, never credentials
- **No sync**: Not sent to any server
- **User control**: Can be cleared or deleted anytime

## 🧹 Maintenance

### View state file:
```bash
cat ~/.n8n_workflow_builder_state.json
```

### Clear state programmatically:
```
You: "Clear session state"
```

### Clear state manually:
```bash
rm ~/.n8n_workflow_builder_state.json
```

### Backup state:
```bash
cp ~/.n8n_workflow_builder_state.json ~/n8n_state_backup.json
```

## 🚀 Tips & Tricks

1. **Use descriptive names**: Named workflows are easier to track
2. **Check state regularly**: Use `get_session_state` to stay oriented
3. **Clean up old state**: Clear state when switching projects
4. **Leverage context**: Say "current workflow" instead of IDs

## 📝 Logging Format

Each history entry contains:
- `timestamp`: ISO 8601 format
- `action`: Tool name that was called
- `details`: Action-specific metadata

**Example:**
```json
{
  "timestamp": "2025-12-16T10:30:45.123456",
  "action": "execute_workflow",
  "details": {
    "workflow_id": "abc-123",
    "execution_id": "exec-456"
  }
}
```

## 🎓 Summary

The state management system makes your n8n workflow operations:
- **Contextual**: Reference "current workflow" instead of IDs
- **Traceable**: See exactly what you did and when
- **Persistent**: Context survives between sessions
- **Convenient**: Less copy-paste of IDs and names
- **Smart**: Automatically tracks important operations

This transforms the MCP server from a stateless API wrapper into an **intelligent workflow assistant** that remembers your context! 🚀
