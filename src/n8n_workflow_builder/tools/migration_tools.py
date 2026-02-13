#!/usr/bin/env python3
"""
Migration Tool Handlers
Handles workflow migration, compatibility checking, and version updates
"""
from typing import Any, TYPE_CHECKING

from mcp.types import TextContent

from .base import BaseTool, ToolError

if TYPE_CHECKING:
    from ..dependencies import Dependencies


class MigrationTools(BaseTool):
    """Handler for workflow migration and compatibility tools"""
    
    async def handle(self, name: str, arguments: dict) -> list[TextContent]:
        """Route migration tool calls to appropriate handler methods
        
        Args:
            name: Tool name
            arguments: Tool arguments
            
        Returns:
            List of TextContent responses
        """
        handlers = {
            "migrate_workflow": self.migrate_workflow,
            "get_migration_preview": self.get_migration_preview,
            "batch_check_compatibility": self.batch_check_compatibility,
        }
        
        handler = handlers.get(name)
        if not handler:
            raise ToolError("UNKNOWN_TOOL", f"Tool '{name}' not found in migration tools")
        
        return await handler(arguments)
    
    async def migrate_workflow(self, arguments: dict) -> list[TextContent]:
        """Migrate a workflow to latest version"""
        workflow_id = arguments["workflow_id"]
        dry_run = arguments.get("dry_run", False)
        target_version = arguments.get("target_version")
        
        workflow = await self.deps.client.get_workflow(workflow_id)
        
        # Access workflow updater and migration reporter from deps
        workflow_updater = self.deps.workflow_updater
        migration_reporter = self.deps.migration_reporter
        
        # Check compatibility before migration
        before_result = workflow_updater.version_checker.check_workflow_compatibility(workflow)
        
        # Perform migration
        updated_workflow, after_result, migration_log = workflow_updater.check_and_update(
            workflow,
            auto_migrate=True,
            dry_run=dry_run
        )
        
        # If not dry run, update in n8n
        if not dry_run and migration_log:
            updated_workflow = await self.deps.client.update_workflow(workflow_id, updated_workflow)
        
        # Generate report
        report = migration_reporter.generate_migration_report(
            updated_workflow,
            migration_log if isinstance(migration_log, list) else [],
            before_result,
            after_result
        )
        
        return [TextContent(type="text", text=report)]
    
    async def get_migration_preview(self, arguments: dict) -> list[TextContent]:
        """Get preview of workflow migration without applying changes"""
        workflow_id = arguments["workflow_id"]
        workflow = await self.deps.client.get_workflow(workflow_id)
        
        workflow_updater = self.deps.workflow_updater
        
        preview = workflow_updater.get_update_preview(workflow)
        summary = workflow_updater.get_migration_summary(workflow)
        
        return [TextContent(type="text", text=summary)]
    
    async def batch_check_compatibility(self, arguments: dict) -> list[TextContent]:
        """Check compatibility for multiple workflows"""
        workflow_ids = arguments.get("workflow_ids")
        
        # If no IDs provided, get all workflows
        if not workflow_ids:
            workflows = await self.deps.client.get_workflows()
            workflow_ids = [w["id"] for w in workflows]
        
        # Fetch workflows
        workflows = []
        for wf_id in workflow_ids:
            try:
                wf = await self.deps.client.get_workflow(wf_id)
                workflows.append(wf)
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"Failed to fetch workflow {wf_id}: {e}")
        
        # Check compatibility
        workflow_updater = self.deps.workflow_updater
        migration_reporter = self.deps.migration_reporter
        
        results = []
        for workflow in workflows:
            compatibility = workflow_updater.version_checker.check_workflow_compatibility(workflow)
            results.append((workflow, compatibility, []))
        
        # Generate batch report
        report = migration_reporter.generate_batch_report(results)
        
        return [TextContent(type="text", text=report)]
