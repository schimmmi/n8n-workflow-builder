"""
Migration Reporter

Generates detailed reports about migrations and compatibility issues.
"""
from typing import Dict, List, Optional
from datetime import datetime

from .version_checker import CompatibilityResult, CompatibilityIssue, CompatibilityStatus


class MigrationReporter:
    """
    Generates formatted reports for migrations
    """

    def generate_compatibility_report(
        self,
        workflow: Dict,
        result: CompatibilityResult
    ) -> str:
        """
        Generate detailed compatibility report

        Args:
            workflow: Workflow JSON
            result: Compatibility check result

        Returns:
            Formatted report text
        """
        report = []
        report.append(f"# Compatibility Report: {workflow.get('name', 'Unknown')}")
        report.append("")
        report.append(f"**Status:** {self._status_emoji(result.status)} {result.status.value.upper()}")
        report.append(f"**Issues Found:** {len(result.issues)}")
        report.append(f"**Workflow Version:** {result.workflow_version or 'Unknown'}")
        report.append("")

        if not result.has_issues:
            report.append("✅ **All nodes are compatible!** No migration needed.")
            return "\n".join(report)

        # Group issues by severity
        critical = [i for i in result.issues if i.severity == "critical"]
        high = [i for i in result.issues if i.severity == "high"]
        medium = [i for i in result.issues if i.severity == "medium"]
        low = [i for i in result.issues if i.severity == "low"]

        if critical:
            report.append("## 🔴 Critical Issues")
            report.append("")
            for issue in critical:
                report.append(self._format_issue(issue))
                report.append("")

        if high:
            report.append("## 🟠 High Priority Issues")
            report.append("")
            for issue in high:
                report.append(self._format_issue(issue))
                report.append("")

        if medium:
            report.append("## 🟡 Medium Priority Issues")
            report.append("")
            for issue in medium:
                report.append(self._format_issue(issue))
                report.append("")

        if low:
            report.append("## 🟢 Low Priority Issues")
            report.append("")
            for issue in low:
                report.append(self._format_issue(issue))
                report.append("")

        # Migration recommendations
        report.append("## 💡 Recommendations")
        report.append("")

        can_auto_migrate = all(i.migration_available for i in result.issues)
        if can_auto_migrate:
            report.append("✅ **Auto-migration available** - All issues can be automatically fixed!")
            report.append("")
            report.append("Run: `migrate_workflow(workflow_id)` to apply fixes")
        else:
            report.append("⚠️ **Manual intervention required** - Some issues need manual fixes.")
            manual_issues = [i for i in result.issues if not i.migration_available]
            report.append("")
            report.append("Issues requiring manual review:")
            for issue in manual_issues:
                report.append(f"- {issue.node_name}: {issue.description}")

        return "\n".join(report)

    def generate_migration_report(
        self,
        workflow: Dict,
        migration_log: List[Dict],
        before_result: CompatibilityResult,
        after_result: CompatibilityResult
    ) -> str:
        """
        Generate report about completed migration

        Args:
            workflow: Workflow JSON (after migration)
            migration_log: Log of applied migrations
            before_result: Compatibility before migration
            after_result: Compatibility after migration

        Returns:
            Formatted report text
        """
        report = []
        report.append(f"# Migration Report: {workflow.get('name', 'Unknown')}")
        report.append("")
        report.append(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Migrations Applied:** {len(migration_log)}")
        report.append("")

        # Before/After comparison
        report.append("## Status Comparison")
        report.append("")
        report.append("| Metric | Before | After |")
        report.append("|--------|--------|-------|")
        report.append(f"| Status | {before_result.status.value} | {after_result.status.value} |")
        report.append(f"| Issues | {len(before_result.issues)} | {len(after_result.issues)} |")
        report.append(f"| Breaking Changes | {'Yes' if before_result.has_breaking_changes else 'No'} | {'Yes' if after_result.has_breaking_changes else 'No'} |")
        report.append("")

        # Applied migrations
        if migration_log:
            report.append("## Applied Migrations")
            report.append("")

            # Group by node
            by_node = {}
            for entry in migration_log:
                node_name = entry.get("node_name", "Unknown")
                if node_name not in by_node:
                    by_node[node_name] = []
                by_node[node_name].append(entry)

            for node_name, entries in by_node.items():
                report.append(f"### {node_name}")
                report.append("")
                for entry in entries:
                    report.append(f"- **{entry.get('rule_name')}**")
                    report.append(f"  - Version: {entry.get('from_version')} → {entry.get('to_version')}")
                    report.append(f"  - Rule ID: `{entry.get('rule_id')}`")
                report.append("")

        # Remaining issues
        if after_result.has_issues:
            report.append("## ⚠️ Remaining Issues")
            report.append("")
            report.append("Some issues could not be automatically resolved:")
            report.append("")
            for issue in after_result.issues:
                report.append(f"- **{issue.node_name}**: {issue.description}")
                if issue.suggested_fix:
                    report.append(f"  - Fix: {issue.suggested_fix}")
            report.append("")
        else:
            report.append("## ✅ Success")
            report.append("")
            report.append("All compatibility issues have been resolved!")
            report.append("")

        return "\n".join(report)

    def generate_batch_report(
        self,
        results: List[tuple[Dict, CompatibilityResult, List[Dict]]]
    ) -> str:
        """
        Generate report for batch workflow updates

        Args:
            results: List of (workflow, compatibility_result, migration_log) tuples

        Returns:
            Formatted report text
        """
        report = []
        report.append("# Batch Migration Report")
        report.append("")
        report.append(f"**Workflows Processed:** {len(results)}")
        report.append(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Summary statistics
        compatible = sum(1 for _, r, _ in results if r.status == CompatibilityStatus.COMPATIBLE)
        deprecated = sum(1 for _, r, _ in results if r.status == CompatibilityStatus.DEPRECATED)
        breaking = sum(1 for _, r, _ in results if r.status == CompatibilityStatus.BREAKING)
        total_issues = sum(len(r.issues) for _, r, _ in results)
        total_migrations = sum(len(log) for _, _, log in results)

        report.append("## Summary")
        report.append("")
        report.append(f"- ✅ Compatible: {compatible}")
        report.append(f"- 🟡 Deprecated: {deprecated}")
        report.append(f"- 🔴 Breaking: {breaking}")
        report.append(f"- 📝 Total Issues: {total_issues}")
        report.append(f"- 🔄 Migrations Applied: {total_migrations}")
        report.append("")

        # Per-workflow results
        report.append("## Workflow Results")
        report.append("")

        for workflow, compatibility, migration_log in results:
            name = workflow.get("name", "Unknown")
            status_emoji = self._status_emoji(compatibility.status)

            report.append(f"### {status_emoji} {name}")
            report.append("")
            report.append(f"- Status: {compatibility.status.value}")
            report.append(f"- Issues: {len(compatibility.issues)}")
            report.append(f"- Migrations: {len(migration_log)}")

            if compatibility.has_breaking_changes:
                report.append("- ⚠️ **Has breaking changes**")

            report.append("")

        return "\n".join(report)

    def _format_issue(self, issue: CompatibilityIssue) -> str:
        """Format a single compatibility issue"""
        lines = []
        lines.append(f"**{issue.node_name}** ({issue.node_type})")
        lines.append(f"- Type: {issue.issue_type}")
        lines.append(f"- {issue.description}")

        if issue.old_value:
            lines.append(f"- Current value: `{issue.old_value}`")

        if issue.suggested_fix:
            lines.append(f"- 💡 Suggested fix: {issue.suggested_fix}")

        if issue.migration_available:
            lines.append("- ✅ Auto-migration available")
        else:
            lines.append("- ⚠️ Manual fix required")

        return "\n".join(lines)

    def _status_emoji(self, status: CompatibilityStatus) -> str:
        """Get emoji for compatibility status"""
        emoji_map = {
            CompatibilityStatus.COMPATIBLE: "✅",
            CompatibilityStatus.DEPRECATED: "🟡",
            CompatibilityStatus.BREAKING: "🔴",
            CompatibilityStatus.UNKNOWN: "❓",
        }
        return emoji_map.get(status, "❓")

    def generate_json_report(
        self,
        workflow: Dict,
        result: CompatibilityResult,
        migration_log: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Generate machine-readable JSON report

        Args:
            workflow: Workflow JSON
            result: Compatibility result
            migration_log: Optional migration log

        Returns:
            JSON-serializable report dictionary
        """
        return {
            "workflow": {
                "id": workflow.get("id"),
                "name": workflow.get("name"),
                "version": workflow.get("version"),
            },
            "compatibility": {
                "status": result.status.value,
                "has_issues": result.has_issues,
                "has_breaking_changes": result.has_breaking_changes,
                "n8n_version": result.n8n_version,
                "workflow_version": result.workflow_version,
            },
            "issues": [
                {
                    "node_name": issue.node_name,
                    "node_type": issue.node_type,
                    "issue_type": issue.issue_type,
                    "severity": issue.severity,
                    "description": issue.description,
                    "old_value": issue.old_value,
                    "suggested_fix": issue.suggested_fix,
                    "migration_available": issue.migration_available,
                }
                for issue in result.issues
            ],
            "migration": {
                "available": all(i.migration_available for i in result.issues),
                "log": migration_log or [],
            },
            "timestamp": datetime.now().isoformat(),
        }
