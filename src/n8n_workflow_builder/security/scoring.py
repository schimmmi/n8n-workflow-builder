"""
Security Scoring System

Calculates overall security score and risk level for workflows.
"""

from typing import List, Dict
from enum import Enum
from dataclasses import dataclass


class RiskLevel(Enum):
    """Overall risk levels"""
    CRITICAL = "critical"  # 0-30
    HIGH = "high"          # 31-60
    MEDIUM = "medium"      # 61-80
    LOW = "low"            # 81-100
    EXCELLENT = "excellent"  # 100


@dataclass
class SecurityScore:
    """Security score result"""
    score: int  # 0-100
    risk_level: RiskLevel
    findings_count: Dict[str, int]  # Count by severity
    deductions: Dict[str, int]  # Points deducted per category
    max_possible: int = 100

    def to_dict(self) -> Dict:
        return {
            "score": self.score,
            "risk_level": self.risk_level.value,
            "grade": self._get_grade(),
            "findings_count": self.findings_count,
            "deductions": self.deductions,
            "max_possible": self.max_possible
        }

    def _get_grade(self) -> str:
        """Get letter grade"""
        if self.score >= 95:
            return "A+"
        elif self.score >= 90:
            return "A"
        elif self.score >= 85:
            return "B+"
        elif self.score >= 80:
            return "B"
        elif self.score >= 75:
            return "C+"
        elif self.score >= 70:
            return "C"
        elif self.score >= 60:
            return "D"
        else:
            return "F"


class SecurityScorer:
    """
    Calculates security scores based on findings
    """

    # Point deductions by severity
    DEDUCTION_MAP = {
        "critical": 25,
        "high": 15,
        "medium": 8,
        "low": 3
    }

    # Category weights (for prioritization)
    CATEGORY_WEIGHTS = {
        "secrets": 1.5,      # Hardcoded secrets are very bad
        "authentication": 1.3,  # Missing auth is serious
        "exposure": 1.2,     # Data exposure is important
    }

    def __init__(self):
        pass

    def calculate_score(
        self,
        secret_findings: List,
        auth_findings: List,
        exposure_findings: List
    ) -> SecurityScore:
        """
        Calculate overall security score

        Args:
            secret_findings: List of secret detection findings
            auth_findings: List of authentication findings
            exposure_findings: List of exposure findings

        Returns:
            SecurityScore object
        """
        # Start with perfect score
        score = 100
        deductions = {
            "secrets": 0,
            "authentication": 0,
            "exposure": 0
        }

        # Count findings by severity
        findings_count = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }

        # Process secret findings
        for finding in secret_findings:
            severity = finding.severity.value if hasattr(finding.severity, 'value') else finding.severity
            deduction = self.DEDUCTION_MAP[severity] * self.CATEGORY_WEIGHTS["secrets"]
            deductions["secrets"] += deduction
            findings_count[severity] += 1

        # Process auth findings
        for finding in auth_findings:
            severity = finding.severity.value if hasattr(finding.severity, 'value') else finding.severity
            deduction = self.DEDUCTION_MAP[severity] * self.CATEGORY_WEIGHTS["authentication"]
            deductions["authentication"] += deduction
            findings_count[severity] += 1

        # Process exposure findings
        for finding in exposure_findings:
            severity = finding.severity.value if hasattr(finding.severity, 'value') else finding.severity
            deduction = self.DEDUCTION_MAP[severity] * self.CATEGORY_WEIGHTS["exposure"]
            deductions["exposure"] += deduction
            findings_count[severity] += 1

        # Calculate total deductions
        total_deduction = sum(deductions.values())
        score = max(0, score - int(total_deduction))

        # Determine risk level
        risk_level = self._determine_risk_level(score, findings_count)

        return SecurityScore(
            score=score,
            risk_level=risk_level,
            findings_count=findings_count,
            deductions={k: int(v) for k, v in deductions.items()}
        )

    def _determine_risk_level(self, score: int, findings_count: Dict[str, int]) -> RiskLevel:
        """Determine risk level based on score and findings"""
        # Critical findings always mean high risk
        if findings_count["critical"] > 0:
            return RiskLevel.CRITICAL

        # Score-based risk level
        if score <= 30:
            return RiskLevel.CRITICAL
        elif score <= 60:
            return RiskLevel.HIGH
        elif score <= 80:
            return RiskLevel.MEDIUM
        elif score < 100:
            return RiskLevel.LOW
        else:
            return RiskLevel.EXCELLENT

    def get_priority_findings(
        self,
        secret_findings: List,
        auth_findings: List,
        exposure_findings: List,
        limit: int = 10
    ) -> List:
        """
        Get top priority findings to fix

        Args:
            secret_findings: Secret detection findings
            auth_findings: Authentication findings
            exposure_findings: Exposure findings
            limit: Max findings to return

        Returns:
            List of top priority findings
        """
        all_findings = []

        # Add weighted findings
        for finding in secret_findings:
            all_findings.append((finding, self.CATEGORY_WEIGHTS["secrets"]))

        for finding in auth_findings:
            all_findings.append((finding, self.CATEGORY_WEIGHTS["authentication"]))

        for finding in exposure_findings:
            all_findings.append((finding, self.CATEGORY_WEIGHTS["exposure"]))

        # Sort by severity and weight
        severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}

        def sort_key(item):
            finding, weight = item
            severity = finding.severity.value if hasattr(finding.severity, 'value') else finding.severity
            return (severity_order.get(severity, 0) * weight, weight)

        all_findings.sort(key=sort_key, reverse=True)

        # Return top findings
        return [finding for finding, _ in all_findings[:limit]]
