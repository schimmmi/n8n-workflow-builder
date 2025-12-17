"""
Main Security Auditor

Orchestrates all security audits and generates comprehensive reports.
"""

from typing import Dict, List, Optional, Tuple
from .secrets import SecretDetector, SecretFinding
from .auth import AuthenticationAuditor, AuthFinding
from .exposure import ExposureAnalyzer, ExposureFinding
from .scoring import SecurityScorer, SecurityScore
from .report import SecurityReport
import logging

logger = logging.getLogger("n8n-workflow-builder")


class SecurityAuditor:
    """
    Main security auditor that orchestrates all security checks
    """

    def __init__(self):
        self.secret_detector = SecretDetector()
        self.auth_auditor = AuthenticationAuditor()
        self.exposure_analyzer = ExposureAnalyzer()
        self.scorer = SecurityScorer()
        self.reporter = SecurityReport()

    def audit_workflow(
        self,
        workflow: Dict,
        include_secrets: bool = True,
        include_auth: bool = True,
        include_exposure: bool = True
    ) -> Tuple[SecurityScore, List[SecretFinding], List[AuthFinding], List[ExposureFinding]]:
        """
        Perform comprehensive security audit on workflow

        Args:
            workflow: Workflow dict with nodes and connections
            include_secrets: Run secret detection
            include_auth: Run authentication audit
            include_exposure: Run exposure analysis

        Returns:
            Tuple of (SecurityScore, secret_findings, auth_findings, exposure_findings)
        """
        workflow_id = workflow.get("id", "unknown")
        workflow_name = workflow.get("name", "Unknown")

        logger.info(f"🔐 Starting security audit for workflow: {workflow_name} ({workflow_id})")

        # Run security scans
        secret_findings = []
        auth_findings = []
        exposure_findings = []

        if include_secrets:
            logger.info("  🔍 Scanning for hardcoded secrets...")
            secret_findings = self.secret_detector.scan_workflow(workflow)
            logger.info(f"     Found {len(secret_findings)} secret(s)")

        if include_auth:
            logger.info("  🔒 Auditing authentication...")
            auth_findings = self.auth_auditor.audit_workflow(workflow)
            logger.info(f"     Found {len(auth_findings)} authentication issue(s)")

        if include_exposure:
            logger.info("  🌐 Analyzing exposure risks...")
            exposure_findings = self.exposure_analyzer.analyze_workflow(workflow)
            logger.info(f"     Found {len(exposure_findings)} exposure risk(s)")

        # Calculate security score
        logger.info("  📊 Calculating security score...")
        score = self.scorer.calculate_score(
            secret_findings,
            auth_findings,
            exposure_findings
        )

        logger.info(f"✅ Security audit complete. Score: {score.score}/100 ({score.risk_level.value})")

        return score, secret_findings, auth_findings, exposure_findings

    def generate_report(
        self,
        workflow: Dict,
        score: SecurityScore,
        secret_findings: List[SecretFinding],
        auth_findings: List[AuthFinding],
        exposure_findings: List[ExposureFinding],
        format: str = "markdown"
    ) -> str:
        """
        Generate formatted security audit report

        Args:
            workflow: Workflow dict
            score: Security score
            secret_findings: Secret detection findings
            auth_findings: Authentication findings
            exposure_findings: Exposure findings
            format: Report format (markdown, json, text)

        Returns:
            Formatted report string
        """
        return self.reporter.generate_report(
            workflow,
            score,
            secret_findings,
            auth_findings,
            exposure_findings,
            format=format
        )

    def audit_and_report(
        self,
        workflow: Dict,
        format: str = "markdown",
        include_secrets: bool = True,
        include_auth: bool = True,
        include_exposure: bool = True
    ) -> Tuple[str, SecurityScore]:
        """
        Run complete audit and generate report in one call

        Args:
            workflow: Workflow dict
            format: Report format
            include_secrets: Include secret detection
            include_auth: Include authentication audit
            include_exposure: Include exposure analysis

        Returns:
            Tuple of (report_string, security_score)
        """
        # Run audit
        score, secrets, auth, exposure = self.audit_workflow(
            workflow,
            include_secrets=include_secrets,
            include_auth=include_auth,
            include_exposure=include_exposure
        )

        # Generate report
        report = self.generate_report(
            workflow,
            score,
            secrets,
            auth,
            exposure,
            format=format
        )

        return report, score

    def get_critical_findings(
        self,
        workflow: Dict
    ) -> Dict[str, List]:
        """
        Get only critical and high severity findings

        Args:
            workflow: Workflow dict

        Returns:
            Dict with 'secrets', 'authentication', 'exposure' lists
        """
        score, secrets, auth, exposure = self.audit_workflow(workflow)

        critical_findings = {
            "secrets": [
                f for f in secrets
                if f.severity.value in ["critical", "high"]
            ],
            "authentication": [
                f for f in auth
                if f.severity.value in ["critical", "high"]
            ],
            "exposure": [
                f for f in exposure
                if f.severity.value in ["critical", "high"]
            ]
        }

        return critical_findings

    def get_summary(
        self,
        workflow: Dict
    ) -> Dict:
        """
        Get concise security audit summary

        Args:
            workflow: Workflow dict

        Returns:
            Summary dict with score and counts
        """
        score, secrets, auth, exposure = self.audit_workflow(workflow)

        return {
            "workflow_id": workflow.get("id", "unknown"),
            "workflow_name": workflow.get("name", "Unknown"),
            "score": score.score,
            "risk_level": score.risk_level.value,
            "grade": score._get_grade(),
            "total_findings": len(secrets) + len(auth) + len(exposure),
            "findings_by_category": {
                "secrets": len(secrets),
                "authentication": len(auth),
                "exposure": len(exposure)
            },
            "findings_by_severity": score.findings_count
        }

    def validate_compliance(
        self,
        workflow: Dict,
        standard: str = "basic"
    ) -> Tuple[bool, List[str]]:
        """
        Check if workflow meets security compliance standards

        Args:
            workflow: Workflow dict
            standard: Compliance standard (basic, strict, enterprise)

        Returns:
            Tuple of (is_compliant, list_of_violations)
        """
        score, secrets, auth, exposure = self.audit_workflow(workflow)

        violations = []

        if standard == "basic":
            # Basic: No critical findings
            if score.findings_count["critical"] > 0:
                violations.append("Critical security findings detected")

        elif standard == "strict":
            # Strict: No critical or high findings
            if score.findings_count["critical"] > 0:
                violations.append("Critical security findings detected")
            if score.findings_count["high"] > 0:
                violations.append("High severity security findings detected")

        elif standard == "enterprise":
            # Enterprise: Score must be >= 85, no critical/high findings
            if score.score < 85:
                violations.append(f"Security score too low: {score.score}/100 (required: 85+)")
            if score.findings_count["critical"] > 0:
                violations.append("Critical security findings detected")
            if score.findings_count["high"] > 0:
                violations.append("High severity security findings detected")

            # Additional enterprise requirements
            if any("webhook" in node.get("type", "").lower() for node in workflow.get("nodes", [])):
                webhook_auth = [
                    f for f in auth
                    if f.issue_type.value == "missing_auth" and "webhook" in f.node_type.lower()
                ]
                if webhook_auth:
                    violations.append("Unauthenticated webhooks detected")

        is_compliant = len(violations) == 0

        return is_compliant, violations

    def compare_security(
        self,
        workflow1: Dict,
        workflow2: Dict
    ) -> Dict:
        """
        Compare security posture of two workflows

        Args:
            workflow1: First workflow
            workflow2: Second workflow

        Returns:
            Comparison dict
        """
        summary1 = self.get_summary(workflow1)
        summary2 = self.get_summary(workflow2)

        return {
            "workflow1": summary1,
            "workflow2": summary2,
            "comparison": {
                "score_difference": summary1["score"] - summary2["score"],
                "better_security": summary1["workflow_name"] if summary1["score"] > summary2["score"] else summary2["workflow_name"],
                "total_findings_difference": summary1["total_findings"] - summary2["total_findings"]
            }
        }
