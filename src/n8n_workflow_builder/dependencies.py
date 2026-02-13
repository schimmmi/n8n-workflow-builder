#!/usr/bin/env python3
"""
Dependency Injection Container for MCP Server
Simplified version that wraps existing server dependencies
"""
from dataclasses import dataclass
from typing import Any


@dataclass
class Dependencies:
    """Centralized dependency container for MCP server
    
    This is a lightweight wrapper around existing server dependencies.
    Instead of creating dependencies, it accepts already-instantiated ones.
    """
    
    # Core services
    client: Any
    state_manager: Any
    
    # Builders & Validators
    workflow_builder: Any
    workflow_validator: Any
    
    # Analyzers
    semantic_analyzer: Any = None
    ai_feedback_analyzer: Any = None
    security_auditor: Any = None
    
    # Templates & Intent
    template_manager: Any = None
    template_engine: Any = None
    template_registry: Any = None
    template_adapter: Any = None
    provenance_tracker: Any = None
    intent_manager: Any = None
    
    # Migration & Drift
    workflow_updater: Any = None
    migration_reporter: Any = None
    
    # Discovery
    node_discovery: Any = None
    node_recommender: Any = None
    
    # Documentation
    n8n_docs: Any = None
    
    # Change Management
    approval_workflow: Any = None
    
    # RBAC
    rbac_manager: Any = None
    
    @classmethod
    def from_server(cls, **kwargs) -> 'Dependencies':
        """Create Dependencies from already-instantiated server components
        
        This allows gradual migration from the old structure to DI.
        Pass in any components that exist, others will be None.
        
        Args:
            **kwargs: Component instances (client, state_manager, etc.)
            
        Returns:
            Dependencies instance
        """
        return cls(**kwargs)
    
    async def close(self):
        """Cleanup resources when server shuts down"""
        if hasattr(self.client, 'close'):
            await self.client.close()

