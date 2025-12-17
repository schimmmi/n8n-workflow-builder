#!/usr/bin/env python3
"""
Schema Drift Analyzer

Detects changes in API response structures, field types, and data schemas over time.
"""

from typing import Dict, List, Set, Optional, Any
from collections import defaultdict
from datetime import datetime
import json


class SchemaDriftAnalyzer:
    """Analyzes schema drift in workflow execution data"""

    @staticmethod
    def analyze_schema_drift(executions: List[Dict]) -> Dict:
        """
        Detect schema changes in execution data over time

        Args:
            executions: List of execution records with output data

        Returns:
            Schema drift analysis with detected changes
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

        # Extract schemas from each period
        baseline_schemas = SchemaDriftAnalyzer._extract_schemas(baseline_execs)
        current_schemas = SchemaDriftAnalyzer._extract_schemas(current_execs)

        # Detect drift patterns
        drift_patterns = []

        # 1. Missing fields (fields that existed in baseline but missing in current)
        for node_name, baseline_fields in baseline_schemas["fields"].items():
            current_fields = current_schemas["fields"].get(node_name, set())
            missing_fields = baseline_fields - current_fields

            if missing_fields:
                drift_patterns.append({
                    "type": "missing_fields",
                    "severity": "critical" if len(missing_fields) > 3 else "warning",
                    "node": node_name,
                    "missing_fields": list(missing_fields),
                    "count": len(missing_fields),
                    "description": f"Node '{node_name}' lost {len(missing_fields)} field(s): {', '.join(list(missing_fields)[:3])}{'...' if len(missing_fields) > 3 else ''}"
                })

        # 2. New fields (fields in current but not in baseline)
        for node_name, current_fields in current_schemas["fields"].items():
            baseline_fields = baseline_schemas["fields"].get(node_name, set())
            new_fields = current_fields - baseline_fields

            if new_fields:
                drift_patterns.append({
                    "type": "new_fields",
                    "severity": "info",
                    "node": node_name,
                    "new_fields": list(new_fields),
                    "count": len(new_fields),
                    "description": f"Node '{node_name}' gained {len(new_fields)} new field(s): {', '.join(list(new_fields)[:3])}{'...' if len(new_fields) > 3 else ''}"
                })

        # 3. Type changes (field exists in both but type changed)
        for node_name in baseline_schemas["types"].keys():
            if node_name in current_schemas["types"]:
                baseline_types = baseline_schemas["types"][node_name]
                current_types = current_schemas["types"][node_name]

                for field in baseline_types.keys():
                    if field in current_types:
                        baseline_type = baseline_types[field]
                        current_type = current_types[field]

                        if baseline_type != current_type:
                            drift_patterns.append({
                                "type": "type_change",
                                "severity": "critical",
                                "node": node_name,
                                "field": field,
                                "baseline_type": baseline_type,
                                "current_type": current_type,
                                "description": f"Field '{field}' in '{node_name}' changed type: {baseline_type} → {current_type}"
                            })

        # 4. Structure changes (nested object structure changed)
        for node_name in baseline_schemas["structures"].keys():
            if node_name in current_schemas["structures"]:
                baseline_structure = baseline_schemas["structures"][node_name]
                current_structure = current_schemas["structures"][node_name]

                if baseline_structure != current_structure:
                    drift_patterns.append({
                        "type": "structure_change",
                        "severity": "warning",
                        "node": node_name,
                        "description": f"Data structure changed in '{node_name}'"
                    })

        # 5. Null value frequency (fields becoming null more often)
        for node_name in baseline_schemas["null_rates"].keys():
            if node_name in current_schemas["null_rates"]:
                baseline_nulls = baseline_schemas["null_rates"][node_name]
                current_nulls = current_schemas["null_rates"][node_name]

                for field in baseline_nulls.keys():
                    if field in current_nulls:
                        baseline_rate = baseline_nulls[field]
                        current_rate = current_nulls[field]

                        # Increased null rate by > 20%
                        if current_rate > baseline_rate + 0.2:
                            drift_patterns.append({
                                "type": "increased_null_rate",
                                "severity": "warning",
                                "node": node_name,
                                "field": field,
                                "baseline_null_rate": baseline_rate,
                                "current_null_rate": current_rate,
                                "increase_percent": (current_rate - baseline_rate) * 100,
                                "description": f"Field '{field}' in '{node_name}' null rate increased from {baseline_rate:.1%} to {current_rate:.1%}"
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
                "nodes_analyzed": len(baseline_schemas["fields"])
            },
            "current_period": {
                "executions": len(current_execs),
                "nodes_analyzed": len(current_schemas["fields"])
            },
            "summary": {
                "missing_fields": sum(1 for p in drift_patterns if p["type"] == "missing_fields"),
                "new_fields": sum(1 for p in drift_patterns if p["type"] == "new_fields"),
                "type_changes": sum(1 for p in drift_patterns if p["type"] == "type_change"),
                "null_rate_increases": sum(1 for p in drift_patterns if p["type"] == "increased_null_rate")
            }
        }

    @staticmethod
    def _extract_schemas(executions: List[Dict]) -> Dict:
        """
        Extract schema information from executions

        Returns:
            Dict with fields, types, structures, and null rates per node
        """
        # Track fields per node
        node_fields = defaultdict(set)
        # Track types per field per node
        node_types = defaultdict(lambda: defaultdict(set))
        # Track structure depth per node
        node_structures = defaultdict(set)
        # Track null occurrences per field per node
        node_field_counts = defaultdict(lambda: defaultdict(int))
        node_field_nulls = defaultdict(lambda: defaultdict(int))

        for execution in executions:
            # Extract node output data
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

                    # Process each output item
                    for output_item in node_outputs:
                        if not isinstance(output_item, dict):
                            continue

                        # Get JSON data
                        json_data = output_item.get("json", {})
                        if not isinstance(json_data, dict):
                            continue

                        # Extract fields and types
                        SchemaDriftAnalyzer._extract_fields_recursive(
                            json_data,
                            node_name,
                            "",
                            node_fields,
                            node_types,
                            node_structures,
                            node_field_counts,
                            node_field_nulls
                        )

        # Calculate null rates
        node_null_rates = {}
        for node_name in node_field_counts.keys():
            null_rates = {}
            for field in node_field_counts[node_name].keys():
                total_count = node_field_counts[node_name][field]
                null_count = node_field_nulls[node_name][field]
                null_rates[field] = null_count / total_count if total_count > 0 else 0
            node_null_rates[node_name] = null_rates

        # Convert types to most common type
        simplified_types = {}
        for node_name in node_types.keys():
            simplified_types[node_name] = {}
            for field in node_types[node_name].keys():
                types = list(node_types[node_name][field])
                # Use first seen type (could be improved with voting)
                simplified_types[node_name][field] = types[0] if types else "unknown"

        return {
            "fields": dict(node_fields),
            "types": simplified_types,
            "structures": dict(node_structures),
            "null_rates": node_null_rates
        }

    @staticmethod
    def _extract_fields_recursive(
        data: Any,
        node_name: str,
        prefix: str,
        node_fields: Dict,
        node_types: Dict,
        node_structures: Dict,
        node_field_counts: Dict,
        node_field_nulls: Dict,
        max_depth: int = 5,
        current_depth: int = 0
    ):
        """Recursively extract fields, types, and track nulls"""
        if current_depth >= max_depth:
            return

        if isinstance(data, dict):
            for key, value in data.items():
                field_name = f"{prefix}.{key}" if prefix else key
                node_fields[node_name].add(field_name)
                node_field_counts[node_name][field_name] += 1

                if value is None:
                    node_field_nulls[node_name][field_name] += 1
                    node_types[node_name][field_name].add("null")
                elif isinstance(value, bool):
                    node_types[node_name][field_name].add("boolean")
                elif isinstance(value, int):
                    node_types[node_name][field_name].add("integer")
                elif isinstance(value, float):
                    node_types[node_name][field_name].add("float")
                elif isinstance(value, str):
                    node_types[node_name][field_name].add("string")
                elif isinstance(value, list):
                    node_types[node_name][field_name].add("array")
                    if value:
                        # Recurse into first array item to get element schema
                        SchemaDriftAnalyzer._extract_fields_recursive(
                            value[0],
                            node_name,
                            f"{field_name}[]",
                            node_fields,
                            node_types,
                            node_structures,
                            node_field_counts,
                            node_field_nulls,
                            max_depth,
                            current_depth + 1
                        )
                elif isinstance(value, dict):
                    node_types[node_name][field_name].add("object")
                    node_structures[node_name].add(field_name)
                    # Recurse into nested object
                    SchemaDriftAnalyzer._extract_fields_recursive(
                        value,
                        node_name,
                        field_name,
                        node_fields,
                        node_types,
                        node_structures,
                        node_field_counts,
                        node_field_nulls,
                        max_depth,
                        current_depth + 1
                    )

        elif isinstance(data, list):
            if data:
                # Process first item as representative
                SchemaDriftAnalyzer._extract_fields_recursive(
                    data[0],
                    node_name,
                    prefix,
                    node_fields,
                    node_types,
                    node_structures,
                    node_field_counts,
                    node_field_nulls,
                    max_depth,
                    current_depth
                )

    @staticmethod
    def suggest_schema_fixes(drift_analysis: Dict, workflow: Dict) -> List[Dict]:
        """
        Suggest fixes for schema drift issues

        Args:
            drift_analysis: Output from analyze_schema_drift
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

            if pattern_type == "missing_fields":
                fixes.append({
                    "type": "add_fallback_handling",
                    "node": pattern["node"],
                    "fields": pattern["missing_fields"],
                    "severity": pattern["severity"],
                    "description": f"Add null checks for missing fields in '{pattern['node']}'",
                    "suggestion": f"Use expressions like {{{{ $json.{pattern['missing_fields'][0]} ?? 'default' }}}} to handle missing fields",
                    "confidence": 0.90
                })

            elif pattern_type == "type_change":
                fixes.append({
                    "type": "add_type_conversion",
                    "node": pattern["node"],
                    "field": pattern["field"],
                    "severity": pattern["severity"],
                    "description": f"Convert field type in '{pattern['node']}'",
                    "suggestion": f"Add type conversion for '{pattern['field']}': {pattern['baseline_type']} → {pattern['current_type']}",
                    "confidence": 0.85
                })

            elif pattern_type == "increased_null_rate":
                fixes.append({
                    "type": "add_null_handling",
                    "node": pattern["node"],
                    "field": pattern["field"],
                    "severity": pattern["severity"],
                    "description": f"Handle increased null values in '{pattern['node']}.{pattern['field']}'",
                    "suggestion": f"Field is null {pattern['current_null_rate']:.1%} of the time - add null checks or default values",
                    "confidence": 0.80
                })

        # Add general recommendations
        if any(p["type"] == "missing_fields" for p in patterns):
            fixes.append({
                "type": "add_schema_validation",
                "description": "Add schema validation to detect API changes early",
                "suggestion": "Add an IF node to validate required fields exist before processing",
                "confidence": 0.85
            })

        return fixes
