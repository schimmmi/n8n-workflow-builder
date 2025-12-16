"""
Workflow Explainer - Main coordinator for explainability layer

Orchestrates all explainability components to generate comprehensive
workflow documentation and analysis.
"""

from typing import Dict, List, Optional
from .purpose_analyzer import WorkflowPurposeAnalyzer
from .data_flow_tracer import DataFlowTracer
from .dependency_mapper import DependencyMapper
from .risk_analyzer import RiskAnalyzer


class WorkflowExplainer:
    """Main coordinator for workflow explainability"""

    @staticmethod
    def explain_workflow(
        workflow: Dict,
        all_workflows: Optional[List[Dict]] = None,
        semantic_analysis: Optional[Dict] = None,
        drift_analysis: Optional[Dict] = None,
        execution_history: Optional[List[Dict]] = None,
        intent_metadata: Optional[Dict] = None,
    ) -> Dict:
        """
        Generate comprehensive workflow explanation

        Args:
            workflow: The workflow to explain
            all_workflows: Optional list of all workflows (for cross-workflow dependencies)
            semantic_analysis: Optional semantic analysis results
            drift_analysis: Optional drift detection results
            execution_history: Optional execution history

        Returns:
            Complete explainability report with:
            - Purpose analysis
            - Data flow analysis
            - Dependency mapping
            - Risk assessment
        """
        # Analyze purpose
        purpose_analysis = WorkflowPurposeAnalyzer.analyze_purpose(workflow)

        # Trace data flow
        data_flow_analysis = DataFlowTracer.trace_data_flow(workflow)

        # Map dependencies
        dependency_analysis = DependencyMapper.map_dependencies(workflow, all_workflows)

        # Analyze risks
        risk_analysis = RiskAnalyzer.analyze_risks(
            workflow,
            semantic_analysis=semantic_analysis,
            drift_analysis=drift_analysis,
            execution_history=execution_history,
            dependency_analysis=dependency_analysis,
            intent_metadata=intent_metadata,
        )

        # Generate executive summary
        executive_summary = WorkflowExplainer._generate_executive_summary(
            workflow,
            purpose_analysis,
            data_flow_analysis,
            dependency_analysis,
            risk_analysis,
        )

        return {
            "workflow_id": workflow.get("id", ""),
            "workflow_name": workflow.get("name", ""),
            "executive_summary": executive_summary,
            "purpose": purpose_analysis,
            "data_flow": data_flow_analysis,
            "dependencies": dependency_analysis,
            "risks": risk_analysis,
            "metadata": {
                "node_count": len(workflow.get("nodes", [])),
                "active": workflow.get("active", False),
                "tags": workflow.get("tags", []),
            },
        }

    @staticmethod
    def _generate_executive_summary(
        workflow: Dict,
        purpose_analysis: Dict,
        data_flow_analysis: Dict,
        dependency_analysis: Dict,
        risk_analysis: Dict,
    ) -> str:
        """Generate executive summary for the workflow"""
        parts = []

        # Workflow identification
        name = workflow.get("name", "Unnamed Workflow")
        parts.append(f"Workflow: {name}")

        # Purpose
        parts.append(f"Purpose: {purpose_analysis.get('primary_purpose', 'Unknown')}")

        # Business domain and type
        domain = purpose_analysis.get("business_domain", "general")
        wf_type = purpose_analysis.get("workflow_type", "manual")
        parts.append(f"Domain: {domain}, Type: {wf_type}")

        # Data flow summary
        parts.append(data_flow_analysis.get("summary", "Data flow unclear"))

        # Dependency summary
        parts.append(dependency_analysis.get("summary", "No dependencies identified"))

        # Risk summary
        risk_level = risk_analysis.get("risk_level", "low")
        parts.append(f"Risk Level: {risk_level.upper()}")

        return " | ".join(parts)

    @staticmethod
    def get_workflow_purpose(workflow: Dict) -> Dict:
        """Quick purpose analysis only"""
        return WorkflowPurposeAnalyzer.analyze_purpose(workflow)

    @staticmethod
    def trace_data_flow(workflow: Dict) -> Dict:
        """Quick data flow analysis only"""
        return DataFlowTracer.trace_data_flow(workflow)

    @staticmethod
    def map_dependencies(
        workflow: Dict,
        all_workflows: Optional[List[Dict]] = None
    ) -> Dict:
        """Quick dependency mapping only"""
        return DependencyMapper.map_dependencies(workflow, all_workflows)

    @staticmethod
    def analyze_risks(
        workflow: Dict,
        semantic_analysis: Optional[Dict] = None,
        drift_analysis: Optional[Dict] = None,
        execution_history: Optional[List[Dict]] = None,
        intent_metadata: Optional[Dict] = None,
    ) -> Dict:
        """Quick risk analysis only"""
        # Need dependency analysis for comprehensive risk assessment
        dependency_analysis = DependencyMapper.map_dependencies(workflow)

        return RiskAnalyzer.analyze_risks(
            workflow,
            semantic_analysis=semantic_analysis,
            drift_analysis=drift_analysis,
            execution_history=execution_history,
            dependency_analysis=dependency_analysis,
            intent_metadata=intent_metadata,
        )
