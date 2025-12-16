#!/usr/bin/env python3
"""
Drift Detection System
Detects workflow degradation over time by analyzing execution patterns
"""
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import statistics


class DriftDetector:
    """Detects drift in workflow executions over time"""

    @staticmethod
    def analyze_execution_history(executions: List[Dict]) -> Dict:
        """Analyze execution history and detect drift patterns

        Args:
            executions: List of execution records sorted by date (oldest first)

        Returns:
            Drift analysis with patterns and severity
        """
        if not executions or len(executions) < 2:
            return {
                "drift_detected": False,
                "reason": "Insufficient execution history (need at least 2 executions)"
            }

        # Split into baseline (first 30%) and current (last 30%) periods
        total = len(executions)
        baseline_size = max(1, int(total * 0.3))
        current_size = max(1, int(total * 0.3))

        baseline_execs = executions[:baseline_size]
        current_execs = executions[-current_size:]

        # Calculate metrics for each period
        baseline_metrics = DriftDetector._calculate_period_metrics(baseline_execs)
        current_metrics = DriftDetector._calculate_period_metrics(current_execs)

        # Detect drift patterns
        drift_patterns = []

        # Success rate drift
        success_change = current_metrics["success_rate"] - baseline_metrics["success_rate"]
        if abs(success_change) > 0.15:  # 15% threshold
            severity = "critical" if abs(success_change) > 0.3 else "warning"
            drift_patterns.append({
                "type": "success_rate_drift",
                "severity": severity,
                "baseline": baseline_metrics["success_rate"],
                "current": current_metrics["success_rate"],
                "change_percent": success_change * 100,
                "description": f"Success rate {'decreased' if success_change < 0 else 'increased'} by {abs(success_change * 100):.1f}%"
            })

        # Duration drift
        if baseline_metrics["avg_duration"] > 0:
            duration_ratio = current_metrics["avg_duration"] / baseline_metrics["avg_duration"]
            if duration_ratio > 1.5 or duration_ratio < 0.5:  # 50% change threshold
                severity = "critical" if duration_ratio > 2.0 else "warning"
                drift_patterns.append({
                    "type": "performance_drift",
                    "severity": severity,
                    "baseline": baseline_metrics["avg_duration"],
                    "current": current_metrics["avg_duration"],
                    "change_ratio": duration_ratio,
                    "description": f"Average duration {'increased' if duration_ratio > 1 else 'decreased'} by {abs((duration_ratio - 1) * 100):.1f}%"
                })

        # Error pattern drift
        baseline_errors = set(baseline_metrics["error_types"].keys())
        current_errors = set(current_metrics["error_types"].keys())

        # New error types
        new_errors = current_errors - baseline_errors
        if new_errors:
            drift_patterns.append({
                "type": "new_error_pattern",
                "severity": "warning",
                "new_errors": list(new_errors),
                "description": f"New error types appeared: {', '.join(new_errors)}"
            })

        # Error frequency increase
        for error_type in baseline_errors & current_errors:
            baseline_count = baseline_metrics["error_types"][error_type]
            current_count = current_metrics["error_types"][error_type]

            # Normalize by period size
            baseline_freq = baseline_count / len(baseline_execs)
            current_freq = current_count / len(current_execs)

            if current_freq > baseline_freq * 2:  # 2x increase
                drift_patterns.append({
                    "type": "error_frequency_drift",
                    "severity": "warning" if current_freq > baseline_freq * 5 else "info",
                    "error_type": error_type,
                    "baseline_frequency": baseline_freq,
                    "current_frequency": current_freq,
                    "increase_ratio": current_freq / baseline_freq if baseline_freq > 0 else float('inf'),
                    "description": f"{error_type} errors increased {current_freq / baseline_freq:.1f}x"
                })

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
                "metrics": baseline_metrics
            },
            "current_period": {
                "executions": len(current_execs),
                "metrics": current_metrics
            },
            "total_executions_analyzed": total
        }

    @staticmethod
    def _calculate_period_metrics(executions: List[Dict]) -> Dict:
        """Calculate metrics for a period of executions

        Args:
            executions: List of execution records

        Returns:
            Metrics dictionary
        """
        if not executions:
            return {
                "success_rate": 0,
                "avg_duration": 0,
                "error_types": {},
                "execution_count": 0
            }

        success_count = 0
        durations = []
        error_types = defaultdict(int)

        for exec_data in executions:
            # Determine success/failure
            status = exec_data.get("status", exec_data.get("finished", False))
            if status == "success" or status is True:
                success_count += 1
            else:
                # Track error types
                error = exec_data.get("stoppedAt") or exec_data.get("error")
                if error:
                    # Try to extract error type from execution data
                    error_type = DriftDetector._extract_error_type(exec_data)
                    error_types[error_type] += 1

            # Track duration
            started = exec_data.get("startedAt")
            stopped = exec_data.get("stoppedAt")
            if started and stopped:
                try:
                    start_time = datetime.fromisoformat(started.replace('Z', '+00:00'))
                    stop_time = datetime.fromisoformat(stopped.replace('Z', '+00:00'))
                    duration_ms = (stop_time - start_time).total_seconds() * 1000
                    durations.append(duration_ms)
                except:
                    pass

        success_rate = success_count / len(executions) if executions else 0
        avg_duration = statistics.mean(durations) if durations else 0

        return {
            "success_rate": success_rate,
            "avg_duration": avg_duration,
            "error_types": dict(error_types),
            "execution_count": len(executions),
            "duration_stddev": statistics.stdev(durations) if len(durations) > 1 else 0
        }

    @staticmethod
    def _extract_error_type(execution: Dict) -> str:
        """Extract error type from execution data

        Args:
            execution: Execution record

        Returns:
            Error type string
        """
        # Check execution data for error information
        data = execution.get("data", {})

        # Check for top-level error
        if "error" in data:
            error = data["error"]
            message = error.get("message", "")

            # Classify by message patterns
            if "401" in message or "unauthorized" in message.lower():
                return "authentication"
            elif "403" in message or "forbidden" in message.lower():
                return "permission"
            elif "404" in message or "not found" in message.lower():
                return "not_found"
            elif "429" in message or "rate limit" in message.lower():
                return "rate_limit"
            elif "500" in message or "internal server" in message.lower():
                return "server_error"
            elif "timeout" in message.lower() or "timed out" in message.lower():
                return "timeout"
            elif "json" in message.lower() or "parse" in message.lower():
                return "json_parse"
            elif "connection" in message.lower():
                return "connection"
            else:
                return "unknown"

        return "unknown"


