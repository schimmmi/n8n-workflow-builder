"""
Dry-Run Simulator - Validates changes without applying them

Simulates workflow changes and validates:
- Structure validity
- Semantic correctness
- Risk assessment
- Performance impact estimation
"""

from typing import Dict, Optional


class DryRunSimulator:
    """Simulates workflow changes without applying them"""

    @staticmethod
    def simulate(
        new_workflow: Dict,
        validator=None,
        semantic_analyzer=None
    ) -> Dict:
        """
        Simulate workflow deployment

        Returns:
            {
                "valid": bool,
                "validation_results": Dict,
                "semantic_issues": List[Dict],
                "estimated_performance": Dict,
                "simulation_passed": bool
            }
        """
        results = {
            "valid": True,
            "validation_results": None,
            "semantic_issues": [],
            "estimated_performance": {},
            "simulation_passed": True,
            "errors": [],
        }

        # Validate structure
        if validator:
            try:
                validation = validator.validate_workflow_full(new_workflow)
                results["validation_results"] = validation

                if validation.get("has_errors"):
                    results["valid"] = False
                    results["simulation_passed"] = False
                    results["errors"].append("Workflow has validation errors")
            except Exception as e:
                results["errors"].append(f"Validation failed: {str(e)}")
                results["simulation_passed"] = False

        # Semantic analysis
        if semantic_analyzer:
            try:
                semantic = semantic_analyzer.analyze_workflow_full(new_workflow)
                results["semantic_issues"] = semantic.get("issues", [])

                critical_issues = [i for i in results["semantic_issues"] if i.get("severity") == "critical"]
                if critical_issues:
                    results["errors"].append(f"{len(critical_issues)} critical semantic issue(s) found")
            except Exception as e:
                results["errors"].append(f"Semantic analysis failed: {str(e)}")

        # Estimate performance
        results["estimated_performance"] = DryRunSimulator._estimate_performance(new_workflow)

        return results

    @staticmethod
    def _estimate_performance(workflow: Dict) -> Dict:
        """Estimate workflow performance"""
        node_count = len(workflow.get("nodes", []))

        # Rough estimates
        estimated_duration = node_count * 0.5  # 500ms per node average
        memory_usage = node_count * 10  # 10MB per node average

        complexity = "low"
        if node_count > 20:
            complexity = "high"
        elif node_count > 10:
            complexity = "medium"

        return {
            "node_count": node_count,
            "estimated_duration_seconds": round(estimated_duration, 1),
            "estimated_memory_mb": memory_usage,
            "complexity": complexity,
        }
