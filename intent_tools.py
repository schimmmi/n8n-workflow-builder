# Intent Management Tools to add to server.py list_tools()

INTENT_TOOLS = [
    {
        "name": "add_node_intent",
        "description": (
            "📝 Add 'why' metadata to a workflow node for AI context continuity. "
            "Helps LLMs remember the reasoning, assumptions, and risks across iterations. "
            "This is crucial for maintaining design decisions over time."
        ),
        "inputSchema": {
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
    },
    {
        "name": "get_workflow_intents",
        "description": (
            "📋 Get all intent metadata from a workflow. "
            "Shows the 'why' behind each node - perfect for understanding existing workflows "
            "or resuming work after a break."
        ),
        "inputSchema": {
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
    },
    {
        "name": "analyze_intent_coverage",
        "description": (
            "📊 Analyze how well a workflow is documented with intent metadata. "
            "Shows coverage percentage, identifies nodes without intent, "
            "and provides recommendations for improving documentation."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "workflow_id": {
                    "type": "string",
                    "description": "Workflow ID to analyze"
                }
            },
            "required": ["workflow_id"]
        }
    },
    {
        "name": "suggest_node_intent",
        "description": (
            "💡 Get AI-generated intent template for a specific node. "
            "Provides a starting point for documenting the 'why' based on node type and context. "
            "Saves time and ensures consistent documentation."
        ),
        "inputSchema": {
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
    },
    {
        "name": "update_node_intent",
        "description": (
            "✏️ Update existing intent metadata for a node. "
            "Use this to refine the documentation as understanding evolves "
            "or circumstances change."
        ),
        "inputSchema": {
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
    },
    {
        "name": "remove_node_intent",
        "description": (
            "🗑️ Remove intent metadata from a node. "
            "Use when intent is no longer relevant or needs to be completely rewritten."
        ),
        "inputSchema": {
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
    }
]


# Intent Management Tool Handlers to add to call_tool()

INTENT_HANDLERS = """
            elif name == "add_node_intent":
                workflow_id = arguments["workflow_id"]
                node_name = arguments["node_name"]
                reason = arguments["reason"]
                assumption = arguments.get("assumption")
                risk = arguments.get("risk")
                alternative = arguments.get("alternative")
                dependency = arguments.get("dependency")

                # Fetch workflow
                workflow = await n8n_client.get_workflow(workflow_id)

                # Find node
                node = None
                for n in workflow.get("nodes", []):
                    if n["name"] == node_name:
                        node = n
                        break

                if not node:
                    return [TextContent(
                        type="text",
                        text=f"❌ Node '{node_name}' not found in workflow"
                    )]

                # Create intent
                intent = intent_manager.create_intent(
                    reason=reason,
                    assumption=assumption,
                    risk=risk,
                    alternative=alternative,
                    dependency=dependency
                )

                # Add intent to node
                intent_manager.add_intent_to_node(node, intent)

                # Update workflow
                updated_workflow = await n8n_client.update_workflow(workflow_id, {
                    "nodes": workflow["nodes"]
                })

                # Log action
                state_manager.log_action("add_node_intent", {
                    "workflow_id": workflow_id,
                    "node_name": node_name
                })

                result = f"✅ Intent added to node: **{node_name}**\\n\\n"
                result += f"**Reason:** {reason}\\n"
                if assumption:
                    result += f"**Assumption:** {assumption}\\n"
                if risk:
                    result += f"**Risk:** {risk}\\n"
                if alternative:
                    result += f"**Alternative:** {alternative}\\n"
                if dependency:
                    result += f"**Dependency:** {dependency}\\n"

                return [TextContent(type="text", text=result)]

            elif name == "get_workflow_intents":
                workflow_id = arguments["workflow_id"]
                format_type = arguments.get("format", "report")

                # Fetch workflow
                workflow = await n8n_client.get_workflow(workflow_id)

                # Log action
                state_manager.log_action("get_workflow_intents", {
                    "workflow_id": workflow_id,
                    "format": format_type
                })

                if format_type == "json":
                    intents = intent_manager.get_workflow_intents(workflow)
                    result = json.dumps(intents, indent=2)
                else:
                    result = intent_manager.generate_intent_report(workflow)

                return [TextContent(type="text", text=result)]

            elif name == "analyze_intent_coverage":
                workflow_id = arguments["workflow_id"]

                # Fetch workflow
                workflow = await n8n_client.get_workflow(workflow_id)

                # Analyze coverage
                analysis = intent_manager.analyze_intent_coverage(workflow)

                # Log action
                state_manager.log_action("analyze_intent_coverage", {
                    "workflow_id": workflow_id,
                    "coverage": analysis["coverage_percentage"]
                })

                # Format result
                result = f"# Intent Coverage Analysis: {workflow['name']}\\n\\n"
                result += f"**Coverage**: {analysis['coverage_percentage']}%\\n"
                result += f"**Nodes with Intent**: {analysis['nodes_with_intent']} / {analysis['total_nodes']}\\n"
                result += f"**Nodes without Intent**: {analysis['nodes_without_intent']}\\n\\n"

                if analysis['critical_without_intent']:
                    result += "## ⚠️ Critical Nodes Missing Intent:\\n\\n"
                    for node_name in analysis['critical_without_intent']:
                        result += f"- {node_name}\\n"
                    result += "\\n"

                result += "## Node Breakdown:\\n\\n"
                result += f"- Triggers: {analysis['node_breakdown']['triggers']}\\n"
                result += f"- Logic nodes: {analysis['node_breakdown']['logic']}\\n"
                result += f"- Action nodes: {analysis['node_breakdown']['actions']}\\n\\n"

                result += f"## 💡 Recommendation\\n\\n{analysis['recommendation']}"

                return [TextContent(type="text", text=result)]

            elif name == "suggest_node_intent":
                workflow_id = arguments["workflow_id"]
                node_name = arguments["node_name"]

                # Fetch workflow
                workflow = await n8n_client.get_workflow(workflow_id)

                # Find node
                node = None
                for n in workflow.get("nodes", []):
                    if n["name"] == node_name:
                        node = n
                        break

                if not node:
                    return [TextContent(
                        type="text",
                        text=f"❌ Node '{node_name}' not found in workflow"
                    )]

                # Generate suggestion
                suggestion = intent_manager.suggest_intent_for_node(node, workflow)

                # Log action
                state_manager.log_action("suggest_node_intent", {
                    "workflow_id": workflow_id,
                    "node_name": node_name
                })

                return [TextContent(type="text", text=suggestion)]

            elif name == "update_node_intent":
                workflow_id = arguments["workflow_id"]
                node_name = arguments["node_name"]

                # Fetch workflow
                workflow = await n8n_client.get_workflow(workflow_id)

                # Find node
                node = None
                for n in workflow.get("nodes", []):
                    if n["name"] == node_name:
                        node = n
                        break

                if not node:
                    return [TextContent(
                        type="text",
                        text=f"❌ Node '{node_name}' not found in workflow"
                    )]

                # Build updates
                updates = {}
                if "reason" in arguments:
                    updates["reason"] = arguments["reason"]
                if "assumption" in arguments:
                    updates["assumption"] = arguments["assumption"]
                if "risk" in arguments:
                    updates["risk"] = arguments["risk"]
                if "alternative" in arguments:
                    updates["alternative"] = arguments["alternative"]
                if "dependency" in arguments:
                    updates["dependency"] = arguments["dependency"]

                if not updates:
                    return [TextContent(
                        type="text",
                        text="No updates provided. Specify at least one field to update."
                    )]

                # Update intent
                intent_manager.update_node_intent(node, updates)

                # Update workflow
                updated_workflow = await n8n_client.update_workflow(workflow_id, {
                    "nodes": workflow["nodes"]
                })

                # Log action
                state_manager.log_action("update_node_intent", {
                    "workflow_id": workflow_id,
                    "node_name": node_name,
                    "fields_updated": list(updates.keys())
                })

                result = f"✅ Intent updated for node: **{node_name}**\\n\\n"
                result += "**Updated fields:**\\n"
                for key, value in updates.items():
                    result += f"- {key}: {value}\\n"

                return [TextContent(type="text", text=result)]

            elif name == "remove_node_intent":
                workflow_id = arguments["workflow_id"]
                node_name = arguments["node_name"]

                # Fetch workflow
                workflow = await n8n_client.get_workflow(workflow_id)

                # Find node
                node = None
                for n in workflow.get("nodes", []):
                    if n["name"] == node_name:
                        node = n
                        break

                if not node:
                    return [TextContent(
                        type="text",
                        text=f"❌ Node '{node_name}' not found in workflow"
                    )]

                # Check if node has intent
                if "_intent" not in node:
                    return [TextContent(
                        type="text",
                        text=f"ℹ️ Node '{node_name}' has no intent metadata to remove"
                    )]

                # Remove intent
                intent_manager.remove_intent_from_node(node)

                # Update workflow
                updated_workflow = await n8n_client.update_workflow(workflow_id, {
                    "nodes": workflow["nodes"]
                })

                # Log action
                state_manager.log_action("remove_node_intent", {
                    "workflow_id": workflow_id,
                    "node_name": node_name
                })

                return [TextContent(
                    type="text",
                    text=f"✅ Intent metadata removed from node: **{node_name}**"
                )]
"""
