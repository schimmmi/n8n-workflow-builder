#!/usr/bin/env python3
"""
Data Quality Drift Analyzer

Detects degradation in data quality: empty values, invalid formats, completeness issues.
"""

from typing import Dict, List, Optional, Any
from collections import defaultdict
import re
import statistics


class DataQualityDriftAnalyzer:
    """Analyzes data quality drift in workflow outputs"""

    @staticmethod
    def analyze_quality_drift(executions: List[Dict]) -> Dict:
        """
        Detect data quality degradation over time

        Args:
            executions: List of execution records with output data

        Returns:
            Data quality drift analysis
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

        # Extract quality metrics
        baseline_metrics = DataQualityDriftAnalyzer._extract_quality_metrics(baseline_execs)
        current_metrics = DataQualityDriftAnalyzer._extract_quality_metrics(current_execs)

        drift_patterns = []

        # 1. Empty value rate increase
        for node_name in baseline_metrics["empty_rates"].keys():
            if node_name in current_metrics["empty_rates"]:
                baseline_empty = baseline_metrics["empty_rates"][node_name]
                current_empty = current_metrics["empty_rates"][node_name]

                for field in baseline_empty.keys():
                    if field in current_empty:
                        baseline_rate = baseline_empty[field]
                        current_rate = current_empty[field]

                        # Increase of >20% in empty values
                        if current_rate > baseline_rate + 0.2:
                            severity = "critical" if current_rate > 0.5 else "warning"
                            drift_patterns.append({
                                "type": "empty_value_increase",
                                "severity": severity,
                                "node": node_name,
                                "field": field,
                                "baseline_empty_rate": baseline_rate,
                                "current_empty_rate": current_rate,
                                "increase_percent": (current_rate - baseline_rate) * 100,
                                "description": f"Empty values in '{field}' ({node_name}) increased from {baseline_rate:.1%} to {current_rate:.1%}"
                            })

        # 2. Data completeness degradation
        baseline_completeness = baseline_metrics["completeness"]
        current_completeness = current_metrics["completeness"]

        if baseline_completeness > 0:
            completeness_ratio = current_completeness / baseline_completeness
            if completeness_ratio < 0.8:  # >20% decrease
                severity = "critical" if completeness_ratio < 0.6 else "warning"
                drift_patterns.append({
                    "type": "completeness_degradation",
                    "severity": severity,
                    "baseline_completeness": baseline_completeness,
                    "current_completeness": current_completeness,
                    "decrease_percent": (1 - completeness_ratio) * 100,
                    "description": f"Data completeness decreased by {(1 - completeness_ratio) * 100:.1f}%"
                })

        # 3. Format validation failures
        for node_name in baseline_metrics["format_violations"].keys():
            if node_name in current_metrics["format_violations"]:
                baseline_violations = baseline_metrics["format_violations"][node_name]
                current_violations = current_metrics["format_violations"][node_name]

                for field_type in baseline_violations.keys():
                    if field_type in current_violations:
                        baseline_rate = baseline_violations[field_type]
                        current_rate = current_violations[field_type]

                        if current_rate > baseline_rate * 2 and current_rate > 0.1:  # 2x increase and >10%
                            drift_patterns.append({
                                "type": "format_validation_increase",
                                "severity": "warning",
                                "node": node_name,
                                "format_type": field_type,
                                "baseline_violation_rate": baseline_rate,
                                "current_violation_rate": current_rate,
                                "increase_ratio": current_rate / baseline_rate if baseline_rate > 0 else float('inf'),
                                "description": f"{field_type} format violations in '{node_name}' increased from {baseline_rate:.1%} to {current_rate:.1%}"
                            })

        # 4. Data consistency issues
        baseline_consistency = baseline_metrics["consistency_score"]
        current_consistency = current_metrics["consistency_score"]

        if baseline_consistency > 0:
            consistency_ratio = current_consistency / baseline_consistency
            if consistency_ratio < 0.7:  # >30% decrease
                drift_patterns.append({
                    "type": "consistency_degradation",
                    "severity": "warning",
                    "baseline_consistency": baseline_consistency,
                    "current_consistency": current_consistency,
                    "decrease_percent": (1 - consistency_ratio) * 100,
                    "description": f"Data consistency decreased by {(1 - consistency_ratio) * 100:.1f}%"
                })

        # 5. Output size changes
        if baseline_metrics["avg_output_size"] > 0:
            size_ratio = current_metrics["avg_output_size"] / baseline_metrics["avg_output_size"]
            if size_ratio < 0.5:  # >50% decrease (data loss?)
                drift_patterns.append({
                    "type": "output_size_decrease",
                    "severity": "critical",
                    "baseline_avg_size": baseline_metrics["avg_output_size"],
                    "current_avg_size": current_metrics["avg_output_size"],
                    "decrease_percent": (1 - size_ratio) * 100,
                    "description": f"Average output size decreased by {(1 - size_ratio) * 100:.1f}% (possible data loss)"
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
                "completeness": baseline_completeness,
                "consistency_score": baseline_consistency,
                "avg_output_size": baseline_metrics["avg_output_size"]
            },
            "current_period": {
                "executions": len(current_execs),
                "completeness": current_completeness,
                "consistency_score": current_consistency,
                "avg_output_size": current_metrics["avg_output_size"]
            },
            "summary": {
                "empty_value_issues": sum(1 for p in drift_patterns if p["type"] == "empty_value_increase"),
                "completeness_issues": sum(1 for p in drift_patterns if p["type"] == "completeness_degradation"),
                "format_issues": sum(1 for p in drift_patterns if p["type"] == "format_validation_increase"),
                "consistency_issues": sum(1 for p in drift_patterns if p["type"] == "consistency_degradation")
            }
        }

    @staticmethod
    def _extract_quality_metrics(executions: List[Dict]) -> Dict:
        """Extract data quality metrics from executions"""
        # Track empty/null values per field per node
        node_field_counts = defaultdict(lambda: defaultdict(int))
        node_field_empty = defaultdict(lambda: defaultdict(int))

        # Track format violations
        node_format_violations = defaultdict(lambda: defaultdict(int))
        node_format_total = defaultdict(lambda: defaultdict(int))

        # Track output sizes
        output_sizes = []

        # Track completeness (fields present)
        total_fields_expected = 0
        total_fields_present = 0

        # Track consistency (value stability)
        field_value_sets = defaultdict(set)

        for execution in executions:
            data = execution.get("data", {})
            result_data = data.get("resultData", {})

            if not result_data:
                continue

            # Process each node's output
            for run_index, run_data in result_data.items():
                if not isinstance(run_data, dict):
                    continue

                for node_name, node_outputs in run_data.items():
                    if not isinstance(node_outputs, list):
                        continue

                    # Calculate output size
                    output_sizes.append(len(node_outputs))

                    # Process each output item
                    for output_item in node_outputs:
                        if not isinstance(output_item, dict):
                            continue

                        json_data = output_item.get("json", {})
                        if not isinstance(json_data, dict):
                            continue

                        # Analyze fields
                        for field, value in json_data.items():
                            node_field_counts[node_name][field] += 1
                            total_fields_expected += 1

                            # Check if empty
                            if DataQualityDriftAnalyzer._is_empty(value):
                                node_field_empty[node_name][field] += 1
                            else:
                                total_fields_present += 1

                            # Check format violations
                            format_type = DataQualityDriftAnalyzer._detect_format_type(field)
                            if format_type:
                                node_format_total[node_name][format_type] += 1
                                if not DataQualityDriftAnalyzer._validate_format(value, format_type):
                                    node_format_violations[node_name][format_type] += 1

                            # Track value for consistency
                            if isinstance(value, (str, int, float, bool)):
                                field_value_sets[f"{node_name}.{field}"].add(str(value))

        # Calculate empty rates
        empty_rates = {}
        for node_name in node_field_counts.keys():
            empty_rates[node_name] = {}
            for field in node_field_counts[node_name].keys():
                total = node_field_counts[node_name][field]
                empty = node_field_empty[node_name][field]
                empty_rates[node_name][field] = empty / total if total > 0 else 0

        # Calculate format violation rates
        format_violation_rates = {}
        for node_name in node_format_total.keys():
            format_violation_rates[node_name] = {}
            for format_type in node_format_total[node_name].keys():
                total = node_format_total[node_name][format_type]
                violations = node_format_violations[node_name][format_type]
                format_violation_rates[node_name][format_type] = violations / total if total > 0 else 0

        # Calculate completeness
        completeness = total_fields_present / total_fields_expected if total_fields_expected > 0 else 1.0

        # Calculate consistency (lower cardinality = more consistent)
        consistency_scores = []
        for field, values in field_value_sets.items():
            if len(values) > 0:
                # Inverse of cardinality (more unique values = less consistent)
                consistency_scores.append(1.0 / len(values))

        consistency_score = statistics.mean(consistency_scores) if consistency_scores else 1.0

        # Calculate average output size
        avg_output_size = statistics.mean(output_sizes) if output_sizes else 0

        return {
            "empty_rates": dict(empty_rates),
            "format_violations": dict(format_violation_rates),
            "completeness": completeness,
            "consistency_score": consistency_score,
            "avg_output_size": avg_output_size
        }

    @staticmethod
    def _is_empty(value: Any) -> bool:
        """Check if value is considered empty"""
        if value is None:
            return True
        if isinstance(value, str) and value.strip() == "":
            return True
        if isinstance(value, (list, dict)) and len(value) == 0:
            return True
        return False

    @staticmethod
    def _detect_format_type(field_name: str) -> Optional[str]:
        """Detect expected format based on field name"""
        field_lower = field_name.lower()

        if "email" in field_lower:
            return "email"
        elif "phone" in field_lower or "tel" in field_lower:
            return "phone"
        elif "url" in field_lower or "link" in field_lower:
            return "url"
        elif "date" in field_lower:
            return "date"
        elif "zip" in field_lower or "postal" in field_lower:
            return "postal_code"
        elif "ip" in field_lower:
            return "ip_address"

        return None

    @staticmethod
    def _validate_format(value: Any, format_type: str) -> bool:
        """Validate value against expected format"""
        if not isinstance(value, str):
            return False

        if format_type == "email":
            return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value))
        elif format_type == "phone":
            # Simple phone validation
            return bool(re.match(r'^\+?[\d\s\-\(\)]{10,}$', value))
        elif format_type == "url":
            return bool(re.match(r'^https?://', value))
        elif format_type == "date":
            # Check for common date patterns
            return bool(re.match(r'\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}', value))
        elif format_type == "postal_code":
            # US zip or other postal codes
            return bool(re.match(r'^\d{5}(-\d{4})?$|^[A-Z\d]{3,}$', value))
        elif format_type == "ip_address":
            # Simple IP validation
            return bool(re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', value))

        return True  # Unknown format, assume valid

    @staticmethod
    def suggest_quality_fixes(drift_analysis: Dict, workflow: Dict) -> List[Dict]:
        """
        Suggest fixes for data quality drift issues

        Args:
            drift_analysis: Output from analyze_quality_drift
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

            if pattern_type == "empty_value_increase":
                fixes.append({
                    "type": "add_empty_value_handling",
                    "node": pattern["node"],
                    "field": pattern["field"],
                    "severity": pattern["severity"],
                    "description": f"Handle increased empty values in '{pattern['field']}'",
                    "suggestion": f"Add validation: {{{{ $json.{pattern['field']} ? $json.{pattern['field']} : 'default_value' }}}}",
                    "confidence": 0.90
                })

            elif pattern_type == "completeness_degradation":
                fixes.append({
                    "type": "add_completeness_check",
                    "severity": pattern["severity"],
                    "description": "Add data completeness validation",
                    "suggestion": "Add IF node to check required fields exist before processing",
                    "confidence": 0.85
                })

            elif pattern_type == "format_validation_increase":
                fixes.append({
                    "type": "add_format_validation",
                    "node": pattern["node"],
                    "format_type": pattern["format_type"],
                    "severity": pattern["severity"],
                    "description": f"Add {pattern['format_type']} format validation",
                    "suggestion": f"Add validation node to check {pattern['format_type']} format before processing",
                    "confidence": 0.85
                })

            elif pattern_type == "output_size_decrease":
                fixes.append({
                    "type": "investigate_data_loss",
                    "severity": pattern["severity"],
                    "description": "Investigate potential data loss",
                    "suggestion": "Check API pagination, filtering, or query parameters that may have changed",
                    "confidence": 0.80
                })

        # General recommendations
        fixes.append({
            "type": "add_data_quality_monitoring",
            "description": "Add proactive data quality monitoring",
            "suggestion": "Set up alerts for empty value thresholds and format violations",
            "confidence": 0.80
        })

        return fixes