class DriftPatternAnalyzer:
    """Analyzes specific drift patterns and provides insights"""

    @staticmethod
    def analyze_pattern(pattern: Dict, executions: List[Dict]) -> Dict:
        """Deep analysis of a specific drift pattern

        Args:
            pattern: Drift pattern from DriftDetector
            executions: Full execution history

        Returns:
            Detailed pattern analysis
        """
        pattern_type = pattern["type"]

        if pattern_type == "success_rate_drift":
            return DriftPatternAnalyzer._analyze_success_rate_drift(pattern, executions)
        elif pattern_type == "performance_drift":
            return DriftPatternAnalyzer._analyze_performance_drift(pattern, executions)
        elif pattern_type == "new_error_pattern":
            return DriftPatternAnalyzer._analyze_new_error_pattern(pattern, executions)
        elif pattern_type == "error_frequency_drift":
            return DriftPatternAnalyzer._analyze_error_frequency_drift(pattern, executions)
        else:
            return {"analysis": "Unknown pattern type"}

    @staticmethod
    def _analyze_success_rate_drift(pattern: Dict, executions: List[Dict]) -> Dict:
        """Analyze success rate drift pattern"""
        # Find when the drift started
        change_point = DriftPatternAnalyzer._find_change_point(
            executions,
            lambda e: e.get("status") == "success" or e.get("finished") is True
        )

        return {
            "pattern_type": "success_rate_drift",
            "severity": pattern["severity"],
            "started_around": change_point["date"] if change_point else "Unknown",
            "change_was_gradual": change_point["gradual"] if change_point else False,
            "potential_causes": [
                "API endpoint changed or deprecated",
                "Authentication requirements changed",
                "New validation rules added",
                "Upstream service experiencing issues",
                "Rate limits were introduced or tightened"
            ],
            "recommendation": "Check recent API changes and compare successful vs failed executions"
        }

    @staticmethod
    def _analyze_performance_drift(pattern: Dict, executions: List[Dict]) -> Dict:
        """Analyze performance drift pattern"""
        change_point = DriftPatternAnalyzer._find_change_point(
            executions,
            lambda e: DriftPatternAnalyzer._get_duration(e)
        )

        return {
            "pattern_type": "performance_drift",
            "severity": pattern["severity"],
            "started_around": change_point["date"] if change_point else "Unknown",
            "change_was_gradual": change_point["gradual"] if change_point else False,
            "potential_causes": [
                "API response times increased",
                "Database performance degraded",
                "Network latency increased",
                "Processing larger data volumes",
                "Resource constraints on server"
            ],
            "recommendation": "Monitor individual node execution times and check external service status"
        }

    @staticmethod
    def _analyze_new_error_pattern(pattern: Dict, executions: List[Dict]) -> Dict:
        """Analyze new error pattern"""
        new_errors = pattern.get("new_errors", [])

        # Find when each new error type first appeared
        first_occurrences = {}
        for error_type in new_errors:
            for exec_data in executions:
                if DriftDetector._extract_error_type(exec_data) == error_type:
                    date = exec_data.get("startedAt", "Unknown")
                    first_occurrences[error_type] = date
                    break

        return {
            "pattern_type": "new_error_pattern",
            "severity": pattern["severity"],
            "new_error_types": new_errors,
            "first_occurrences": first_occurrences,
            "potential_causes": {
                "rate_limit": "API provider added rate limiting",
                "authentication": "Auth method or token format changed",
                "json_parse": "API response format changed",
                "permission": "New permission requirements added",
                "not_found": "Endpoint path or resource IDs changed"
            },
            "recommendation": "Review API provider changelog and test failing requests manually"
        }

    @staticmethod
    def _analyze_error_frequency_drift(pattern: Dict, executions: List[Dict]) -> Dict:
        """Analyze error frequency increase"""
        error_type = pattern.get("error_type", "unknown")

        return {
            "pattern_type": "error_frequency_drift",
            "severity": pattern["severity"],
            "error_type": error_type,
            "increase_ratio": pattern.get("increase_ratio", 1.0),
            "potential_causes": {
                "authentication": ["Token expired", "Auth server issues", "Credentials changed"],
                "rate_limit": ["Increased request volume", "Tighter limits", "Concurrent executions"],
                "timeout": ["API slowdown", "Increased payload size", "Network issues"],
                "server_error": ["Upstream service degradation", "Database issues", "Deploy problems"]
            }.get(error_type, ["Check API health", "Review recent changes"]),
            "recommendation": f"Focus on fixing {error_type} errors - they're the main source of drift"
        }

    @staticmethod
    def _find_change_point(executions: List[Dict], metric_fn) -> Optional[Dict]:
        """Find when a significant change occurred in executions

        Args:
            executions: List of executions
            metric_fn: Function to extract metric from execution

        Returns:
            Change point information or None
        """
        if len(executions) < 4:
            return None

        # Calculate rolling averages
        window_size = max(3, len(executions) // 10)
        averages = []

        for i in range(len(executions) - window_size + 1):
            window = executions[i:i + window_size]
            values = [metric_fn(e) for e in window if metric_fn(e) is not None]
            if values:
                avg = sum(values) / len(values) if isinstance(values[0], (int, float)) else sum(1 for v in values if v) / len(values)
                averages.append((i + window_size // 2, avg))

        if len(averages) < 2:
            return None

        # Find largest jump
        max_change = 0
        change_idx = 0
        for i in range(1, len(averages)):
            change = abs(averages[i][1] - averages[i-1][1])
            if change > max_change:
                max_change = change
                change_idx = averages[i][0]

        if change_idx < len(executions):
            return {
                "index": change_idx,
                "date": executions[change_idx].get("startedAt", "Unknown"),
                "gradual": max_change < (averages[-1][1] - averages[0][1]) / 2
            }

        return None

    @staticmethod
    def _get_duration(execution: Dict) -> Optional[float]:
        """Get execution duration in milliseconds"""
        started = execution.get("startedAt")
        stopped = execution.get("stoppedAt")
        if started and stopped:
            try:
                start_time = datetime.fromisoformat(started.replace('Z', '+00:00'))
                stop_time = datetime.fromisoformat(stopped.replace('Z', '+00:00'))
                return (stop_time - start_time).total_seconds() * 1000
            except:
                pass
        return None


class DriftRootCauseAnalyzer:
    """Analyzes root causes of drift"""

    @staticmethod
    def analyze_root_cause(drift_analysis: Dict, executions: List[Dict], workflow: Dict) -> Dict:
        """Determine root cause of drift

        Args:
            drift_analysis: Output from DriftDetector
            executions: Full execution history
            workflow: Workflow definition

        Returns:
            Root cause analysis
        """
        if not drift_analysis.get("drift_detected"):
            return {"root_cause": "none", "confidence": 1.0}

        patterns = drift_analysis.get("patterns", [])
        if not patterns:
            return {"root_cause": "unknown", "confidence": 0.0}

        # Analyze the most severe pattern
        critical_patterns = [p for p in patterns if p["severity"] == "critical"]
        target_pattern = critical_patterns[0] if critical_patterns else patterns[0]

        pattern_type = target_pattern["type"]

        if pattern_type == "new_error_pattern":
            return DriftRootCauseAnalyzer._analyze_new_error_cause(target_pattern, executions, workflow)
        elif pattern_type == "error_frequency_drift":
            return DriftRootCauseAnalyzer._analyze_frequency_cause(target_pattern, executions, workflow)
        elif pattern_type == "success_rate_drift":
            return DriftRootCauseAnalyzer._analyze_success_drift_cause(target_pattern, executions, workflow)
        elif pattern_type == "performance_drift":
            return DriftRootCauseAnalyzer._analyze_performance_cause(target_pattern, executions, workflow)

        return {"root_cause": "unknown", "confidence": 0.0}

    @staticmethod
    def _analyze_new_error_cause(pattern: Dict, executions: List[Dict], workflow: Dict) -> Dict:
        """Analyze cause of new error types"""
        new_errors = pattern.get("new_errors", [])

        if "rate_limit" in new_errors:
            return {
                "root_cause": "api_rate_limit_introduced",
                "confidence": 0.85,
                "evidence": [
                    "Rate limit (429) errors appeared where none existed before",
                    "Errors likely started after API provider update"
                ],
                "recommended_action": "Add request throttling or implement exponential backoff"
            }

        if "authentication" in new_errors:
            return {
                "root_cause": "authentication_method_changed",
                "confidence": 0.80,
                "evidence": [
                    "Authentication errors suddenly appeared",
                    "Token format or auth method may have changed"
                ],
                "recommended_action": "Review API authentication documentation and update credentials"
            }

        if "json_parse" in new_errors:
            return {
                "root_cause": "api_response_format_changed",
                "confidence": 0.75,
                "evidence": [
                    "JSON parsing errors started occurring",
                    "API response structure likely changed"
                ],
                "recommended_action": "Compare old and new API responses, update field mappings"
            }

        return {
            "root_cause": "api_breaking_change",
            "confidence": 0.60,
            "evidence": [f"New error type appeared: {', '.join(new_errors)}"],
            "recommended_action": "Check API provider changelog and test manually"
        }

    @staticmethod
    def _analyze_frequency_cause(pattern: Dict, executions: List[Dict], workflow: Dict) -> Dict:
        """Analyze cause of error frequency increase"""
        error_type = pattern.get("error_type", "unknown")
        increase = pattern.get("increase_ratio", 1.0)

        if error_type == "rate_limit" and increase > 3:
            return {
                "root_cause": "rate_limit_tightened",
                "confidence": 0.85,
                "evidence": [
                    f"Rate limit errors increased {increase:.1f}x",
                    "API provider likely reduced rate limits"
                ],
                "recommended_action": "Reduce request frequency or implement request queuing"
            }

        if error_type == "authentication" and increase > 5:
            return {
                "root_cause": "credential_expiration",
                "confidence": 0.90,
                "evidence": [
                    f"Auth errors increased {increase:.1f}x",
                    "Credentials may have expired or been revoked"
                ],
                "recommended_action": "Refresh or regenerate API credentials"
            }

        return {
            "root_cause": "increased_failure_rate",
            "confidence": 0.50,
            "evidence": [f"{error_type} errors increased {increase:.1f}x"],
            "recommended_action": "Investigate recent changes and monitor error patterns"
        }

    @staticmethod
    def _analyze_success_drift_cause(pattern: Dict, executions: List[Dict], workflow: Dict) -> Dict:
        """Analyze cause of success rate drift"""
        return {
            "root_cause": "workflow_degradation",
            "confidence": 0.70,
            "evidence": [
                f"Success rate changed by {pattern.get('change_percent', 0):.1f}%",
                "Multiple factors may be contributing"
            ],
            "recommended_action": "Review failed executions and identify common error patterns"
        }

    @staticmethod
    def _analyze_performance_cause(pattern: Dict, executions: List[Dict], workflow: Dict) -> Dict:
        """Analyze cause of performance drift"""
        ratio = pattern.get("change_ratio", 1.0)

        if ratio > 2.0:
            return {
                "root_cause": "external_service_slowdown",
                "confidence": 0.75,
                "evidence": [
                    f"Duration increased {ratio:.1f}x",
                    "External API or database likely slowed down"
                ],
                "recommended_action": "Monitor individual node execution times and check service status"
            }

        return {
            "root_cause": "performance_degradation",
            "confidence": 0.60,
            "evidence": [f"Duration changed by {(ratio - 1) * 100:.1f}%"],
            "recommended_action": "Profile workflow execution and identify slow nodes"
        }


class DriftFixSuggester:
    """Suggests fixes for detected drift"""

    @staticmethod
    def suggest_fixes(root_cause_analysis: Dict, workflow: Dict, drift_patterns: List[Dict]) -> Dict:
        """Generate fix suggestions based on root cause

        Args:
            root_cause_analysis: Output from DriftRootCauseAnalyzer
            workflow: Workflow definition
            drift_patterns: Drift patterns from DriftDetector

        Returns:
            Fix suggestions
        """
        root_cause = root_cause_analysis.get("root_cause", "unknown")

        fixes = []

        if root_cause == "api_rate_limit_introduced":
            fixes.extend(DriftFixSuggester._suggest_rate_limit_fixes(workflow))
        elif root_cause == "authentication_method_changed":
            fixes.extend(DriftFixSuggester._suggest_auth_fixes(workflow))
        elif root_cause == "api_response_format_changed":
            fixes.extend(DriftFixSuggester._suggest_format_change_fixes(workflow))
        elif root_cause == "credential_expiration":
            fixes.extend(DriftFixSuggester._suggest_credential_fixes(workflow))
        elif root_cause == "external_service_slowdown":
            fixes.extend(DriftFixSuggester._suggest_performance_fixes(workflow))
        else:
            # General fixes
            fixes.extend(DriftFixSuggester._suggest_general_fixes(workflow, drift_patterns))

        return {
            "root_cause": root_cause,
            "confidence": root_cause_analysis.get("confidence", 0.5),
            "fixes": fixes,
            "testing_recommendations": [
                "Test fixes in a development environment first",
                "Monitor execution success rate after applying fixes",
                "Compare error patterns before and after changes",
                "Consider adding retry logic for transient failures"
            ]
        }

    @staticmethod
    def _suggest_rate_limit_fixes(workflow: Dict) -> List[Dict]:
        """Suggest fixes for rate limit issues"""
        http_nodes = [n for n in workflow.get("nodes", []) if "http" in n.get("type", "").lower()]

        fixes = []
        for node in http_nodes:
            fixes.append({
                "type": "add_delay",
                "node": node["name"],
                "description": "Add delay between requests to respect rate limits",
                "suggestion": "Add a 'Wait' node before this HTTP request with 1-2 second delay",
                "confidence": 0.85
            })

            fixes.append({
                "type": "add_retry_logic",
                "node": node["name"],
                "description": "Implement exponential backoff for 429 errors",
                "suggestion": "Enable 'Retry On Fail' with exponential backoff in node settings",
                "confidence": 0.90
            })

        fixes.append({
            "type": "batch_requests",
            "description": "Reduce request volume by batching operations",
            "suggestion": "Combine multiple API calls into single batch requests where possible",
            "confidence": 0.70
        })

        return fixes

    @staticmethod
    def _suggest_auth_fixes(workflow: Dict) -> List[Dict]:
        """Suggest fixes for authentication issues"""
        return [
            {
                "type": "update_credentials",
                "description": "Refresh API credentials",
                "suggestion": "Check if API token/key has expired and regenerate in n8n credentials",
                "confidence": 0.90
            },
            {
                "type": "check_auth_format",
                "description": "Verify authentication header format",
                "suggestion": "Check if auth format changed (e.g., 'Bearer' to 'Token' prefix)",
                "confidence": 0.80
            },
            {
                "type": "review_auth_docs",
                "description": "Review API authentication documentation",
                "suggestion": "Check API provider docs for recent auth changes",
                "confidence": 0.75
            }
        ]

    @staticmethod
    def _suggest_format_change_fixes(workflow: Dict) -> List[Dict]:
        """Suggest fixes for response format changes"""
        return [
            {
                "type": "update_field_mappings",
                "description": "Update JSON field paths in expressions",
                "suggestion": "Compare old and new API responses, update {{$json.path}} expressions",
                "confidence": 0.85
            },
            {
                "type": "add_fallback_paths",
                "description": "Add fallback for backward compatibility",
                "suggestion": "Use {{$json.new_path || $json.old_path}} for graceful degradation",
                "confidence": 0.80
            },
            {
                "type": "add_data_validation",
                "description": "Add validation to detect format changes early",
                "suggestion": "Add IF node to check required fields exist before processing",
                "confidence": 0.75
            }
        ]

    @staticmethod
    def _suggest_credential_fixes(workflow: Dict) -> List[Dict]:
        """Suggest fixes for credential expiration"""
        return [
            {
                "type": "regenerate_credentials",
                "description": "Regenerate expired API credentials",
                "suggestion": "Generate new API key/token and update in n8n credentials manager",
                "confidence": 0.95
            },
            {
                "type": "implement_token_refresh",
                "description": "Implement automatic token refresh",
                "suggestion": "Add OAuth refresh flow or token rotation logic",
                "confidence": 0.70
            }
        ]

    @staticmethod
    def _suggest_performance_fixes(workflow: Dict) -> List[Dict]:
        """Suggest fixes for performance issues"""
        return [
            {
                "type": "increase_timeout",
                "description": "Increase request timeout values",
                "suggestion": "Update timeout settings in HTTP Request nodes",
                "confidence": 0.80
            },
            {
                "type": "add_caching",
                "description": "Cache API responses to reduce load",
                "suggestion": "Add caching layer for frequently accessed data",
                "confidence": 0.70
            },
            {
                "type": "optimize_queries",
                "description": "Optimize data queries and reduce payload size",
                "suggestion": "Request only necessary fields, use pagination",
                "confidence": 0.75
            }
        ]

    @staticmethod
    def _suggest_general_fixes(workflow: Dict, patterns: List[Dict]) -> List[Dict]:
        """Suggest general fixes based on patterns"""
        fixes = [
            {
                "type": "add_error_handling",
                "description": "Improve error handling",
                "suggestion": "Add Error Trigger node to catch and handle failures gracefully",
                "confidence": 0.85
            },
            {
                "type": "add_monitoring",
                "description": "Add execution monitoring",
                "suggestion": "Set up alerts for execution failures and drift detection",
                "confidence": 0.80
            }
        ]

        # Check for specific pattern types
        has_performance_issue = any(p["type"] == "performance_drift" for p in patterns)
        if has_performance_issue:
            fixes.append({
                "type": "add_timeout_handling",
                "description": "Handle timeout errors",
                "suggestion": "Enable retry with increased timeout for slow operations",
                "confidence": 0.75
            })

        return fixes
