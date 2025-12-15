"""Entry point for running the n8n-workflow-builder MCP server."""
import asyncio
from .server import main

if __name__ == "__main__":
    asyncio.run(main())
