"""
Change Formatter - Terraform-style output formatting

Formats change plans in a clear, readable format similar to terraform plan:
- Color-coded changes (breaking=red, structural=yellow, safe=green)
- Clear diff view
- Impact summary
- Recommendations
"""

from typing import Dict, List


class ChangeFormatter:
    """Formats change plans in terraform-style output"""

    @staticmethod
    def format_plan(diff: Dict, impact: Dict) -> str:
        """Format complete change plan"""
        output = []

        # Header
        output.append("=" * 80)
        output.append("WORKFLOW CHANGE PLAN")
        output.append("=" * 80)
        output.append("")

        # Summary
        summary = diff["summary"]
        output.append(f"Total Changes: {summary['total_changes']}")
        output.append(f"Risk Level: {summary['risk_level'].upper()}")
        output.append("")

        # Breaking changes
        if diff["breaking_changes"]:
            output.append("🔴 BREAKING CHANGES")
            output.append("-" * 80)
            for bc in diff["breaking_changes"]:
                output.append(f"  • [{bc['severity'].upper()}] {bc['description']}")
                output.append(f"    Impact: {bc['impact']}")
                output.append(f"    Recommendation: {bc['recommendation']}")
                output.append("")

        # Node changes
        node_diff = diff["nodes"]
        if node_diff["added"] or node_diff["removed"] or node_diff["modified"]:
            output.append("🟡 STRUCTURAL CHANGES")
            output.append("-" * 80)

            for node in node_diff["added"]:
                output.append(f"  + Added node: '{node['name']}' ({node['type']})")

            for node in node_diff["removed"]:
                output.append(f"  - Removed node: '{node['name']}' ({node['type']})")

            for mod in node_diff["modified"]:
                output.append(f"  ~ Modified node: '{mod['node_name']}'")
                for change in mod["changes"][:3]:  # Show first 3 changes
                    output.append(f"      {change['field']}: {change['old_value']} → {change['new_value']}")

            output.append("")

        # Connection changes
        conn_diff = diff["connections"]
        if conn_diff["added"] or conn_diff["removed"]:
            output.append("🟢 DATA FLOW CHANGES")
            output.append("-" * 80)

            for conn in conn_diff["added"]:
                output.append(f"  + New path: {conn['from']} → {conn['to']}")

            for conn in conn_diff["removed"]:
                output.append(f"  - Removed path: {conn['from']} → {conn['to']}")

            output.append("")

        # Impact summary
        output.append("⚠️  IMPACT ASSESSMENT")
        output.append("-" * 80)
        output.append(f"Overall Risk Score: {impact['overall_risk_score']}/10 ({impact['risk_level'].upper()})")
        output.append("")

        # Show key impacts
        for dimension in ["data_flow_impact", "trigger_impact", "dependency_impact"]:
            dim_impact = impact[dimension]
            if dim_impact["impacts"]:
                output.append(f"  {dimension.replace('_', ' ').title()}:")
                for imp in dim_impact["impacts"][:2]:  # Top 2
                    output.append(f"    • {imp['description']}")
                output.append("")

        # Recommendations
        if impact["recommendations"]:
            output.append("💡 RECOMMENDATIONS")
            output.append("-" * 80)
            for rec in impact["recommendations"]:
                output.append(f"  {rec}")
            output.append("")

        # Footer
        output.append("=" * 80)
        if summary["has_breaking_changes"]:
            output.append("⚠️  WARNING: This change contains breaking changes!")
            output.append("Review carefully before applying.")
        else:
            output.append("✅ No breaking changes detected.")
            output.append("This change appears safe to apply.")
        output.append("=" * 80)

        return "\n".join(output)

    @staticmethod
    def format_comparison(old_workflow: Dict, new_workflow: Dict, diff: Dict) -> str:
        """Format side-by-side comparison"""
        output = []

        output.append("WORKFLOW COMPARISON")
        output.append("=" * 80)
        output.append("")

        output.append(f"Old: {old_workflow.get('name')} (ID: {old_workflow.get('id')})")
        output.append(f"New: {new_workflow.get('name')} (ID: {new_workflow.get('id')})")
        output.append("")

        output.append(f"{'OLD':^38} | {'NEW':^38}")
        output.append("-" * 80)
        output.append(f"{len(old_workflow.get('nodes', [])):^38} | {len(new_workflow.get('nodes', [])):^38} nodes")
        output.append("")

        # Show key differences
        output.append("Key Differences:")
        if diff["nodes"]["added"]:
            output.append(f"  + {len(diff['nodes']['added'])} node(s) added")
        if diff["nodes"]["removed"]:
            output.append(f"  - {len(diff['nodes']['removed'])} node(s) removed")
        if diff["nodes"]["modified"]:
            output.append(f"  ~ {len(diff['nodes']['modified'])} node(s) modified")

        return "\n".join(output)
