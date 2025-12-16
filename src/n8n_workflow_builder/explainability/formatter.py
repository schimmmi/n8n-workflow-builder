"""
Explainability Formatter - Multi-format export

Formats explainability reports in:
- Markdown (human-readable, great for docs)
- JSON (machine-readable, perfect for APIs)
- Plain Text (console output, simple)
"""

from typing import Dict, List
import json


class ExplainabilityFormatter:
    """Formats explainability reports in multiple formats"""

    @staticmethod
    def format_as_markdown(explanation: Dict) -> str:
        """Format explanation as Markdown"""
        md_parts = []

        # Header
        workflow_name = explanation.get("workflow_name", "Unknown Workflow")
        md_parts.append(f"# Workflow Explanation: {workflow_name}")
        md_parts.append("")

        # Executive Summary
        md_parts.append("## Executive Summary")
        md_parts.append("")
        md_parts.append(explanation.get("executive_summary", ""))
        md_parts.append("")

        # Metadata
        metadata = explanation.get("metadata", {})
        md_parts.append("## Metadata")
        md_parts.append("")
        md_parts.append(f"- **Workflow ID**: {explanation.get('workflow_id', 'N/A')}")
        md_parts.append(f"- **Node Count**: {metadata.get('node_count', 0)}")
        md_parts.append(f"- **Status**: {'Active' if metadata.get('active') else 'Inactive'}")
        tags = metadata.get('tags', [])
        if tags:
            md_parts.append(f"- **Tags**: {', '.join(str(t) for t in tags)}")
        md_parts.append("")

        # Purpose Analysis
        purpose = explanation.get("purpose", {})
        md_parts.append("## Purpose Analysis")
        md_parts.append("")
        md_parts.append(f"**Primary Purpose**: {purpose.get('primary_purpose', 'Unknown')}")
        md_parts.append("")
        md_parts.append(f"**Business Domain**: {purpose.get('business_domain', 'general')}")
        md_parts.append("")
        md_parts.append(f"**Workflow Type**: {purpose.get('workflow_type', 'manual')}")
        md_parts.append("")
        md_parts.append(f"**Confidence**: {purpose.get('confidence', 0)*100:.0f}%")
        md_parts.append("")

        # Description
        md_parts.append("### Description")
        md_parts.append("")
        md_parts.append(purpose.get('description', 'No description available'))
        md_parts.append("")

        # Trigger
        md_parts.append("### Trigger")
        md_parts.append("")
        md_parts.append(purpose.get('trigger_description', 'No trigger configured'))
        md_parts.append("")

        # Expected Outcomes
        outcomes = purpose.get('expected_outcomes', [])
        if outcomes:
            md_parts.append("### Expected Outcomes")
            md_parts.append("")
            for outcome in outcomes:
                md_parts.append(f"- {outcome}")
            md_parts.append("")

        # Data Flow Analysis
        data_flow = explanation.get("data_flow", {})
        md_parts.append("## Data Flow Analysis")
        md_parts.append("")
        md_parts.append(f"**Summary**: {data_flow.get('summary', 'No data flow information')}")
        md_parts.append("")

        # Input Sources
        input_sources = data_flow.get("input_sources", [])
        if input_sources:
            md_parts.append("### Input Sources")
            md_parts.append("")
            for source in input_sources:
                md_parts.append(f"- **{source['node_name']}**: {source['source_type']}")
                details = source.get('details', {})
                if details:
                    for key, value in details.items():
                        if value:
                            md_parts.append(f"  - {key}: `{value}`")
            md_parts.append("")

        # Transformations
        transformations = data_flow.get("transformations", [])
        if transformations:
            md_parts.append("### Data Transformations")
            md_parts.append("")
            for trans in transformations:
                md_parts.append(f"- **{trans['node_name']}**: {trans['transformation_type']}")
            md_parts.append("")

        # Output Destinations
        output_destinations = data_flow.get("output_destinations", [])
        if output_destinations:
            md_parts.append("### Output Destinations")
            md_parts.append("")
            for dest in output_destinations:
                md_parts.append(f"- **{dest['node_name']}**: {dest['sink_type']}")
                details = dest.get('details', {})
                if details:
                    for key, value in details.items():
                        if value:
                            md_parts.append(f"  - {key}: `{value}`")
            md_parts.append("")

        # Critical Paths
        critical_paths = data_flow.get("critical_paths", [])
        if critical_paths:
            md_parts.append("### Critical Data Paths")
            md_parts.append("")
            for idx, path in enumerate(critical_paths[:5], 1):  # Top 5 paths
                path_str = " → ".join(path['path'])
                md_parts.append(f"{idx}. {path_str}")
            md_parts.append("")

        # Dependency Analysis
        dependencies = explanation.get("dependencies", {})
        md_parts.append("## Dependencies")
        md_parts.append("")
        md_parts.append(f"**Summary**: {dependencies.get('summary', 'No dependencies')}")
        md_parts.append("")

        # Internal Dependencies
        internal_deps = dependencies.get("internal_dependencies", [])
        if internal_deps:
            md_parts.append("### Internal Dependencies")
            md_parts.append("")
            for dep in internal_deps:
                if dep["type"] == "workflow_call":
                    md_parts.append(f"- Calls workflow: **{dep['target_workflow_name']}**")
                    md_parts.append(f"  - Node: `{dep['node_name']}`")
                    md_parts.append(f"  - Criticality: {dep['criticality']}")
            md_parts.append("")

        # External Dependencies
        external_deps = dependencies.get("external_dependencies", [])
        if external_deps:
            md_parts.append("### External Dependencies")
            md_parts.append("")
            for dep in external_deps:
                md_parts.append(f"- **{dep['service_name']}** ({dep.get('service_type', 'unknown')})")
                md_parts.append(f"  - Node: `{dep['node_name']}`")
                if dep.get('endpoint'):
                    md_parts.append(f"  - Endpoint: `{dep['endpoint']}`")
            md_parts.append("")

        # Credentials
        credentials = dependencies.get("credentials", [])
        if credentials:
            md_parts.append("### Credentials")
            md_parts.append("")
            for cred in credentials:
                md_parts.append(f"- **{cred['credential_name']}** ({cred['credential_type']})")
                md_parts.append(f"  - Criticality: {cred['criticality']}")
                md_parts.append(f"  - Used by: {', '.join(cred['used_by_nodes'])}")
            md_parts.append("")

        # Single Points of Failure
        spofs = dependencies.get("single_points_of_failure", [])
        if spofs:
            md_parts.append("### ⚠️ Single Points of Failure")
            md_parts.append("")
            for spof in spofs:
                md_parts.append(f"- **{spof.get('type', 'unknown')}** (Severity: {spof.get('severity', 'unknown')})")
                md_parts.append(f"  - {spof.get('impact', '')}")
                if spof.get('affected_nodes'):
                    md_parts.append(f"  - Affected nodes: {', '.join(spof['affected_nodes'])}")
            md_parts.append("")

        # Risk Analysis
        risks = explanation.get("risks", {})
        md_parts.append("## Risk Assessment")
        md_parts.append("")
        md_parts.append(f"**Overall Risk Level**: {risks.get('risk_level', 'low').upper()}")
        md_parts.append("")
        md_parts.append(f"**Risk Score**: {risks.get('overall_risk_score', 0):.1f}/10")
        md_parts.append("")
        md_parts.append(f"**Summary**: {risks.get('risk_summary', 'No risks identified')}")
        md_parts.append("")

        # Risk Categories
        risk_categories = [
            ("Data Loss Risks", "data_loss_risks"),
            ("Security Risks", "security_risks"),
            ("Performance Risks", "performance_risks"),
            ("Availability Risks", "availability_risks"),
            ("Compliance Risks", "compliance_risks"),
        ]

        for category_name, category_key in risk_categories:
            category_risks = risks.get(category_key, [])
            if category_risks:
                md_parts.append(f"### {category_name}")
                md_parts.append("")
                for risk in category_risks:
                    severity = risk.get('severity', 'low')
                    severity_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
                    emoji = severity_emoji.get(severity, "⚪")
                    md_parts.append(f"{emoji} **{risk.get('risk', 'unknown')}** (Severity: {severity})")
                    md_parts.append(f"  - {risk.get('description', '')}")
                    if risk.get('node'):
                        md_parts.append(f"  - Node: `{risk['node']}`")
                md_parts.append("")

        # Mitigation Plan
        mitigation_plan = risks.get("mitigation_plan", [])
        if mitigation_plan:
            md_parts.append("### Mitigation Plan")
            md_parts.append("")
            md_parts.append("Priority-ordered actions to reduce risks:")
            md_parts.append("")
            for item in mitigation_plan[:10]:  # Top 10
                priority = item.get('priority', '?')
                severity = item.get('severity', 'low')
                action = item.get('action', '')
                md_parts.append(f"{priority}. [{severity.upper()}] {action}")
            md_parts.append("")

        # Footer
        md_parts.append("---")
        md_parts.append("")
        md_parts.append("*Generated by n8n Workflow Builder - Explainability Layer*")
        md_parts.append("")

        return "\n".join(md_parts)

    @staticmethod
    def format_as_json(explanation: Dict) -> str:
        """Format explanation as JSON"""
        return json.dumps(explanation, indent=2, default=str)

    @staticmethod
    def format_as_text(explanation: Dict) -> str:
        """Format explanation as plain text"""
        text_parts = []

        # Header
        workflow_name = explanation.get("workflow_name", "Unknown Workflow")
        text_parts.append("=" * 80)
        text_parts.append(f"WORKFLOW EXPLANATION: {workflow_name}")
        text_parts.append("=" * 80)
        text_parts.append("")

        # Executive Summary
        text_parts.append("EXECUTIVE SUMMARY")
        text_parts.append("-" * 80)
        text_parts.append(explanation.get("executive_summary", ""))
        text_parts.append("")

        # Purpose
        purpose = explanation.get("purpose", {})
        text_parts.append("PURPOSE")
        text_parts.append("-" * 80)
        text_parts.append(f"Primary Purpose: {purpose.get('primary_purpose', 'Unknown')}")
        text_parts.append(f"Business Domain: {purpose.get('business_domain', 'general')}")
        text_parts.append(f"Workflow Type: {purpose.get('workflow_type', 'manual')}")
        text_parts.append(f"Confidence: {purpose.get('confidence', 0)*100:.0f}%")
        text_parts.append("")
        text_parts.append(purpose.get('description', 'No description available'))
        text_parts.append("")

        # Data Flow
        data_flow = explanation.get("data_flow", {})
        text_parts.append("DATA FLOW")
        text_parts.append("-" * 80)
        text_parts.append(data_flow.get('summary', 'No data flow information'))
        text_parts.append("")

        input_sources = data_flow.get("input_sources", [])
        if input_sources:
            text_parts.append(f"Input Sources ({len(input_sources)}):")
            for source in input_sources:
                text_parts.append(f"  - {source['node_name']}: {source['source_type']}")
        text_parts.append("")

        output_destinations = data_flow.get("output_destinations", [])
        if output_destinations:
            text_parts.append(f"Output Destinations ({len(output_destinations)}):")
            for dest in output_destinations:
                text_parts.append(f"  - {dest['node_name']}: {dest['sink_type']}")
        text_parts.append("")

        # Dependencies
        dependencies = explanation.get("dependencies", {})
        text_parts.append("DEPENDENCIES")
        text_parts.append("-" * 80)
        text_parts.append(dependencies.get('summary', 'No dependencies'))
        text_parts.append("")

        external_deps = dependencies.get("external_dependencies", [])
        if external_deps:
            text_parts.append(f"External Services ({len(external_deps)}):")
            for dep in external_deps:
                text_parts.append(f"  - {dep['service_name']} ({dep.get('service_type', 'unknown')})")
        text_parts.append("")

        # Risks
        risks = explanation.get("risks", {})
        text_parts.append("RISK ASSESSMENT")
        text_parts.append("-" * 80)
        text_parts.append(f"Overall Risk Level: {risks.get('risk_level', 'low').upper()}")
        text_parts.append(f"Risk Score: {risks.get('overall_risk_score', 0):.1f}/10")
        text_parts.append("")
        text_parts.append(risks.get('risk_summary', 'No risks identified'))
        text_parts.append("")

        # Top Risks
        all_risks = []
        for key in ["data_loss_risks", "security_risks", "performance_risks", "availability_risks", "compliance_risks"]:
            all_risks.extend(risks.get(key, []))

        if all_risks:
            text_parts.append("Top Risks:")
            severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
            sorted_risks = sorted(all_risks, key=lambda r: severity_order.get(r.get('severity', 'low'), 3))
            for risk in sorted_risks[:5]:  # Top 5
                severity = risk.get('severity', 'low')
                text_parts.append(f"  - [{severity.upper()}] {risk.get('description', '')}")
        text_parts.append("")

        # Footer
        text_parts.append("=" * 80)
        text_parts.append("Generated by n8n Workflow Builder - Explainability Layer")
        text_parts.append("=" * 80)
        text_parts.append("")

        return "\n".join(text_parts)

    @staticmethod
    def format(explanation: Dict, format_type: str = "markdown") -> str:
        """
        Format explanation in specified format

        Args:
            explanation: The explanation dict from WorkflowExplainer
            format_type: "markdown", "json", or "text"

        Returns:
            Formatted string
        """
        format_type = format_type.lower()

        if format_type == "markdown" or format_type == "md":
            return ExplainabilityFormatter.format_as_markdown(explanation)
        elif format_type == "json":
            return ExplainabilityFormatter.format_as_json(explanation)
        elif format_type == "text" or format_type == "txt":
            return ExplainabilityFormatter.format_as_text(explanation)
        else:
            raise ValueError(f"Unknown format type: {format_type}. Use 'markdown', 'json', or 'text'")
