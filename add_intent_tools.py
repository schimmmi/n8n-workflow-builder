#!/usr/bin/env python3
"""Script to add Intent Management tools to server.py"""

# Read the server file
with open('src/n8n_workflow_builder/server.py', 'r') as f:
    content = f.read()

# Find the position to insert tools (before the closing ] of the list_tools return statement)
# Look for the last Tool( before the closing ]
import re

# Find the last Tool definition before ]
last_tool_pattern = r'(Tool\([^)]+name="get_template_details"[^]]+\)\s*)\s*\]'
match = re.search(last_tool_pattern, content, re.DOTALL)

if not match:
    print("❌ Could not find insertion point for tools")
    exit(1)

# Define the new intent tools
intent_tools = """,
            Tool(
                name="add_node_intent",
                description=(
                    "📝 Add 'why' metadata to a workflow node for AI context continuity. "
                    "Helps LLMs remember the reasoning, assumptions, and risks across iterations. "
                    "This is crucial for maintaining design decisions over time."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "string",
                            "description": "Workflow ID"
                        },
                        "node_name": {
                            "type": "string",
                            "description": "Name of the node to add intent to"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Why this node exists / what problem it solves"
                        },
                        "assumption": {
                            "type": "string",
                            "description": "Optional: Assumptions made when building this node"
                        },
                        "risk": {
                            "type": "string",
                            "description": "Optional: Known risks or limitations"
                        },
                        "alternative": {
                            "type": "string",
                            "description": "Optional: Alternative approaches considered"
                        },
                        "dependency": {
                            "type": "string",
                            "description": "Optional: Dependencies on other nodes or systems"
                        }
                    },
                    "required": ["workflow_id", "node_name", "reason"]
                }
            ),
            Tool(
                name="get_workflow_intents",
                description=(
                    "📋 Get all intent metadata from a workflow. "
                    "Shows the 'why' behind each node - perfect for understanding existing workflows "
                    "or resuming work after a break."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "string",
                            "description": "Workflow ID"
                        },
                        "format": {
                            "type": "string",
                            "description": "Output format: 'report' (markdown) or 'json' (structured data)",
                            "enum": ["report", "json"],
                            "default": "report"
                        }
                    },
                    "required": ["workflow_id"]
                }
            ),
            Tool(
                name="analyze_intent_coverage",
                description=(
                    "📊 Analyze how well a workflow is documented with intent metadata. "
                    "Shows coverage percentage, identifies nodes without intent, "
                    "and provides recommendations for improving documentation."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "string",
                            "description": "Workflow ID to analyze"
                        }
                    },
                    "required": ["workflow_id"]
                }
            ),
            Tool(
                name="suggest_node_intent",
                description=(
                    "💡 Get AI-generated intent template for a specific node. "
                    "Provides a starting point for documenting the 'why' based on node type and context. "
                    "Saves time and ensures consistent documentation."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "string",
                            "description": "Workflow ID"
                        },
                        "node_name": {
                            "type": "string",
                            "description": "Node name to generate suggestion for"
                        }
                    },
                    "required": ["workflow_id", "node_name"]
                }
            ),
            Tool(
                name="update_node_intent",
                description=(
                    "✏️ Update existing intent metadata for a node. "
                    "Use this to refine the documentation as understanding evolves "
                    "or circumstances change."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "string",
                            "description": "Workflow ID"
                        },
                        "node_name": {
                            "type": "string",
                            "description": "Node name to update"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Optional: Updated reason"
                        },
                        "assumption": {
                            "type": "string",
                            "description": "Optional: Updated assumptions"
                        },
                        "risk": {
                            "type": "string",
                            "description": "Optional: Updated risks"
                        },
                        "alternative": {
                            "type": "string",
                            "description": "Optional: Updated alternatives"
                        },
                        "dependency": {
                            "type": "string",
                            "description": "Optional: Updated dependencies"
                        }
                    },
                    "required": ["workflow_id", "node_name"]
                }
            ),
            Tool(
                name="remove_node_intent",
                description=(
                    "🗑️ Remove intent metadata from a node. "
                    "Use when intent is no longer relevant or needs to be completely rewritten."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "string",
                            "description": "Workflow ID"
                        },
                        "node_name": {
                            "type": "string",
                            "description": "Node name to remove intent from"
                        }
                    },
                    "required": ["workflow_id", "node_name"]
                }
            )"""

# Insert the tools before the closing ]
new_content = content.replace(match.group(1) + '        ]', match.group(1) + intent_tools + '\n        ]')

# Write back
with open('src/n8n_workflow_builder/server.py', 'w') as f:
    f.write(new_content)

print("✅ Intent tools added to list_tools()")
print(f"   Added 6 new tools for intent management")
