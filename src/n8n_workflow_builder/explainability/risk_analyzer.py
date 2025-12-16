"""
Risk Analyzer - Comprehensive workflow risk assessment

Combines insights from:
- Semantic analysis (anti-patterns)
- Drift detection (degradation patterns)
- Execution history (failure patterns)
- Dependency mapping (external dependencies)

Identifies risks in categories:
- Data loss risks
- Security risks
- Performance risks
- Availability risks
- Compliance risks
"""

from typing import Dict, List, Optional


class RiskAnalyzer:
    """Analyzes workflow risks across multiple dimensions"""

    @staticmethod
    def analyze_risks(
        workflow: Dict,
        semantic_analysis: Optional[Dict] = None,
        drift_analysis: Optional[Dict] = None,
        execution_history: Optional[List[Dict]] = None,
        dependency_analysis: Optional[Dict] = None,
        intent_metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Comprehensive risk analysis

        Returns:
            {
                "data_loss_risks": List[Dict],
                "security_risks": List[Dict],
                "performance_risks": List[Dict],
                "availability_risks": List[Dict],
                "compliance_risks": List[Dict],
                "overall_risk_score": float,
                "risk_summary": str,
                "mitigation_plan": List[Dict]
            }
        """
        # Analyze data loss risks
        data_loss_risks = RiskAnalyzer._analyze_data_loss_risks(
            workflow, semantic_analysis, execution_history
        )

        # Analyze security risks
        security_risks = RiskAnalyzer._analyze_security_risks(
            workflow, semantic_analysis, dependency_analysis
        )

        # Analyze performance risks
        performance_risks = RiskAnalyzer._analyze_performance_risks(
            workflow, semantic_analysis, drift_analysis, execution_history
        )

        # Analyze availability risks
        availability_risks = RiskAnalyzer._analyze_availability_risks(
            workflow, drift_analysis, execution_history, dependency_analysis
        )

        # Analyze compliance risks
        compliance_risks = RiskAnalyzer._analyze_compliance_risks(
            workflow, semantic_analysis, dependency_analysis, intent_metadata
        )

        # Calculate overall risk score
        overall_risk_score = RiskAnalyzer._calculate_overall_risk_score(
            data_loss_risks,
            security_risks,
            performance_risks,
            availability_risks,
            compliance_risks
        )

        # Generate risk summary
        risk_summary = RiskAnalyzer._generate_risk_summary(
            overall_risk_score,
            data_loss_risks,
            security_risks,
            performance_risks,
            availability_risks,
            compliance_risks
        )

        # Generate mitigation plan
        mitigation_plan = RiskAnalyzer._generate_mitigation_plan(
            data_loss_risks,
            security_risks,
            performance_risks,
            availability_risks,
            compliance_risks
        )

        return {
            "data_loss_risks": data_loss_risks,
            "security_risks": security_risks,
            "performance_risks": performance_risks,
            "availability_risks": availability_risks,
            "compliance_risks": compliance_risks,
            "overall_risk_score": round(overall_risk_score, 2),
            "risk_level": RiskAnalyzer._risk_level_from_score(overall_risk_score),
            "risk_summary": risk_summary,
            "mitigation_plan": mitigation_plan,
        }

    @staticmethod
    def _analyze_data_loss_risks(
        workflow: Dict,
        semantic_analysis: Optional[Dict],
        execution_history: Optional[List[Dict]]
    ) -> List[Dict]:
        """Analyze risks that could lead to data loss"""
        risks = []
        nodes = workflow.get("nodes", [])

        # Check for missing error handling
        if semantic_analysis:
            issues = semantic_analysis.get("issues", [])
            error_handling_issues = [
                i for i in issues
                if i.get("pattern") == "missing_error_handling" or i.get("pattern") == "missing_retry_logic"
            ]
            if error_handling_issues:
                for issue in error_handling_issues:
                    risks.append({
                        "risk": "data_loss_from_unhandled_errors",
                        "severity": "high",
                        "node": issue.get("node"),
                        "description": "Node may fail silently without retry logic, potentially losing data",
                        "likelihood": "medium",
                        "impact": "high",
                    })

        # Check for database operations without transactions
        for node in nodes:
            node_type = node.get("type", "").lower()
            node_name = node.get("name", "")

            if any(db in node_type for db in ["postgres", "mysql", "mongodb"]):
                params = node.get("parameters", {})
                operation = params.get("operation", "")

                # Write operations without error handling
                if operation in ["insert", "update", "delete", "upsert"]:
                    risks.append({
                        "risk": "data_loss_from_database_operation",
                        "severity": "high",
                        "node": node_name,
                        "description": f"Database {operation} operation without visible transaction management",
                        "likelihood": "medium",
                        "impact": "high",
                    })

        # Check execution history for data-related failures
        if execution_history:
            failed_executions = [e for e in execution_history if not e.get("finished", True)]
            data_errors = [
                e for e in failed_executions
                if any(kw in str(e.get("data", {})).lower() for kw in ["data", "null", "undefined", "empty"])
            ]
            if len(data_errors) > 3:  # Multiple data-related failures
                risks.append({
                    "risk": "recurring_data_errors",
                    "severity": "high",
                    "description": f"{len(data_errors)} executions failed with data-related errors",
                    "likelihood": "high",
                    "impact": "high",
                })

        return risks

    @staticmethod
    def _analyze_security_risks(
        workflow: Dict,
        semantic_analysis: Optional[Dict],
        dependency_analysis: Optional[Dict]
    ) -> List[Dict]:
        """Analyze security risks"""
        risks = []
        nodes = workflow.get("nodes", [])

        # Check for hardcoded credentials (from semantic analysis)
        if semantic_analysis:
            issues = semantic_analysis.get("issues", [])
            cred_issues = [i for i in issues if i.get("pattern") == "hardcoded_credentials"]
            if cred_issues:
                for issue in cred_issues:
                    risks.append({
                        "risk": "hardcoded_credentials",
                        "severity": "critical",
                        "node": issue.get("node"),
                        "description": "Hardcoded credentials detected - security vulnerability",
                        "likelihood": "high",
                        "impact": "critical",
                    })

        # Check for webhook nodes without authentication
        for node in nodes:
            node_type = node.get("type", "").lower()
            node_name = node.get("name", "")

            if "webhook" in node_type:
                params = node.get("parameters", {})
                auth = params.get("authentication", "none")

                if auth == "none" or not auth:
                    risks.append({
                        "risk": "unauthenticated_webhook",
                        "severity": "high",
                        "node": node_name,
                        "description": "Webhook endpoint has no authentication - can be called by anyone",
                        "likelihood": "high",
                        "impact": "high",
                    })

        # Check for high-criticality credentials (from dependency analysis)
        if dependency_analysis:
            credentials = dependency_analysis.get("credentials", [])
            high_crit_creds = [c for c in credentials if c.get("criticality") == "high"]

            if high_crit_creds:
                risks.append({
                    "risk": "high_criticality_credentials",
                    "severity": "high",
                    "description": f"{len(high_crit_creds)} high-criticality credential(s) in use",
                    "likelihood": "medium",
                    "impact": "high",
                })

        # Check for HTTP nodes without TLS
        for node in nodes:
            node_type = node.get("type", "").lower()
            node_name = node.get("name", "")

            if "httprequest" in node_type:
                params = node.get("parameters", {})
                url = params.get("url", "")

                if url.startswith("http://"):  # Not HTTPS
                    risks.append({
                        "risk": "unencrypted_http_request",
                        "severity": "medium",
                        "node": node_name,
                        "description": "HTTP request without TLS encryption",
                        "likelihood": "high",
                        "impact": "medium",
                    })

        return risks

    @staticmethod
    def _analyze_performance_risks(
        workflow: Dict,
        semantic_analysis: Optional[Dict],
        drift_analysis: Optional[Dict],
        execution_history: Optional[List[Dict]]
    ) -> List[Dict]:
        """Analyze performance risks"""
        risks = []

        # Check for N+1 query patterns (from semantic analysis)
        if semantic_analysis:
            issues = semantic_analysis.get("issues", [])
            n_plus_one = [i for i in issues if i.get("pattern") == "n_plus_one_queries"]
            if n_plus_one:
                for issue in n_plus_one:
                    risks.append({
                        "risk": "n_plus_one_queries",
                        "severity": "medium",
                        "node": issue.get("node"),
                        "description": "N+1 query pattern detected - will slow down with more data",
                        "likelihood": "high",
                        "impact": "medium",
                    })

        # Check for performance drift (from drift analysis)
        if drift_analysis:
            drift_patterns = drift_analysis.get("drift_patterns", [])
            perf_drift = [p for p in drift_patterns if p.get("type") == "performance_drift"]
            if perf_drift:
                for pattern in perf_drift:
                    risks.append({
                        "risk": "performance_degradation",
                        "severity": "high",
                        "description": pattern.get("description", "Performance has degraded over time"),
                        "likelihood": "high",
                        "impact": "high",
                    })

        # Check for rate limiting issues (from semantic analysis)
        if semantic_analysis:
            issues = semantic_analysis.get("issues", [])
            rate_limit = [i for i in issues if i.get("pattern") == "missing_rate_limiting"]
            if rate_limit:
                for issue in rate_limit:
                    risks.append({
                        "risk": "no_rate_limiting",
                        "severity": "medium",
                        "node": issue.get("node"),
                        "description": "No rate limiting on external API calls - may hit rate limits",
                        "likelihood": "medium",
                        "impact": "medium",
                    })

        # Check execution history for slow executions
        if execution_history:
            durations = []
            for exec in execution_history:
                if exec.get("finished", True) and exec.get("startedAt") and exec.get("stoppedAt"):
                    try:
                        # Handle both string and int timestamps
                        started = exec["startedAt"]
                        stopped = exec["stoppedAt"]

                        # Convert to datetime if strings
                        if isinstance(started, str):
                            from datetime import datetime
                            started_dt = datetime.fromisoformat(started.replace('Z', '+00:00'))
                            stopped_dt = datetime.fromisoformat(stopped.replace('Z', '+00:00'))
                            duration = (stopped_dt - started_dt).total_seconds()
                        else:
                            # Already timestamps in milliseconds
                            duration = (stopped - started) / 1000

                        durations.append(duration)
                    except (ValueError, TypeError):
                        # Skip if timestamp parsing fails
                        continue

            if durations:
                avg_duration = sum(durations) / len(durations)
                if avg_duration > 10:  # Average execution > 10 seconds
                    risks.append({
                        "risk": "slow_execution_time",
                        "severity": "medium",
                        "description": f"Average execution time is {avg_duration:.1f} seconds",
                        "likelihood": "high",
                        "impact": "medium",
                    })

        return risks

    @staticmethod
    def _analyze_availability_risks(
        workflow: Dict,
        drift_analysis: Optional[Dict],
        execution_history: Optional[List[Dict]],
        dependency_analysis: Optional[Dict]
    ) -> List[Dict]:
        """Analyze availability risks"""
        risks = []

        # Check for success rate drift (from drift analysis)
        if drift_analysis:
            drift_patterns = drift_analysis.get("drift_patterns", [])
            success_drift = [p for p in drift_patterns if p.get("type") == "success_rate_drift"]
            if success_drift:
                for pattern in success_drift:
                    risks.append({
                        "risk": "declining_success_rate",
                        "severity": "critical",
                        "description": pattern.get("description", "Success rate has declined"),
                        "likelihood": "high",
                        "impact": "critical",
                    })

        # Check for single points of failure (from dependency analysis)
        if dependency_analysis:
            spofs = dependency_analysis.get("single_points_of_failure", [])
            if spofs:
                for spof in spofs:
                    risks.append({
                        "risk": "single_point_of_failure",
                        "severity": "high",
                        "description": spof.get("impact", "Single point of failure identified"),
                        "affected_nodes": spof.get("affected_nodes", []),
                        "likelihood": "medium",
                        "impact": "high",
                    })

        # Check execution history for failure rate
        if execution_history and len(execution_history) >= 10:
            failed_count = sum(1 for e in execution_history if not e.get("finished", True))
            failure_rate = failed_count / len(execution_history)

            if failure_rate > 0.1:  # More than 10% failure rate
                risks.append({
                    "risk": "high_failure_rate",
                    "severity": "critical" if failure_rate > 0.3 else "high",
                    "description": f"Workflow has {failure_rate*100:.1f}% failure rate",
                    "likelihood": "high",
                    "impact": "high",
                })

        # Check for infinite loop risk
        nodes = workflow.get("nodes", [])
        loop_nodes = [n for n in nodes if "loop" in n.get("type", "").lower()]
        if loop_nodes:
            # Check if loop has completion conditions
            for loop_node in loop_nodes:
                params = loop_node.get("parameters", {})
                max_iterations = params.get("maxIterations", 0)
                if not max_iterations or max_iterations > 1000:
                    risks.append({
                        "risk": "potential_infinite_loop",
                        "severity": "high",
                        "node": loop_node.get("name", ""),
                        "description": "Loop node without reasonable iteration limit",
                        "likelihood": "low",
                        "impact": "critical",
                    })

        return risks

    @staticmethod
    def _analyze_compliance_risks(
        workflow: Dict,
        semantic_analysis: Optional[Dict],
        dependency_analysis: Optional[Dict],
        intent_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """Analyze compliance risks (GDPR, audit, documentation)"""
        risks = []
        nodes = workflow.get("nodes", [])

        # Check for data handling without validation
        if semantic_analysis:
            issues = semantic_analysis.get("issues", [])
            validation_issues = [i for i in issues if i.get("pattern") == "missing_data_validation"]
            if validation_issues:
                risks.append({
                    "risk": "unvalidated_data_processing",
                    "severity": "medium",
                    "description": "Processing data without validation - compliance risk",
                    "likelihood": "high",
                    "impact": "medium",
                })

        # Check for missing documentation (intent metadata)
        # First check if we have intent metadata system data
        if intent_metadata and "nodes" in intent_metadata:
            # Count nodes with intent metadata
            intent_nodes = intent_metadata.get("nodes", {})
            documented_count = len(intent_nodes)
            doc_coverage = documented_count / len(nodes) if nodes else 0
        else:
            # Fallback to checking node metadata directly
            documented_nodes = [n for n in nodes if n.get("notes") or n.get("metadata", {}).get("intent")]
            doc_coverage = len(documented_nodes) / len(nodes) if nodes else 0

        if doc_coverage < 0.3:  # Less than 30% documented
            risks.append({
                "risk": "insufficient_documentation",
                "severity": "medium",
                "description": f"Only {doc_coverage*100:.0f}% of nodes are documented - audit risk",
                "likelihood": "high",
                "impact": "low",
            })

        # Check for external data transfers (GDPR risk)
        if dependency_analysis:
            external_deps = dependency_analysis.get("external_dependencies", [])
            apis = [d for d in external_deps if d.get("service_type") == "external_api"]

            if len(apis) >= 3:  # Multiple external APIs
                risks.append({
                    "risk": "multiple_external_data_transfers",
                    "severity": "medium",
                    "description": f"Data flows to {len(apis)} external services - GDPR compliance required",
                    "likelihood": "high",
                    "impact": "medium",
                })

        return risks

    @staticmethod
    def _calculate_overall_risk_score(
        data_loss_risks: List[Dict],
        security_risks: List[Dict],
        performance_risks: List[Dict],
        availability_risks: List[Dict],
        compliance_risks: List[Dict]
    ) -> float:
        """Calculate overall risk score (0.0 - 10.0)"""
        severity_scores = {
            "critical": 10,
            "high": 7,
            "medium": 4,
            "low": 2,
        }

        all_risks = (
            data_loss_risks +
            security_risks +
            performance_risks +
            availability_risks +
            compliance_risks
        )

        if not all_risks:
            return 0.0

        total_score = sum(severity_scores.get(r.get("severity", "low"), 2) for r in all_risks)
        # Normalize to 0-10 scale
        return min(10.0, total_score / len(all_risks))

    @staticmethod
    def _risk_level_from_score(score: float) -> str:
        """Convert risk score to risk level"""
        if score >= 7:
            return "critical"
        elif score >= 5:
            return "high"
        elif score >= 3:
            return "medium"
        else:
            return "low"

    @staticmethod
    def _generate_risk_summary(
        overall_risk_score: float,
        data_loss_risks: List[Dict],
        security_risks: List[Dict],
        performance_risks: List[Dict],
        availability_risks: List[Dict],
        compliance_risks: List[Dict]
    ) -> str:
        """Generate human-readable risk summary"""
        risk_level = RiskAnalyzer._risk_level_from_score(overall_risk_score)

        parts = [f"Overall Risk Level: {risk_level.upper()} (score: {overall_risk_score:.1f}/10)"]

        # Count by category
        if data_loss_risks:
            parts.append(f"{len(data_loss_risks)} data loss risk(s)")
        if security_risks:
            parts.append(f"{len(security_risks)} security risk(s)")
        if performance_risks:
            parts.append(f"{len(performance_risks)} performance risk(s)")
        if availability_risks:
            parts.append(f"{len(availability_risks)} availability risk(s)")
        if compliance_risks:
            parts.append(f"{len(compliance_risks)} compliance risk(s)")

        if len(parts) == 1:
            parts.append("No significant risks identified")

        return ". ".join(parts) + "."

    @staticmethod
    def _generate_mitigation_plan(
        data_loss_risks: List[Dict],
        security_risks: List[Dict],
        performance_risks: List[Dict],
        availability_risks: List[Dict],
        compliance_risks: List[Dict]
    ) -> List[Dict]:
        """Generate prioritized mitigation plan"""
        all_risks = (
            data_loss_risks +
            security_risks +
            performance_risks +
            availability_risks +
            compliance_risks
        )

        # Sort by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        sorted_risks = sorted(all_risks, key=lambda r: severity_order.get(r.get("severity", "low"), 3))

        # Generate mitigation actions
        mitigation_plan = []

        for idx, risk in enumerate(sorted_risks[:10], 1):  # Top 10 risks
            risk_type = risk.get("risk", "")
            severity = risk.get("severity", "low")
            node = risk.get("node")

            # Generate mitigation action based on risk type
            action = RiskAnalyzer._get_mitigation_action(risk_type, node)

            mitigation_plan.append({
                "priority": idx,
                "severity": severity,
                "risk": risk_type,
                "description": risk.get("description", ""),
                "node": node,
                "action": action,
            })

        return mitigation_plan

    @staticmethod
    def _get_mitigation_action(risk_type: str, node: Optional[str]) -> str:
        """Get specific mitigation action for risk type"""
        mitigations = {
            "hardcoded_credentials": "Move credentials to n8n credential store immediately",
            "unauthenticated_webhook": "Enable webhook authentication (API key, JWT, or basic auth)",
            "data_loss_from_unhandled_errors": "Add error handling and retry logic with exponential backoff",
            "n_plus_one_queries": "Batch database queries or use JOIN operations",
            "no_rate_limiting": "Add rate limiting or delays between API calls",
            "single_point_of_failure": "Add redundancy or fallback mechanisms",
            "high_failure_rate": "Investigate error patterns and add error handling",
            "potential_infinite_loop": "Set reasonable maxIterations limit on loop node",
            "insufficient_documentation": "Add intent metadata to critical nodes",
            "performance_degradation": "Investigate recent changes and optimize slow nodes",
            "declining_success_rate": "Run drift detection to identify root cause",
            "multiple_external_data_transfers": "Review GDPR compliance and add data processing agreements",
        }

        action = mitigations.get(risk_type, "Review and address this risk")
        if node:
            action = f"[{node}] {action}"

        return action
