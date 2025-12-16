"""
Change Impact Analyzer - Analyzes the impact of workflow changes

Analyzes impact on:
- Data flow (what changes in data movement)
- Execution behavior (performance, reliability)
- Dependencies (new services, credentials)
- Trigger behavior (how workflow is activated)
- Downstream workflows (workflows that depend on this one)
"""

from typing import Dict, List, Optional


class ChangeImpactAnalyzer:
    """Analyzes the impact of proposed workflow changes"""

    @staticmethod
    def analyze_impact(
        diff: Dict,
        old_workflow: Dict,
        new_workflow: Dict,
        all_workflows: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Analyze the impact of workflow changes

        Returns:
            {
                "data_flow_impact": Dict,
                "execution_impact": Dict,
                "dependency_impact": Dict,
                "trigger_impact": Dict,
                "downstream_impact": Dict,
                "overall_risk_score": float,
                "recommendations": List[str]
            }
        """
        # Analyze different impact dimensions
        data_flow_impact = ChangeImpactAnalyzer._analyze_data_flow_impact(diff, old_workflow, new_workflow)
        execution_impact = ChangeImpactAnalyzer._analyze_execution_impact(diff)
        dependency_impact = ChangeImpactAnalyzer._analyze_dependency_impact(diff, old_workflow, new_workflow)
        trigger_impact = ChangeImpactAnalyzer._analyze_trigger_impact(diff, old_workflow, new_workflow)
        downstream_impact = ChangeImpactAnalyzer._analyze_downstream_impact(
            old_workflow, new_workflow, all_workflows or []
        )

        # Calculate overall risk score
        overall_risk_score = ChangeImpactAnalyzer._calculate_overall_risk(
            diff,
            data_flow_impact,
            execution_impact,
            dependency_impact,
            trigger_impact,
            downstream_impact
        )

        # Generate recommendations
        recommendations = ChangeImpactAnalyzer._generate_recommendations(
            diff,
            data_flow_impact,
            execution_impact,
            dependency_impact,
            trigger_impact,
            downstream_impact
        )

        return {
            "data_flow_impact": data_flow_impact,
            "execution_impact": execution_impact,
            "dependency_impact": dependency_impact,
            "trigger_impact": trigger_impact,
            "downstream_impact": downstream_impact,
            "overall_risk_score": round(overall_risk_score, 2),
            "risk_level": ChangeImpactAnalyzer._risk_level_from_score(overall_risk_score),
            "recommendations": recommendations,
        }

    @staticmethod
    def _analyze_data_flow_impact(diff: Dict, old_workflow: Dict, new_workflow: Dict) -> Dict:
        """Analyze impact on data flow"""
        impacts = []

        # Added connections = new data paths
        added_conns = diff["connections"]["added"]
        if added_conns:
            impacts.append({
                "type": "new_data_paths",
                "count": len(added_conns),
                "description": f"{len(added_conns)} new data path(s) created",
                "severity": "low",
            })

        # Removed connections = broken data paths
        removed_conns = diff["connections"]["removed"]
        if removed_conns:
            impacts.append({
                "type": "broken_data_paths",
                "count": len(removed_conns),
                "description": f"{len(removed_conns)} data path(s) removed",
                "severity": "high",
                "affected_paths": removed_conns,
            })

        # Modified nodes that are transformers
        for mod in diff["nodes"]["modified"]:
            node_type = mod["new"].get("type", "")
            if any(t in node_type.lower() for t in ["function", "code", "set", "filter", "merge"]):
                impacts.append({
                    "type": "data_transformation_changed",
                    "node": mod["node_name"],
                    "description": f"Data transformation logic in '{mod['node_name']}' was modified",
                    "severity": "medium",
                })

        return {
            "impacts": impacts,
            "has_breaking_changes": any(i["severity"] == "high" for i in impacts),
            "summary": f"{len(impacts)} data flow impact(s) detected",
        }

    @staticmethod
    def _analyze_execution_impact(diff: Dict) -> Dict:
        """Analyze impact on execution behavior"""
        impacts = []

        # Adding nodes = more execution time
        added_nodes = diff["nodes"]["added"]
        if len(added_nodes) > 2:
            impacts.append({
                "type": "increased_execution_time",
                "count": len(added_nodes),
                "description": f"{len(added_nodes)} new node(s) will increase execution time",
                "severity": "low",
            })

        # Removing nodes = faster but maybe broken
        removed_nodes = diff["nodes"]["removed"]
        if removed_nodes:
            impacts.append({
                "type": "execution_path_changed",
                "count": len(removed_nodes),
                "description": f"{len(removed_nodes)} node(s) removed from execution path",
                "severity": "medium",
            })

        # Check for added retry/error handling = better reliability
        for node in added_nodes:
            node_type = node.get("type", "").lower()
            if "error" in node_type or "retry" in node_type:
                impacts.append({
                    "type": "improved_reliability",
                    "node": node["name"],
                    "description": f"Added error handling/retry node: {node['name']}",
                    "severity": "positive",
                })

        # Check for removed error handling = worse reliability
        for node in removed_nodes:
            node_type = node.get("type", "").lower()
            if "error" in node_type:
                impacts.append({
                    "type": "reduced_reliability",
                    "node": node["name"],
                    "description": f"Removed error handling node: {node['name']}",
                    "severity": "high",
                })

        return {
            "impacts": impacts,
            "has_breaking_changes": any(i["severity"] == "high" for i in impacts),
            "summary": f"{len(impacts)} execution impact(s) detected",
        }

    @staticmethod
    def _analyze_dependency_impact(diff: Dict, old_workflow: Dict, new_workflow: Dict) -> Dict:
        """Analyze impact on dependencies"""
        impacts = []

        # Extract dependencies from nodes
        old_deps = ChangeImpactAnalyzer._extract_dependencies(old_workflow.get("nodes", []))
        new_deps = ChangeImpactAnalyzer._extract_dependencies(new_workflow.get("nodes", []))

        # New external services
        new_services = new_deps["services"] - old_deps["services"]
        if new_services:
            impacts.append({
                "type": "new_external_services",
                "services": list(new_services),
                "count": len(new_services),
                "description": f"{len(new_services)} new external service(s) added",
                "severity": "medium",
            })

        # Removed external services
        removed_services = old_deps["services"] - new_deps["services"]
        if removed_services:
            impacts.append({
                "type": "removed_external_services",
                "services": list(removed_services),
                "count": len(removed_services),
                "description": f"{len(removed_services)} external service(s) no longer used",
                "severity": "low",
            })

        # New credentials
        new_creds = new_deps["credentials"] - old_deps["credentials"]
        if new_creds:
            impacts.append({
                "type": "new_credentials_required",
                "credentials": list(new_creds),
                "count": len(new_creds),
                "description": f"{len(new_creds)} new credential(s) required",
                "severity": "high",
            })

        # Removed credentials
        removed_creds = old_deps["credentials"] - new_deps["credentials"]
        if removed_creds:
            impacts.append({
                "type": "credentials_no_longer_needed",
                "credentials": list(removed_creds),
                "count": len(removed_creds),
                "description": f"{len(removed_creds)} credential(s) no longer needed",
                "severity": "low",
            })

        return {
            "impacts": impacts,
            "has_breaking_changes": any(i["severity"] == "high" for i in impacts),
            "summary": f"{len(impacts)} dependency impact(s) detected",
        }

    @staticmethod
    def _extract_dependencies(nodes: List[Dict]) -> Dict:
        """Extract external services and credentials from nodes"""
        services = set()
        credentials = set()

        for node in nodes:
            node_type = node.get("type", "").lower()

            # Extract service from node type
            for service in ["slack", "github", "stripe", "telegram", "email", "http"]:
                if service in node_type:
                    services.add(service)

            # Extract credentials
            node_creds = node.get("credentials", {})
            for cred_type in node_creds.keys():
                credentials.add(cred_type)

        return {
            "services": services,
            "credentials": credentials,
        }

    @staticmethod
    def _analyze_trigger_impact(diff: Dict, old_workflow: Dict, new_workflow: Dict) -> Dict:
        """Analyze impact on workflow trigger"""
        impacts = []

        old_nodes = old_workflow.get("nodes", [])
        new_nodes = new_workflow.get("nodes", [])

        # Find old and new triggers
        old_trigger = next((n for n in old_nodes if "trigger" in n.get("type", "").lower()), None)
        new_trigger = next((n for n in new_nodes if "trigger" in n.get("type", "").lower()), None)

        # Trigger removed
        if old_trigger and not new_trigger:
            impacts.append({
                "type": "trigger_removed",
                "severity": "critical",
                "description": "Workflow trigger was removed - workflow cannot be executed automatically",
                "old_trigger": old_trigger.get("type"),
            })

        # Trigger added
        elif not old_trigger and new_trigger:
            impacts.append({
                "type": "trigger_added",
                "severity": "positive",
                "description": "Workflow trigger was added - workflow can now be executed automatically",
                "new_trigger": new_trigger.get("type"),
            })

        # Trigger changed
        elif old_trigger and new_trigger and old_trigger.get("type") != new_trigger.get("type"):
            impacts.append({
                "type": "trigger_type_changed",
                "severity": "critical",
                "description": f"Trigger changed from {old_trigger.get('type')} to {new_trigger.get('type')}",
                "old_trigger": old_trigger.get("type"),
                "new_trigger": new_trigger.get("type"),
            })

        # Trigger parameters changed
        elif old_trigger and new_trigger:
            old_params = old_trigger.get("parameters", {})
            new_params = new_trigger.get("parameters", {})

            if old_params != new_params:
                impacts.append({
                    "type": "trigger_parameters_changed",
                    "severity": "high",
                    "description": "Trigger configuration was modified",
                })

        return {
            "impacts": impacts,
            "has_breaking_changes": any(i["severity"] in ["critical", "high"] for i in impacts),
            "summary": f"{len(impacts)} trigger impact(s) detected",
        }

    @staticmethod
    def _analyze_downstream_impact(
        old_workflow: Dict,
        new_workflow: Dict,
        all_workflows: List[Dict]
    ) -> Dict:
        """Analyze impact on workflows that depend on this one"""
        impacts = []

        workflow_id = old_workflow.get("id")
        workflow_name = old_workflow.get("name")

        # Find workflows that call this workflow
        dependent_workflows = []
        for wf in all_workflows:
            if wf.get("id") == workflow_id:
                continue  # Skip self

            # Check if any node calls this workflow
            for node in wf.get("nodes", []):
                if "executeworkflow" in node.get("type", "").lower():
                    params = node.get("parameters", {})
                    target_id = params.get("workflowId")
                    target_name = params.get("workflowName")

                    if target_id == workflow_id or target_name == workflow_name:
                        dependent_workflows.append({
                            "workflow_id": wf.get("id"),
                            "workflow_name": wf.get("name"),
                            "calling_node": node.get("name"),
                        })

        if dependent_workflows:
            impacts.append({
                "type": "affects_downstream_workflows",
                "count": len(dependent_workflows),
                "severity": "high",
                "description": f"Changes will affect {len(dependent_workflows)} workflow(s) that call this workflow",
                "affected_workflows": dependent_workflows,
            })

        return {
            "impacts": impacts,
            "has_breaking_changes": any(i["severity"] == "high" for i in impacts),
            "summary": f"{len(impacts)} downstream impact(s) detected",
        }

    @staticmethod
    def _calculate_overall_risk(
        diff: Dict,
        data_flow_impact: Dict,
        execution_impact: Dict,
        dependency_impact: Dict,
        trigger_impact: Dict,
        downstream_impact: Dict
    ) -> float:
        """Calculate overall risk score (0-10)"""
        risk_score = 0.0

        # Breaking changes = high risk
        if diff["breaking_changes"]:
            risk_score += len(diff["breaking_changes"]) * 2.0

        # Data flow breaking changes
        if data_flow_impact["has_breaking_changes"]:
            risk_score += 1.5

        # Execution breaking changes
        if execution_impact["has_breaking_changes"]:
            risk_score += 1.0

        # Dependency breaking changes (new credentials)
        if dependency_impact["has_breaking_changes"]:
            risk_score += 1.5

        # Trigger changes
        if trigger_impact["has_breaking_changes"]:
            risk_score += 2.5

        # Downstream impact
        if downstream_impact["has_breaking_changes"]:
            risk_score += 1.5

        # Nodes removed = risk
        risk_score += len(diff["nodes"]["removed"]) * 0.5

        # Connections removed = risk
        risk_score += len(diff["connections"]["removed"]) * 0.3

        return min(10.0, risk_score)

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
    def _generate_recommendations(
        diff: Dict,
        data_flow_impact: Dict,
        execution_impact: Dict,
        dependency_impact: Dict,
        trigger_impact: Dict,
        downstream_impact: Dict
    ) -> List[str]:
        """Generate recommendations based on impact analysis"""
        recommendations = []

        # Breaking changes
        if diff["breaking_changes"]:
            recommendations.append("⚠️  Test in staging environment before deploying to production")
            recommendations.append("📢 Notify stakeholders about breaking changes")

        # Trigger changes
        if trigger_impact["has_breaking_changes"]:
            recommendations.append("🔔 Update all systems that depend on this workflow's trigger")
            recommendations.append("📝 Document the trigger behavior change")

        # New dependencies
        for impact in dependency_impact["impacts"]:
            if impact["type"] == "new_credentials_required":
                recommendations.append(f"🔑 Configure {impact['count']} new credential(s) before deployment")

            if impact["type"] == "new_external_services":
                recommendations.append(f"🌐 Verify connectivity to new external service(s): {', '.join(impact['services'])}")

        # Downstream impact
        if downstream_impact["has_breaking_changes"]:
            affected_count = downstream_impact["impacts"][0]["count"]
            recommendations.append(f"⚙️  Review and update {affected_count} downstream workflow(s)")

        # Data flow changes
        if data_flow_impact["has_breaking_changes"]:
            recommendations.append("📊 Verify data flow changes don't break data pipelines")

        # Execution changes
        if execution_impact["has_breaking_changes"]:
            recommendations.append("🧪 Run end-to-end tests to verify execution behavior")

        # Generic recommendations
        if diff["summary"]["total_changes"] > 5:
            recommendations.append("🔍 Consider breaking changes into smaller, incremental updates")

        if not recommendations:
            recommendations.append("✅ Changes appear safe - proceed with deployment")

        return recommendations
