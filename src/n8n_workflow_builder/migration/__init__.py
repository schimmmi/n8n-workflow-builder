"""
Migration Engine for n8n Workflow Builder

Automatically checks and updates workflows for node compatibility
when n8n APIs change.
"""

from .version_checker import NodeVersionChecker, CompatibilityResult
from .migration_engine import MigrationEngine, MigrationRule
from .migration_rules import MIGRATION_RULES
from .updater import WorkflowUpdater
from .reporter import MigrationReporter

__all__ = [
    "NodeVersionChecker",
    "CompatibilityResult",
    "MigrationEngine",
    "MigrationRule",
    "MIGRATION_RULES",
    "WorkflowUpdater",
    "MigrationReporter",
]
