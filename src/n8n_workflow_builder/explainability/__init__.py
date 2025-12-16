"""
Explainability Layer - Automatic workflow documentation and analysis

This module provides automatic generation of human-readable and audit-ready
documentation for n8n workflows, including:
- Purpose and business domain
- Data flow tracing
- Dependency mapping (internal and external)
- Risk analysis
- Multi-format export (Markdown, JSON, Plain Text)
"""

from .explainer import WorkflowExplainer
from .purpose_analyzer import WorkflowPurposeAnalyzer
from .data_flow_tracer import DataFlowTracer
from .dependency_mapper import DependencyMapper
from .risk_analyzer import RiskAnalyzer
from .formatter import ExplainabilityFormatter

__all__ = [
    "WorkflowExplainer",
    "WorkflowPurposeAnalyzer",
    "DataFlowTracer",
    "DependencyMapper",
    "RiskAnalyzer",
    "ExplainabilityFormatter",
]
