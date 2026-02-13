"""Advanced Template Management Tools

This module provides advanced template functionality including:
- Template sync, stats, and caching
- Intent-based template search
- Template adaptation and customization  
- Template provenance and requirements analysis
- Workflow compatibility checking
"""

from mcp.types import TextContent
import json

from .base import BaseTool, ToolError
from ..dependencies import Dependencies

class AdvancedTemplateTools(BaseTool):
    """Handler for advanced template management operations"""
    
    async def handle(self, name: str, arguments: dict) -> list[TextContent]:
        """Route advanced template tool calls to appropriate handler methods
        
        Args:
            name: Tool name
            arguments: Tool arguments
            
        Returns:
            List of TextContent responses
        """
        handlers = {
            "sync_templates": self.sync_templates,
            "get_template_stats": self.get_template_stats,
            "get_popular_templates": self.get_popular_templates,
            "get_recent_templates": self.get_recent_templates,
            "get_template_by_id": self.get_template_by_id,
            "clear_template_cache": self.clear_template_cache,
            "find_templates_by_intent": self.find_templates_by_intent,
            "extract_template_intent": self.extract_template_intent,
            "adapt_template": self.adapt_template,
            "get_template_provenance": self.get_template_provenance,
            "get_template_requirements": self.get_template_requirements,
            "check_workflow_compatibility": self.check_workflow_compatibility,
        }
        
        handler = handlers.get(name)
        if not handler:
            raise ToolError("UNKNOWN_TOOL", f"Tool '{name}' not found in advanced template tools")
        
        return await handler(arguments)
    
    async def sync_templates(self, arguments: dict) -> list[TextContent]:
        """Sync templates from configured sources
        
        Args:
            arguments: {"source": str (optional), "force": bool (optional)}
            
        Returns:
            Sync results and statistics
        """
        source = arguments.get("source", "all")
        force = arguments.get("force", False)
        template_manager = self.deps.template_manager
        
        result_data = await template_manager.sync_templates(source=source, force=force)
        
        result = "# 🔄 Template Sync Results\n\n"
        result += f"**Sources Synced:** {', '.join(result_data['synced_sources']) or 'None'}\n"
        result += f"**Total Templates:** {result_data['total_templates']}\n\n"
        
        if result_data['errors']:
            result += "## ⚠️ Errors:\n"
            for error in result_data['errors']:
                result += f"- {error}\n"
        else:
            result += "✅ Sync completed successfully!\n"
        
        return [TextContent(type="text", text=result)]
    
    async def get_template_stats(self, arguments: dict) -> list[TextContent]:
        """Get template library statistics
        
        Args:
            arguments: {}
            
        Returns:
            Template statistics by source, category, complexity
        """
        template_manager = self.deps.template_manager
        stats = template_manager.get_template_stats()
        
        result = "# 📊 Template Statistics\n\n"
        result += f"**Total Templates:** {stats['total_templates']}\n\n"
        
        if stats['by_source']:
            result += "## By Source\n"
            for source, count in sorted(stats['by_source'].items(), key=lambda x: -x[1]):
                result += f"- **{source}**: {count} templates\n"
            result += "\n"
        
        if stats['by_category']:
            result += "## By Category\n"
            for category, count in sorted(stats['by_category'].items(), key=lambda x: -x[1]):
                result += f"- **{category}**: {count} templates\n"
            result += "\n"
        
        if stats['by_complexity']:
            result += "## By Complexity\n"
            complexity_order = {'beginner': 1, 'intermediate': 2, 'advanced': 3}
            for complexity, count in sorted(stats['by_complexity'].items(), key=lambda x: complexity_order.get(x[0], 99)):
                result += f"- **{complexity}**: {count} templates\n"
            result += "\n"
        
        return [TextContent(type="text", text=result)]
    
    async def get_popular_templates(self, arguments: dict) -> list[TextContent]:
        """Get most popular templates
        
        Args:
            arguments: {"limit": int (optional)}
            
        Returns:
            List of popular templates
        """
        limit = arguments.get("limit", 10)
        template_manager = self.deps.template_manager
        
        templates = await template_manager.get_popular_templates(limit=limit)
        
        result = f"# ⭐ Top {limit} Popular Templates\n\n"
        
        for i, template in enumerate(templates, 1):
            result += f"## {i}. {template['name']}\n"
            result += f"**ID:** `{template['id']}`\n"
            result += f"**Category:** {template['category']}\n"
            result += f"**Complexity:** {template['complexity']}\n"
            result += f"**Usage:** {template.get('usage_count', 0)} times\n"
            result += f"\n{template['description'][:150]}...\n\n"
        
        return [TextContent(type="text", text=result)]
    
    async def get_recent_templates(self, arguments: dict) -> list[TextContent]:
        """Get recently added templates
        
        Args:
            arguments: {"limit": int (optional)}
            
        Returns:
            List of recent templates
        """
        limit = arguments.get("limit", 10)
        template_manager = self.deps.template_manager
        
        templates = await template_manager.get_recent_templates(limit=limit)
        
        result = f"# 🆕 {limit} Most Recent Templates\n\n"
        
        for i, template in enumerate(templates, 1):
            result += f"## {i}. {template['name']}\n"
            result += f"**ID:** `{template['id']}`\n"
            result += f"**Added:** {template.get('created_at', 'Unknown')}\n"
            result += f"**Category:** {template['category']}\n"
            result += f"\n{template['description'][:150]}...\n\n"
        
        return [TextContent(type="text", text=result)]
    
    async def get_template_by_id(self, arguments: dict) -> list[TextContent]:
        """Get detailed template information
        
        Args:
            arguments: {"template_id": str}
            
        Returns:
            Complete template details
        """
        template_id = arguments["template_id"]
        template_manager = self.deps.template_manager
        
        template = await template_manager.get_template_by_id(template_id)
        
        if not template:
            return [TextContent(type="text", text=f"Template not found: {template_id}")]
        
        result = f"# 📄 Template: {template['name']}\n\n"
        result += f"**ID:** `{template['id']}`\n"
        result += f"**Source:** {template['source']}\n"
        result += f"**Category:** {template.get('category', 'unknown')}\n"
        result += f"**Complexity:** {template.get('complexity', 'intermediate')}\n"
        result += f"**Node Count:** {template.get('node_count', 0)}\n"
        result += f"**Setup Time:** {template.get('estimated_setup_time', 'Unknown')}\n"
        result += f"**Trigger Type:** {template.get('trigger_type', 'N/A')}\n"
        result += f"**Author:** {template.get('author', 'Unknown')}\n\n"
        
        if template.get('tags'):
            result += f"**Tags:** {', '.join(template['tags'])}\n\n"
        
        result += f"## Description\n{template['description']}\n\n"
        
        if template.get('nodes'):
            result += f"## Nodes ({len(template['nodes'])})\n"
            for node in template['nodes'][:10]:
                node_name = node.get('name', 'Unknown')
                node_type = node.get('type', 'Unknown')
                result += f"- {node_name} ({node_type})\n"
            if len(template['nodes']) > 10:
                result += f"... and {len(template['nodes']) - 10} more\n"
            result += "\n"
        
        if template.get('has_error_handling'):
            result += "✅ Includes error handling\n"
        if template.get('has_documentation'):
            result += "✅ Well documented\n"
        
        if template.get('source_url'):
            result += f"\n[View Original]({template['source_url']})\n"
        
        return [TextContent(type="text", text=result)]
    
    async def clear_template_cache(self, arguments: dict) -> list[TextContent]:
        """Clear template cache
        
        Args:
            arguments: {"source": str (optional)}
            
        Returns:
            Cache clear confirmation
        """
        source = arguments.get("source", "all")
        template_manager = self.deps.template_manager
        
        result_data = template_manager.clear_cache(source=source)
        
        result = f"# 🗑️ Template Cache Cleared\n\n"
        result += f"**Cleared:** {result_data['cleared']}\n\n"
        result += "✅ Cache has been cleared. Use `sync_templates` to re-download.\n"
        
        return [TextContent(type="text", text=result)]
    
    async def find_templates_by_intent(self, arguments: dict) -> list[TextContent]:
        """Find templates matching a natural language intent
        
        Args:
            arguments: {"description": str, "top_k": int (optional)}
            
        Returns:
            Ranked template matches with scores
        """
        from ..templates.sources.base import TemplateMetadata
        from ..templates.matcher import TemplateMatcher
        from ..templates.sources.registry import template_registry
        from ..templates.provenance import provenance_tracker
        
        description = arguments["description"]
        top_k = arguments.get("top_k", 5)
        
        # Fetch all templates
        all_templates = await template_registry.fetch_all_templates()
        
        # Create matcher and find matches
        matcher = TemplateMatcher(all_templates)
        matches = matcher.match(description, top_k=top_k)
        
        # Format results
        result = f"# Template Suggestions for: \"{description}\"\n\n"
        result += f"Found {len(matches)} matches:\n\n"
        
        for i, (template, score, reason) in enumerate(matches, 1):
            result += f"## {i}. {template.name} ({int(score * 100)}% match)\n\n"
            result += f"**Why**: {reason}\n\n"
            
            # Template details
            result += f"- **Category**: {template.category}\n"
            result += f"- **Complexity**: {template.complexity}\n"
            result += f"- **Source**: {template.source}\n"
            
            if template.trigger_type:
                result += f"- **Trigger**: {template.trigger_type}\n"
            
            if template.data_flow:
                result += f"- **Data Flow**: {template.data_flow}\n"
            
            if template.external_systems:
                result += f"- **External Systems**: {', '.join(template.external_systems[:3])}\n"
            
            result += f"- **Node Count**: {template.node_count}\n"
            result += f"- **Setup Time**: ~{template.estimated_setup_time}\n"
            
            if template.description:
                result += f"\n**Description**: {template.description}\n"
            
            result += "\n"
            
            # Track usage
            provenance_tracker.record_usage(template.id)
        
        return [TextContent(type="text", text=result)]
    
    async def extract_template_intent(self, arguments: dict) -> list[TextContent]:
        """Extract and analyze template intent
        
        Args:
            arguments: {"template_id": str}
            
        Returns:
            Template intent analysis
        """
        from ..templates.sources.base import TemplateMetadata
        from ..templates.sources.registry import template_registry
        from ..templates.intent_extractor import TemplateIntentExtractor
        from ..server import WORKFLOW_TEMPLATES
        
        template_id = arguments["template_id"]
        
        # Get template
        template = await template_registry.get_template(template_id)
        
        if not template:
            # Try from old template engine
            if template_id in WORKFLOW_TEMPLATES:
                template_dict = WORKFLOW_TEMPLATES[template_id]
                
                # Convert node names to full node objects
                full_nodes = []
                for node_info in template_dict["nodes"]:
                    full_nodes.append({
                        "name": node_info["name"],
                        "type": node_info["type"],
                        "position": [0, 0],
                        "parameters": {}
                    })
                
                template = TemplateMetadata(
                    id=template_id,
                    source="n8n_official",
                    name=template_dict["name"],
                    description=template_dict["description"],
                    category=template_dict["category"],
                    tags=template_dict["tags"],
                    n8n_version=">=1.0",
                    template_version="1.0.0",
                    nodes=full_nodes,
                    connections={},
                    settings={},
                    complexity=template_dict.get("complexity", template_dict.get("difficulty", "intermediate")),
                    node_count=len(full_nodes),
                    estimated_setup_time=template_dict["estimated_time"]
                )
        
        if not template:
            return [TextContent(type="text", text=f"Template {template_id} not found")]
        
        # Extract intent
        intent_data = TemplateIntentExtractor.extract_intent(template)
        
        # Format result
        result = f"# Template Intent Analysis: {template.name}\n\n"
        
        result += f"## 🎯 Purpose\n{intent_data['intent']}\n\n"
        
        result += f"## 📋 Classification\n"
        result += f"- **Type**: {intent_data['purpose']}\n"
        result += f"- **Trigger**: {intent_data['trigger_type'] or 'N/A'}\n"
        result += f"- **Data Flow**: {intent_data['data_flow']}\n\n"
        
        if intent_data['external_systems']:
            result += f"## 🔗 External Systems\n"
            for system in intent_data['external_systems']:
                result += f"- {system}\n"
            result += "\n"
        
        if intent_data['assumptions']:
            result += f"## 💭 Assumptions\n"
            for assumption in intent_data['assumptions']:
                result += f"- {assumption}\n"
            result += "\n"
        
        if intent_data['risks']:
            result += f"## ⚠️  Risks\n"
            for risk in intent_data['risks']:
                result += f"- {risk}\n"
            result += "\n"
        
        result += f"## 📊 Template Metadata\n"
        result += f"- **Source**: {template.source}\n"
        result += f"- **Category**: {template.category}\n"
        result += f"- **Complexity**: {template.complexity}\n"
        result += f"- **Node Count**: {template.node_count}\n"
        result += f"- **Error Handling**: {'✅ Yes' if template.has_error_handling else '❌ No'}\n"
        result += f"- **Documentation**: {'✅ Yes' if template.has_documentation else '❌ No'}\n"
        
        return [TextContent(type="text", text=result)]
    
    async def adapt_template(self, arguments: dict) -> list[TextContent]:
        """Adapt template with customizations
        
        Args:
            arguments: {
                "template_id": str,
                "replacements": dict (optional),
                "add_error_handling": bool (optional),
                "modernize_nodes": bool (optional)
            }
            
        Returns:
            Adapted workflow JSON
        """
        from ..templates.sources.registry import template_registry
        from ..templates.adapter import template_adapter
        from ..templates.provenance import provenance_tracker
        
        template_id = arguments["template_id"]
        replacements = arguments.get("replacements", {})
        add_error_handling = arguments.get("add_error_handling", True)
        modernize_nodes = arguments.get("modernize_nodes", True)
        
        # Get template
        template = await template_registry.get_template(template_id)
        
        if not template:
            return [TextContent(type="text", text=f"Template {template_id} not found")]
        
        # Adapt template
        adapted_workflow = template_adapter.adapt_template(
            template,
            replacements=replacements,
            add_error_handling=add_error_handling,
            modernize_nodes=modernize_nodes
        )
        
        # Get adaptation log
        adaptation_log = template_adapter.get_adaptation_log()
        
        # Format result
        result = f"# Template Adapted: {template.name}\n\n"
        
        result += f"## ✅ Adaptation Complete\n\n"
        result += f"**Changes Applied**:\n"
        for log_entry in adaptation_log:
            result += f"- {log_entry}\n"
        result += "\n"
        
        result += f"## 📋 Next Steps\n\n"
        result += f"1. Review the adapted workflow JSON below\n"
        result += f"2. Configure required credentials\n"
        result += f"3. Test in a safe environment\n"
        result += f"4. Deploy to production\n\n"
        
        result += f"## 🔧 Adapted Workflow\n\n"
        result += f"```json\n{json.dumps(adapted_workflow, indent=2)}\n```\n"
        
        # Track adaptation
        provenance_tracker.record_adaptation(template_id, ", ".join(adaptation_log))
        
        return [TextContent(type="text", text=result)]
    
    async def get_template_provenance(self, arguments: dict) -> list[TextContent]:
        """Get template provenance and trust metrics
        
        Args:
            arguments: {"template_id": str}
            
        Returns:
            Provenance tracking information
        """
        from ..templates.sources.registry import template_registry
        from ..templates.provenance import provenance_tracker
        
        template_id = arguments["template_id"]
        
        # Get template
        template = await template_registry.get_template(template_id)
        
        if not template:
            return [TextContent(type="text", text=f"Template {template_id} not found")]
        
        # Get or create provenance record
        record = provenance_tracker.get_record(template_id)
        
        if not record:
            record = provenance_tracker.track_template(
                template_id,
                template.name,
                template.source,
                template.author
            )
        
        # Format result
        result = f"# Template Provenance: {template.name}\n\n"
        
        result += f"## 📊 Trust Metrics\n"
        result += f"- **Overall Trust Score**: {record.overall_trust_score:.0%}\n"
        result += f"- **Reliability Score**: {record.reliability_score:.0%}\n"
        result += f"- **Security Score**: {record.security_score:.0%}\n"
        result += f"- **Success Rate**: {record.success_rate:.0%} ({record.successful_executions}/{record.total_executions} executions)\n\n"
        
        result += f"## 📈 Usage Statistics\n"
        result += f"- **Total Usage**: {record.usage_count} times\n"
        result += f"- **Deployments**: {record.deployment_count}\n"
        result += f"- **Adaptations**: {record.adaptation_count}\n"
        result += f"- **Last Used**: {record.last_used_at.strftime('%Y-%m-%d %H:%M') if record.last_used_at else 'Never'}\n\n"
        
        result += f"## 🏷️  Source Info\n"
        result += f"- **Source**: {template.source}\n"
        result += f"- **Author**: {template.author or 'Unknown'}\n"
        result += f"- **Created**: {template.created_at.strftime('%Y-%m-%d') if template.created_at else 'Unknown'}\n"
        
        if template.source_url:
            result += f"- **URL**: {template.source_url}\n"
        
        result += "\n"
        
        result += f"## ✅ Quality Indicators\n"
        result += f"- **Error Handling**: {'✅ Yes' if record.has_error_handling else '❌ No'}\n"
        result += f"- **Documentation**: {'✅ Yes' if record.has_documentation else '❌ No'}\n"
        result += f"- **Tests**: {'✅ Yes' if record.has_tests else '❌ No'}\n"
        result += f"- **Best Practices**: {'✅ Yes' if record.uses_best_practices else '❌ No'}\n\n"
        
        if record.rating:
            result += f"## ⭐ User Rating\n"
            result += f"- **Average**: {record.rating:.1f}/5.0 ({record.rating_count} ratings)\n\n"
        
        return [TextContent(type="text", text=result)]
    
    async def get_template_requirements(self, arguments: dict) -> list[TextContent]:
        """Get template deployment requirements
        
        Args:
            arguments: {"template_id": str}
            
        Returns:
            List of placeholders, credentials, and prerequisites
        """
        from ..templates.sources.registry import template_registry
        from ..templates.adapter import template_adapter
        
        template_id = arguments["template_id"]
        
        # Get template
        template = await template_registry.get_template(template_id)
        
        if not template:
            return [TextContent(type="text", text=f"Template {template_id} not found")]
        
        # Get requirements
        placeholders = template_adapter.get_placeholders(template)
        credentials = template_adapter.get_required_credentials(template)
        
        # Format result
        result = f"# Template Requirements: {template.name}\n\n"
        
        if placeholders:
            result += f"## 📝 Placeholders to Fill ({len(placeholders)})\n\n"
            for placeholder in placeholders:
                result += f"### {placeholder['key']}\n"
                result += f"- **Placeholder**: `{placeholder['placeholder']}`\n"
                result += f"- **Node**: {placeholder['node']}\n"
                result += f"- **Required**: {'✅ Yes' if placeholder['required'] else '❌ No'}\n\n"
        else:
            result += f"## ✅ No Placeholders\nThis template is ready to use without placeholder replacement.\n\n"
        
        if credentials:
            result += f"## 🔑 Credentials Needed ({len(credentials)})\n\n"
            for cred in credentials:
                result += f"### {cred['name']}\n"
                result += f"- **Type**: {cred['type']}\n"
                result += f"- **Used by**: {cred['node']}\n"
                result += f"- **Required**: {'✅ Yes' if cred['required'] else '❌ No'}\n\n"
        else:
            result += f"## ✅ No Credentials\nThis template doesn't require credential configuration.\n\n"
        
        if template.external_systems:
            result += f"## 🌐 External Systems ({len(template.external_systems)})\n\n"
            for system in template.external_systems:
                result += f"- {system}\n"
            result += "\n"
        
        result += f"## 📋 Pre-Deployment Checklist\n\n"
        result += f"- [ ] Fill all placeholders ({len(placeholders)} total)\n"
        result += f"- [ ] Configure credentials ({len(credentials)} total)\n"
        result += f"- [ ] Verify access to external systems ({len(template.external_systems or [])} total)\n"
        result += f"- [ ] Test in staging environment\n"
        result += f"- [ ] Review error handling\n"
        result += f"- [ ] Deploy to production\n"
        
        return [TextContent(type="text", text=result)]
    
    async def check_workflow_compatibility(self, arguments: dict) -> list[TextContent]:
        """Check workflow compatibility with current n8n version
        
        Args:
            arguments: {"workflow_id": str}
            
        Returns:
            Compatibility report
        """
        workflow_id = arguments["workflow_id"]
        n8n_client = self.deps.client
        workflow_updater = self.deps.workflow_updater
        migration_reporter = self.deps.migration_reporter
        
        workflow = await n8n_client.get_workflow(workflow_id)
        
        compatibility_result = workflow_updater.version_checker.check_workflow_compatibility(workflow)
        report = migration_reporter.generate_compatibility_report(workflow, compatibility_result)
        
        return [TextContent(type="text", text=report)]
