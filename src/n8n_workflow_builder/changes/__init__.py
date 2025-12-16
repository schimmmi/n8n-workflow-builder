"""
Change Simulation & Approval System - Terraform-style workflow changes

This module provides comprehensive change management for n8n workflows:
- Dry-run simulation (preview changes before applying)
- Workflow diff engine (old vs new comparison)
- Impact analysis (what will be affected)
- Approval workflow (review and approve changes)
- Change history tracking

Like "terraform plan" but for n8n workflows.
"""

from .diff_engine import WorkflowDiffEngine
from .impact_analyzer import ChangeImpactAnalyzer
from .dry_run import DryRunSimulator
from .approval import ApprovalWorkflow, ChangeRequest
from .formatter import ChangeFormatter

__all__ = [
    "WorkflowDiffEngine",
    "ChangeImpactAnalyzer",
    "DryRunSimulator",
    "ApprovalWorkflow",
    "ChangeRequest",
    "ChangeFormatter",
]
