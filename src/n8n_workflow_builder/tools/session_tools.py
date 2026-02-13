#!/usr/bin/env python3
"""
Session State Tool Handlers
Handles session state management, workflow tracking, and action history
"""
from typing import Any, TYPE_CHECKING

from mcp.types import TextContent

from .base import BaseTool, ToolError

if TYPE_CHECKING:
    from ..dependencies import Dependencies


class SessionTools(BaseTool):
    """Handler for session state and workflow tracking tools"""
    
    async def handle(self, name: str, arguments: dict) -> list[TextContent]:
        """Route session tool calls to appropriate handler methods
        
        Args:
            name: Tool name
            arguments: Tool arguments
            
        Returns:
            List of TextContent responses
        """
        handlers = {
            "get_session_state": self.get_session_state,
            "set_active_workflow": self.set_active_workflow,
            "get_active_workflow": self.get_active_workflow,
            "get_recent_workflows": self.get_recent_workflows,
            "get_session_history": self.get_session_history,
            "clear_session_state": self.clear_session_state,
        }
        
        handler = handlers.get(name)
        if not handler:
            raise ToolError("UNKNOWN_TOOL", f"Tool '{name}' not found in session tools")
        
        return await handler(arguments)
    
    async def get_session_state(self, arguments: dict) -> list[TextContent]:
        """Get summary of current session state"""
        result = self.deps.state_manager.get_state_summary()
        return [TextContent(type="text", text=result)]
    
    async def set_active_workflow(self, arguments: dict) -> list[TextContent]:
        """Set the active workflow for the session"""
        workflow_id = arguments["workflow_id"]
        
        # Fetch workflow to get its name
        workflow = await self.deps.client.get_workflow(workflow_id)
        self.deps.state_manager.set_current_workflow(workflow['id'], workflow['name'])
        self.deps.state_manager.log_action("set_active_workflow", {
            "workflow_id": workflow_id,
            "workflow_name": workflow['name']
        })
        
        result = f"✅ Set active workflow: **{workflow['name']}** (`{workflow['id']}`)\n\n"
        result += "You can now reference this workflow as the 'current workflow' in future prompts."
        
        return [TextContent(type="text", text=result)]
    
    async def get_active_workflow(self, arguments: dict) -> list[TextContent]:
        """Get the currently active workflow"""
        current = self.deps.state_manager.get_current_workflow()
        
        if not current:
            return [TextContent(
                type="text",
                text="No active workflow set. Use `set_active_workflow` to set one."
            )]
        
        result = f"# Active Workflow\n\n"
        result += f"**Name:** {current['name']}\n"
        result += f"**ID:** `{current['id']}`\n"
        
        return [TextContent(type="text", text=result)]
    
    async def get_recent_workflows(self, arguments: dict) -> list[TextContent]:
        """Get recently accessed workflows"""
        recent = self.deps.state_manager.get_recent_workflows()
        
        if not recent:
            return [TextContent(
                type="text",
                text="No recent workflows. Start working with workflows to see them here."
            )]
        
        result = f"# Recent Workflows ({len(recent)})\n\n"
        for wf in recent:
            result += f"- **{wf['name']}** (`{wf['id']}`)\n"
            result+= f"  Last accessed: {wf['accessed_at']}\n\n"
        
        return [TextContent(type="text", text=result)]
    
    async def get_session_history(self, arguments: dict) -> list[TextContent]:
        """Get session action history"""
        limit = arguments.get("limit", 10)
        history = self.deps.state_manager.get_session_history(limit)
        
        if not history:
            return [TextContent(
                type="text",
                text="No session history yet. Actions will be logged here as you use the tools."
            )]
        
        result = f"# Session History (Last {len(history)} actions)\n\n"
        for entry in reversed(history):
            result += f"**{entry['timestamp']}**\n"
            result += f"- Action: `{entry['action']}`\n"
            if entry.get('details'):
                details_str = ", ".join([f"{k}={v}" for k, v in entry['details'].items()])
                result += f"- Details: {details_str}\n"
            result += "\n"
        
        return [TextContent(type="text", text=result)]
    
    async def clear_session_state(self, arguments: dict) -> list[TextContent]:
        """Clear the session state"""
        self.deps.state_manager.clear_state()
        
        result = "✅ Session state cleared!\n\n"
        result += "All session data (active workflow, recent workflows, history) has been reset."
        
        return [TextContent(type="text", text=result)]
