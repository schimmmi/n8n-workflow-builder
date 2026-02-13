"""Documentation and GitHub Integration Tools

This module handles:
- n8n documentation retrieval and search
- GitHub template discovery and repository import
"""

from typing import Any
from mcp.types import TextContent

from .base import BaseTool, ToolError
from ..dependencies import Dependencies


class DocumentationTools(BaseTool):
    """Handler for documentation and GitHub integration tools"""
    
    async def handle(self, name: str, arguments: dict) -> list[TextContent]:
        """Route documentation/GitHub tool calls to appropriate handler methods
        
        Args:
            name: Tool name
            arguments: Tool arguments
            
        Returns:
            List of TextContent responses
        """
        handlers = {
            "get_node_documentation": self.get_node_documentation,
            "search_n8n_docs": self.search_n8n_docs,
            "discover_github_templates": self.discover_github_templates,
            "import_github_repo": self.import_github_repo,
        }
        
        handler = handlers.get(name)
        if not handler:
            raise ToolError("UNKNOWN_TOOL", f"Tool '{name}' not found in documentation tools")
        
        return await handler(arguments)
    
    async def get_node_documentation(self, arguments: dict) -> list[TextContent]:
        """Get documentation for a specific node type
        
        Args:
            arguments: {"node_type": str}
            
        Returns:
            Documentation URL and quick links
        """
        node_type = arguments["node_type"]
        n8n_docs = self.deps.n8n_docs
        
        # Get documentation URL
        doc_url = n8n_docs.get_node_doc_url(node_type)
        
        if not doc_url:
            # Search for similar nodes
            search_results = n8n_docs.search_documentation(node_type)
            
            if not search_results:
                return [TextContent(
                    type="text",
                    text=f"❌ Documentation not found for node type: `{node_type}`\n\n"
                         f"💡 Tips:\n"
                         f"- Try using the full node type (e.g., 'n8n-nodes-base.code')\n"
                         f"- Use `search_n8n_docs` to find related documentation\n"
                         f"- Check the official docs: https://docs.n8n.io"
                )]
            
            # Show similar results
            result = f"❌ Exact documentation not found for: `{node_type}`\n\n"
            result += f"📚 **Similar Documentation Found:**\n\n"
            
            for match in search_results[:5]:
                result += f"### {match['name']}\n"
                result += f"- **Category:** {match['category']}\n"
                result += f"- **URL:** {match['url']}\n\n"
            
            return [TextContent(type="text", text=result)]
        
        # Fetch documentation using WebFetch
        result = f"# 📖 n8n Documentation: {node_type}\n\n"
        result += f"**Official Docs:** {doc_url}\n\n"
        
        # Add relevant sections based on node type
        result += f"## Quick Links\n\n"
        
        node_lower = node_type.lower()
        if 'http' in node_lower or 'webhook' in node_lower:
            result += f"- [Webhook Guide]({n8n_docs.get_section_url('webhooks')})\n"
            result += f"- [HTTP Request Examples]({n8n_docs.get_section_url('core-nodes')})\n"
        
        if 'code' in node_lower:
            result += f"- [Code Node Guide]({n8n_docs.get_section_url('code-node')})\n"
            result += f"- [JavaScript Expressions]({n8n_docs.get_section_url('expressions')})\n"
        
        if 'database' in node_lower or 'postgres' in node_lower or 'mysql' in node_lower:
            result += f"- [Database Setup Guide]({n8n_docs.get_section_url('integrations')})\n"
        
        result += f"\n💡 **Tip:** Use `search_n8n_docs` to find more related documentation.\n"
        
        return [TextContent(type="text", text=result)]
    
    async def search_n8n_docs(self, arguments: dict) -> list[TextContent]:
        """Search n8n documentation
        
        Args:
            arguments: {"query": str}
            
        Returns:
            Search results grouped by category
        """
        query = arguments["query"]
        n8n_docs = self.deps.n8n_docs
        
        # Search documentation
        results = n8n_docs.search_documentation(query)
        
        if not results:
            return [TextContent(
                type="text",
                text=f"❌ No documentation found for: '{query}'\n\n"
                     f"💡 Tips:\n"
                     f"- Try different keywords\n"
                     f"- Check common terms (webhook, code, http, trigger, etc.)\n"
                     f"- Visit https://docs.n8n.io for full documentation"
            )]
        
        result = f"# 🔍 n8n Documentation Search: '{query}'\n\n"
        result += f"**Found:** {len(results)} results\n\n"
        
        # Group by category
        by_category = {}
        for item in results:
            category = item['category']
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(item)
        
        # Display by category
        for category, items in sorted(by_category.items()):
            result += f"## {category}\n\n"
            for item in items:
                result += f"### {item['name']}\n"
                result += f"- **URL:** {item['url']}\n"
                result += f"- **Type:** {item['type']}\n\n"
        
        result += f"💡 **Tip:** Use `get_node_documentation` to fetch full documentation for a specific node.\n"
        
        return [TextContent(type="text", text=result)]
    
    async def discover_github_templates(self, arguments: dict) -> list[TextContent]:
        """Discover n8n workflow templates from GitHub
        
        Args:
            arguments: {"query": str (optional), "limit": int (optional)}
            
        Returns:
            List of discovered GitHub repositories
        """
        query = arguments.get("query", "n8n workflows")
        limit = arguments.get("limit", 10)
        template_manager = self.deps.template_manager
        
        repos = await template_manager.discover_github_templates(query=query, limit=limit)
        
        result = f"# 🐙 GitHub Repository Discovery\n\n"
        result += f"**Search Query:** {query}\n"
        result += f"**Repositories Found:** {len(repos)}\n\n"
        
        if repos:
            for i, repo in enumerate(repos, 1):
                result += f"## {i}. {repo['full_name']}\n"
                result += f"⭐ **Stars:** {repo['stars']}\n"
                if repo.get('description'):
                    result += f"📝 **Description:** {repo['description']}\n"
                result += f"🔗 **URL:** {repo['url']}\n"
                if repo.get('topics'):
                    result += f"🏷️  **Topics:** {', '.join(repo['topics'][:5])}\n"
                if repo.get('language'):
                    result += f"💻 **Language:** {repo['language']}\n"
                result += f"🕐 **Last Updated:** {repo.get('updated_at', 'Unknown')}\n"
                result += "\n"
        else:
            result += "⚠️ No repositories found.\n"
            result += "This might be due to GitHub API rate limiting.\n"
            result += "Consider setting GITHUB_TOKEN environment variable.\n"
        
        return [TextContent(type="text", text=result)]
    
    async def import_github_repo(self, arguments: dict) -> list[TextContent]:
        """Import n8n templates from a GitHub repository
        
        Args:
            arguments: {"repo_full_name": str, "add_to_sync": bool (optional)}
            
        Returns:
            Import results and imported template list
        """
        repo_full_name = arguments["repo_full_name"]
        add_to_sync = arguments.get("add_to_sync", True)
        template_manager = self.deps.template_manager
        
        result_data = await template_manager.import_github_repo(
            repo_full_name=repo_full_name,
            add_to_sync=add_to_sync
        )
        
        result = f"# 📦 GitHub Repository Import\n\n"
        result += f"**Repository:** {repo_full_name}\n"
        
        if result_data.get('success'):
            result += f"**Status:** ✅ Success\n"
            result += f"**Templates Imported:** {result_data['templates_imported']}\n"
            result += f"**Added to Sync List:** {'Yes' if add_to_sync else 'No'}\n\n"
            
            if result_data['templates_imported'] > 0:
                result += "## Imported Templates:\n\n"
                for template in result_data.get('templates', [])[:10]:
                    result += f"### {template['name']}\n"
                    result += f"- **ID:** `{template['id']}`\n"
                    result += f"- **Category:** {template.get('category', 'unknown')}\n"
                    result += f"- **Nodes:** {template.get('node_count', 0)}\n"
                    result += f"- **Complexity:** {template.get('complexity', 'unknown')}\n"
                    if template.get('source_url'):
                        result += f"- **Source:** {template['source_url']}\n"
                    result += "\n"
                
                if result_data['templates_imported'] > 10:
                    result += f"... and {result_data['templates_imported'] - 10} more templates\n"
            else:
                result += "ℹ️ No workflow files found in this repository.\n"
                result += "The repository might not contain n8n workflows in standard paths.\n"
        else:
            result += f"**Status:** ❌ Failed\n"
            result += f"**Error:** {result_data.get('error', 'Unknown error')}\n"
        
        return [TextContent(type="text", text=result)]
