"""n8n Workflow Builder MCP Server"""

__version__ = "1.0.0"

from .server import create_n8n_server, N8nClient, WorkflowBuilder

__all__ = ["create_n8n_server", "N8nClient", "WorkflowBuilder"]
