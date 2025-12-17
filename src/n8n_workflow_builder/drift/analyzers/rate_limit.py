#!/usr/bin/env python3
"""
Rate Limit Drift Analyzer

Detects approaching API rate limits, throttling patterns, and 429 error increases.
"""

from typing import Dict, List, Optional
from collections import defaultdict
from datetime import datetime, timedelta
import statistics


class RateLimitDriftAnalyzer:
    """Analyzes rate limit drift and throttling patterns"""

    @staticmethod
    def analyze_rate_limit_drift(executions: List[Dict], workflow: Dict) -> Dict:
        """
        Detect rate limit issues and throttling patterns

        Args:
            executions: List of execution records
            workflow: Workflow definition with node information

        Returns:
            Rate limit drift analysis
        """
        if not executions or len(executions) < 2:
            return {
                "drift_detected": False,
                "reason": "Insufficient execution history"
            }

        # Split into baseline and current periods
        total = len(executions)
        baseline_size = max(1, int(total * 0.3))
        current_size = max(1, int(total * 0.3))

        baseline_execs = executions[:baseline_size]
        current_execs = executions[-current_size:]

        # Extract rate limit metrics
        baseline_metrics = RateLimitDriftAnalyzer._extract_rate_limit_metrics(baseline_execs)
        current_metrics = RateLimitDriftAnalyzer._extract_rate_limit_metrics(current_execs)

        drift_patterns = []

        # 1. Increased 429 errors
        baseline_429_rate = baseline_metrics["rate_limit_errors"] / len(baseline_execs)
        current_429_rate = current_metrics["rate_limit_errors"] / len(current_execs)

        if current_429_rate > baseline_429_rate * 2 and current_429_rate > 0.05:  # >5% error rate
            severity = "critical" if current_429_rate > 0.2 else "warning"
            drift_patterns.append({
                "type": "rate_limit_errors_increased",
                "severity": severity,
                "baseline_rate": baseline_429_rate,
                "current_rate": current_429_rate,
                "increase_ratio": current_429_rate / baseline_429_rate if baseline_429_rate > 0 else float('inf'),
                "description": f"Rate limit (429) errors increased from {baseline_429_rate:.1%} to {current_429_rate:.1%}"
            })

        # 2. Increased retry frequency
        if baseline_metrics["avg_retries"] > 0:
            retry_ratio = current_metrics["avg_retries"] / baseline_metrics["avg_retries"]
            if retry_ratio > 1.5:
                severity = "warning" if retry_ratio < 3 else "critical"
                drift_patterns.append({
                    "type": "retry_frequency_increased",
                    "severity": severity,
                    "baseline_retries": baseline_metrics["avg_retries"],
                    "current_retries": current_metrics["avg_retries"],
                    "increase_ratio": retry_ratio,
                    "description": f"Average retries increased {retry_ratio:.1f}x (from {baseline_metrics['avg_retries']:.2f} to {current_metrics['avg_retries']:.2f})"
                })

        # 3. Execution timing patterns (bunching suggests rate limiting)
        baseline_timing = RateLimitDriftAnalyzer._analyze_execution_timing(baseline_execs)
        current_timing = RateLimitDriftAnalyzer._analyze_execution_timing(current_execs)

        if current_timing["bunching_score"] > baseline_timing["bunching_score"] * 1.5:
            drift_patterns.append({
                "type": "execution_bunching",
                "severity": "info",
                "baseline_bunching": baseline_timing["bunching_score"],
                "current_bunching": current_timing["bunching_score"],
                "description": "Execution timing shows increased bunching pattern (suggests rate limit backoff)"
            })

        # 4. Throughput degradation
        if baseline_metrics["executions_per_hour"] > 0:
            throughput_ratio = current_metrics["executions_per_hour"] / baseline_metrics["executions_per_hour"]
            if throughput_ratio < 0.7:  # >30% decrease
                severity = "warning" if throughput_ratio > 0.5 else "critical"
                drift_patterns.append({
                    "type": "throughput_degradation",
                    "severity": severity,
                    "baseline_throughput": baseline_metrics["executions_per_hour"],
                    "current_throughput": current_metrics["executions_per_hour"],
                    "decrease_percent": (1 - throughput_ratio) * 100,
                    "description": f"Workflow throughput decreased by {(1 - throughput_ratio) * 100:.1f}%"
                })

        # 5. Quota proximity warnings (from execution data)
        quota_warnings = RateLimitDriftAnalyzer._detect_quota_proximity(current_execs)
        if quota_warnings:
            drift_patterns.extend(quota_warnings)

        # Overall assessment
        has_critical = any(p["severity"] == "critical" for p in drift_patterns)
        has_warning = any(p["severity"] == "warning" for p in drift_patterns)

        overall_severity = "critical" if has_critical else ("warning" if has_warning else "info")

        return {
            "drift_detected": len(drift_patterns) > 0,
            "severity": overall_severity,
            "patterns": drift_patterns,
            "baseline_period": {
                "executions": len(baseline_execs),
                "rate_limit_errors": baseline_metrics["rate_limit_errors"],
                "avg_retries": baseline_metrics["avg_retries"],
                "throughput_per_hour": baseline_metrics["executions_per_hour"]
            },
            "current_period": {
                "executions": len(current_execs),
                "rate_limit_errors": current_metrics["rate_limit_errors"],
                "avg_retries": current_metrics["avg_retries"],
                "throughput_per_hour": current_metrics["executions_per_hour"]
            },
            "summary": {
                "rate_limit_error_increase": current_429_rate > baseline_429_rate * 2,
                "retry_frequency_increase": current_metrics["avg_retries"] > baseline_metrics["avg_retries"] * 1.5,
                "throughput_degradation": current_metrics["executions_per_hour"] < baseline_metrics["executions_per_hour"] * 0.7
            }
        }

    @staticmethod
    def _extract_rate_limit_metrics(executions: List[Dict]) -> Dict:
        """Extract rate limit related metrics from executions"""
        rate_limit_errors = 0
        total_retries = 0
        retry_counts = []

        # Calculate time span
        if executions:
            try:
                first_time = datetime.fromisoformat(executions[0].get("startedAt", "").replace('Z', '+00:00'))
                last_time = datetime.fromisoformat(executions[-1].get("startedAt", "").replace('Z', '+00:00'))
                time_span_hours = (last_time - first_time).total_seconds() / 3600
            except:
                time_span_hours = 1  # Default to 1 hour if parsing fails
        else:
            time_span_hours = 1

        for execution in executions:
            # Check for 429 errors
            data = execution.get("data", {})
            error = data.get("error", {})
            error_message = error.get("message", "") if isinstance(error, dict) else str(error)

            if "429" in error_message or "rate limit" in error_message.lower():
                rate_limit_errors += 1

            # Check for retries (if available in execution data)
            retry_count = execution.get("retryOf") or execution.get("retry_count", 0)
            if retry_count:
                total_retries += 1
                retry_counts.append(retry_count)

        avg_retries = total_retries / len(executions) if executions else 0
        executions_per_hour = len(executions) / time_span_hours if time_span_hours > 0 else 0

        return {
            "rate_limit_errors": rate_limit_errors,
            "total_retries": total_retries,
            "avg_retries": avg_retries,
            "executions_per_hour": executions_per_hour
        }

    @staticmethod
    def _analyze_execution_timing(executions: List[Dict]) -> Dict:
        """Analyze execution timing patterns to detect bunching"""
        if len(executions) < 3:
            return {"bunching_score": 0}

        # Extract timestamps
        timestamps = []
        for execution in executions:
            started = execution.get("startedAt")
            if started:
                try:
                    ts = datetime.fromisoformat(started.replace('Z', '+00:00'))
                    timestamps.append(ts)
                except:
                    pass

        if len(timestamps) < 3:
            return {"bunching_score": 0}

        # Calculate gaps between executions
        gaps = []
        for i in range(1, len(timestamps)):
            gap_seconds = (timestamps[i] - timestamps[i-1]).total_seconds()
            gaps.append(gap_seconds)

        if not gaps:
            return {"bunching_score": 0}

        # Bunching score: higher variance in gaps suggests bunching
        mean_gap = statistics.mean(gaps)
        if len(gaps) > 1:
            stddev_gap = statistics.stdev(gaps)
            coefficient_of_variation = stddev_gap / mean_gap if mean_gap > 0 else 0
        else:
            coefficient_of_variation = 0

        return {
            "bunching_score": coefficient_of_variation,
            "mean_gap_seconds": mean_gap,
            "gap_stddev": stddev_gap if len(gaps) > 1 else 0
        }

    @staticmethod
    def _detect_quota_proximity(executions: List[Dict]) -> List[Dict]:
        """Detect quota proximity warnings from execution data"""
        warnings = []

        # Look for quota-related warnings in recent executions
        recent_executions = executions[-10:] if len(executions) > 10 else executions

        quota_warning_count = 0
        for execution in recent_executions:
            data = execution.get("data", {})

            # Check for quota warnings in response headers or data
            # This is API-specific and would need to be customized
            result_data = data.get("resultData", {})
            if isinstance(result_data, dict):
                for run_data in result_data.values():
                    if isinstance(run_data, dict):
                        for node_data in run_data.values():
                            if isinstance(node_data, list):
                                for item in node_data:
                                    if isinstance(item, dict):
                                        # Check headers for rate limit info
                                        headers = item.get("headers", {})
                                        if isinstance(headers, dict):
                                            # Common rate limit headers
                                            remaining = headers.get("x-ratelimit-remaining") or headers.get("x-rate-limit-remaining")
                                            limit = headers.get("x-ratelimit-limit") or headers.get("x-rate-limit-limit")

                                            if remaining and limit:
                                                try:
                                                    remaining_int = int(remaining)
                                                    limit_int = int(limit)
                                                    usage_percent = (limit_int - remaining_int) / limit_int if limit_int > 0 else 0

                                                    if usage_percent > 0.8:  # >80% of quota used
                                                        quota_warning_count += 1
                                                except (ValueError, TypeError):
                                                    pass

        if quota_warning_count > 0:
            warnings.append({
                "type": "quota_proximity",
                "severity": "warning",
                "occurrences": quota_warning_count,
                "description": f"API quota usage detected at >80% in {quota_warning_count} recent execution(s)"
            })

        return warnings

    @staticmethod
    def suggest_rate_limit_fixes(drift_analysis: Dict, workflow: Dict) -> List[Dict]:
        """
        Suggest fixes for rate limit drift issues

        Args:
            drift_analysis: Output from analyze_rate_limit_drift
            workflow: Workflow definition

        Returns:
            List of fix suggestions
        """
        if not drift_analysis.get("drift_detected"):
            return []

        fixes = []
        patterns = drift_analysis.get("patterns", [])

        for pattern in patterns:
            pattern_type = pattern["type"]

            if pattern_type == "rate_limit_errors_increased":
                # Find HTTP nodes in workflow
                http_nodes = [n for n in workflow.get("nodes", []) if "http" in n.get("type", "").lower()]

                for node in http_nodes:
                    fixes.append({
                        "type": "add_request_throttling",
                        "node": node["name"],
                        "severity": pattern["severity"],
                        "description": "Add throttling to respect rate limits",
                        "suggestion": "Add 'Wait' node with 1-2 second delay before this HTTP request",
                        "confidence": 0.90
                    })

                    fixes.append({
                        "type": "enable_exponential_backoff",
                        "node": node["name"],
                        "severity": pattern["severity"],
                        "description": "Enable exponential backoff for 429 errors",
                        "suggestion": "Enable 'Retry On Fail' with exponential backoff in node settings",
                        "confidence": 0.95
                    })

            elif pattern_type == "throughput_degradation":
                fixes.append({
                    "type": "optimize_request_batching",
                    "severity": pattern["severity"],
                    "description": "Reduce request volume through batching",
                    "suggestion": "Combine multiple API calls into batch requests where supported by API",
                    "confidence": 0.75
                })

                fixes.append({
                    "type": "add_request_queue",
                    "severity": pattern["severity"],
                    "description": "Implement request queue to control throughput",
                    "suggestion": "Add workflow to queue requests and process at controlled rate",
                    "confidence": 0.70
                })

            elif pattern_type == "quota_proximity":
                fixes.append({
                    "type": "add_quota_monitoring",
                    "severity": pattern["severity"],
                    "description": "Monitor API quota usage proactively",
                    "suggestion": "Add alerting when quota usage exceeds 70%",
                    "confidence": 0.85
                })

        # General recommendations
        if any(p["type"] == "rate_limit_errors_increased" for p in patterns):
            fixes.append({
                "type": "review_execution_frequency",
                "description": "Review workflow trigger frequency",
                "suggestion": "Check if workflow can be triggered less frequently or process items in batches",
                "confidence": 0.80
            })

        return fixes
