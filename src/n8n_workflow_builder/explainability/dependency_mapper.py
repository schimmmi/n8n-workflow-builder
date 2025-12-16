"""
Dependency Mapper - Maps internal and external dependencies

Analyzes:
- Internal dependencies (other workflows, credentials, n8n features)
- External dependencies (APIs, databases, services)
- Single points of failure
- Critical credentials
- Service health dependencies
"""

from typing import Dict, List, Set, Optional
import re


class DependencyMapper:
    """Maps workflow dependencies (internal and external)"""

    # External service patterns
    EXTERNAL_SERVICES = {
        "slack": {"name": "Slack", "type": "messaging"},
        "telegram": {"name": "Telegram", "type": "messaging"},
        "discord": {"name": "Discord", "type": "messaging"},
        "github": {"name": "GitHub", "type": "version_control"},
        "gitlab": {"name": "GitLab", "type": "version_control"},
        "stripe": {"name": "Stripe", "type": "payment"},
        "paypal": {"name": "PayPal", "type": "payment"},
        "shopify": {"name": "Shopify", "type": "e-commerce"},
        "woocommerce": {"name": "WooCommerce", "type": "e-commerce"},
        "aws": {"name": "AWS", "type": "cloud"},
        "google": {"name": "Google Cloud/Workspace", "type": "cloud"},
        "azure": {"name": "Azure", "type": "cloud"},
        "postgres": {"name": "PostgreSQL", "type": "database"},
        "mysql": {"name": "MySQL", "type": "database"},
        "mongodb": {"name": "MongoDB", "type": "database"},
        "redis": {"name": "Redis", "type": "cache"},
        "elasticsearch": {"name": "Elasticsearch", "type": "search"},
        "jira": {"name": "Jira", "type": "project_management"},
        "asana": {"name": "Asana", "type": "project_management"},
        "trello": {"name": "Trello", "type": "project_management"},
        "salesforce": {"name": "Salesforce", "type": "crm"},
        "hubspot": {"name": "HubSpot", "type": "crm"},
        "zendesk": {"name": "Zendesk", "type": "support"},
        "intercom": {"name": "Intercom", "type": "support"},
        "mailchimp": {"name": "Mailchimp", "type": "email_marketing"},
        "sendgrid": {"name": "SendGrid", "type": "email"},
        "twilio": {"name": "Twilio", "type": "communications"},
    }

    @staticmethod
    def map_dependencies(workflow: Dict, all_workflows: Optional[List[Dict]] = None) -> Dict:
        """
        Map all workflow dependencies

        Args:
            workflow: The workflow to analyze
            all_workflows: Optional list of all workflows for cross-workflow dependency detection

        Returns:
            {
                "internal_dependencies": List[Dict],
                "external_dependencies": List[Dict],
                "credentials": List[Dict],
                "single_points_of_failure": List[Dict],
                "dependency_graph": Dict,
                "risk_assessment": Dict
            }
        """
        nodes = workflow.get("nodes", [])

        # Map internal dependencies
        internal_deps = DependencyMapper._map_internal_dependencies(workflow, all_workflows or [])

        # Map external dependencies
        external_deps = DependencyMapper._map_external_dependencies(nodes)

        # Map credentials
        credentials = DependencyMapper._map_credentials(nodes)

        # Identify single points of failure
        spofs = DependencyMapper._identify_single_points_of_failure(
            external_deps, credentials, nodes
        )

        # Build dependency graph
        dependency_graph = DependencyMapper._build_dependency_graph(
            internal_deps, external_deps, credentials
        )

        # Assess dependency risks
        risk_assessment = DependencyMapper._assess_dependency_risks(
            external_deps, credentials, spofs
        )

        return {
            "internal_dependencies": internal_deps,
            "external_dependencies": external_deps,
            "credentials": credentials,
            "single_points_of_failure": spofs,
            "dependency_graph": dependency_graph,
            "risk_assessment": risk_assessment,
            "summary": DependencyMapper._generate_summary(
                internal_deps, external_deps, credentials, spofs
            ),
        }

    @staticmethod
    def _map_internal_dependencies(workflow: Dict, all_workflows: List[Dict]) -> List[Dict]:
        """Map internal n8n dependencies"""
        dependencies = []
        nodes = workflow.get("nodes", [])

        # Check for Execute Workflow nodes (calling other workflows)
        for node in nodes:
            node_type = node.get("type", "")
            node_name = node.get("name", "")
            node_params = node.get("parameters", {})

            if "executeworkflow" in node_type.lower():
                workflow_id = node_params.get("workflowId", "")
                workflow_name = node_params.get("workflowName", "")

                # Try to find the referenced workflow
                referenced_workflow = None
                if all_workflows:
                    for wf in all_workflows:
                        if wf.get("id") == workflow_id or wf.get("name") == workflow_name:
                            referenced_workflow = wf
                            break

                dependencies.append({
                    "type": "workflow_call",
                    "node_name": node_name,
                    "target_workflow_id": workflow_id,
                    "target_workflow_name": workflow_name or "Unknown",
                    "found": referenced_workflow is not None,
                    "criticality": "high",
                })

            # Check for Wait nodes (timing dependencies)
            elif "wait" in node_type.lower():
                dependencies.append({
                    "type": "timing",
                    "node_name": node_name,
                    "description": "Introduces timing dependency",
                    "criticality": "low",
                })

            # Check for Error Trigger nodes (error handling workflows)
            elif "errortrigger" in node_type.lower():
                dependencies.append({
                    "type": "error_handler",
                    "node_name": node_name,
                    "description": "Depends on error events from other workflows",
                    "criticality": "medium",
                })

        # Check for n8n feature dependencies
        settings = workflow.get("settings", {})

        # Timezone dependency
        if settings.get("timezone"):
            dependencies.append({
                "type": "n8n_feature",
                "feature": "timezone",
                "value": settings["timezone"],
                "criticality": "low",
            })

        # Error workflow dependency
        if settings.get("errorWorkflow"):
            dependencies.append({
                "type": "error_workflow",
                "target_workflow_id": settings["errorWorkflow"],
                "criticality": "high",
            })

        return dependencies

    @staticmethod
    def _map_external_dependencies(nodes: List[Dict]) -> List[Dict]:
        """Map external service dependencies"""
        dependencies = []
        seen_services = set()

        for node in nodes:
            node_type = node.get("type", "").lower()
            node_name = node.get("name", "")
            node_params = node.get("parameters", {})

            # Identify service from node type
            service_info = None
            for pattern, info in DependencyMapper.EXTERNAL_SERVICES.items():
                if pattern in node_type:
                    service_info = info
                    service_key = pattern
                    break

            if service_info:
                # Avoid duplicates
                if service_key not in seen_services:
                    seen_services.add(service_key)

                    # Extract service-specific details
                    details = {
                        "service_name": service_info["name"],
                        "service_type": service_info["type"],
                        "node_name": node_name,
                        "node_type": node_type,
                    }

                    # Add URL/endpoint if available
                    if "httprequest" in node_type:
                        url = node_params.get("url", "")
                        details["endpoint"] = url
                        # Try to extract domain
                        domain_match = re.search(r'https?://([^/]+)', url)
                        if domain_match:
                            details["domain"] = domain_match.group(1)
                            # Override service name with domain
                            details["service_name"] = domain_match.group(1)

                    # Add database-specific info
                    elif any(db in node_type for db in ["postgres", "mysql", "mongo", "redis"]):
                        details["database"] = node_params.get("database", "")
                        details["host"] = node_params.get("host", "")

                    dependencies.append(details)

            # Check for generic HTTP requests (external APIs)
            elif "httprequest" in node_type:
                url = node_params.get("url", "")
                if url:
                    domain_match = re.search(r'https?://([^/]+)', url)
                    if domain_match:
                        domain = domain_match.group(1)
                        if domain not in seen_services:
                            seen_services.add(domain)
                            dependencies.append({
                                "service_name": domain,
                                "service_type": "external_api",
                                "node_name": node_name,
                                "endpoint": url,
                                "domain": domain,
                            })

        return dependencies

    @staticmethod
    def _map_credentials(nodes: List[Dict]) -> List[Dict]:
        """Map credential dependencies"""
        credentials = []
        seen_creds = set()

        for node in nodes:
            node_credentials = node.get("credentials", {})

            for cred_type, cred_info in node_credentials.items():
                cred_id = cred_info.get("id", "")
                cred_name = cred_info.get("name", "")

                # Avoid duplicates
                cred_key = f"{cred_type}:{cred_id}"
                if cred_key not in seen_creds:
                    seen_creds.add(cred_key)

                    credentials.append({
                        "credential_type": cred_type,
                        "credential_id": cred_id,
                        "credential_name": cred_name or "Unnamed",
                        "used_by_nodes": [node.get("name", "")],
                        "criticality": DependencyMapper._assess_credential_criticality(cred_type),
                    })
                else:
                    # Add node to existing credential
                    for cred in credentials:
                        if f"{cred['credential_type']}:{cred['credential_id']}" == cred_key:
                            cred["used_by_nodes"].append(node.get("name", ""))
                            break

        return credentials

    @staticmethod
    def _assess_credential_criticality(cred_type: str) -> str:
        """Assess criticality of credential type"""
        high_criticality = ["database", "postgres", "mysql", "mongodb", "aws", "stripe", "paypal"]
        medium_criticality = ["slack", "github", "jira", "salesforce"]

        cred_type_lower = cred_type.lower()

        if any(pattern in cred_type_lower for pattern in high_criticality):
            return "high"
        elif any(pattern in cred_type_lower for pattern in medium_criticality):
            return "medium"
        else:
            return "low"

    @staticmethod
    def _identify_single_points_of_failure(
        external_deps: List[Dict],
        credentials: List[Dict],
        nodes: List[Dict]
    ) -> List[Dict]:
        """Identify single points of failure"""
        spofs = []

        # External services used by many nodes
        service_usage = {}
        for dep in external_deps:
            service_name = dep.get("service_name", "")
            if service_name not in service_usage:
                service_usage[service_name] = []
            service_usage[service_name].append(dep.get("node_name", ""))

        for service_name, node_names in service_usage.items():
            if len(node_names) >= 2:  # Used by 2+ nodes
                spofs.append({
                    "type": "external_service",
                    "service": service_name,
                    "affected_nodes": node_names,
                    "impact": f"Failure would affect {len(node_names)} node(s)",
                    "severity": "high" if len(node_names) >= 3 else "medium",
                })

        # Critical credentials used by many nodes
        for cred in credentials:
            if len(cred["used_by_nodes"]) >= 2 and cred["criticality"] == "high":
                spofs.append({
                    "type": "credential",
                    "credential_name": cred["credential_name"],
                    "credential_type": cred["credential_type"],
                    "affected_nodes": cred["used_by_nodes"],
                    "impact": f"Credential expiry/revocation would affect {len(cred['used_by_nodes'])} node(s)",
                    "severity": "high",
                })

        # Single trigger node (if workflow has only one trigger)
        trigger_nodes = [n for n in nodes if n.get("type", "").endswith("Trigger")]
        if len(trigger_nodes) == 1:
            spofs.append({
                "type": "single_trigger",
                "node_name": trigger_nodes[0].get("name", ""),
                "impact": "Workflow has only one trigger - if it fails, workflow cannot execute",
                "severity": "medium",
            })

        return spofs

    @staticmethod
    def _build_dependency_graph(
        internal_deps: List[Dict],
        external_deps: List[Dict],
        credentials: List[Dict]
    ) -> Dict:
        """Build dependency graph"""
        graph = {
            "nodes": [],
            "edges": [],
        }

        # Add workflow as root node
        graph["nodes"].append({
            "id": "workflow",
            "type": "workflow",
            "label": "This Workflow",
        })

        # Add internal dependencies as nodes
        for dep in internal_deps:
            if dep["type"] == "workflow_call":
                node_id = f"workflow_{dep['target_workflow_id']}"
                graph["nodes"].append({
                    "id": node_id,
                    "type": "workflow",
                    "label": dep["target_workflow_name"],
                })
                graph["edges"].append({
                    "from": "workflow",
                    "to": node_id,
                    "label": "calls",
                })

        # Add external dependencies as nodes
        for idx, dep in enumerate(external_deps):
            node_id = f"external_{idx}"
            graph["nodes"].append({
                "id": node_id,
                "type": "external_service",
                "label": dep["service_name"],
                "service_type": dep.get("service_type", ""),
            })
            graph["edges"].append({
                "from": "workflow",
                "to": node_id,
                "label": "depends on",
            })

        # Add credentials as nodes
        for idx, cred in enumerate(credentials):
            node_id = f"credential_{idx}"
            graph["nodes"].append({
                "id": node_id,
                "type": "credential",
                "label": cred["credential_name"],
                "criticality": cred["criticality"],
            })
            graph["edges"].append({
                "from": "workflow",
                "to": node_id,
                "label": "requires",
            })

        return graph

    @staticmethod
    def _assess_dependency_risks(
        external_deps: List[Dict],
        credentials: List[Dict],
        spofs: List[Dict]
    ) -> Dict:
        """Assess overall dependency risks"""
        risks = []

        # Risk from number of external dependencies
        if len(external_deps) > 5:
            risks.append({
                "risk": "high_external_dependency_count",
                "severity": "medium",
                "description": f"Workflow depends on {len(external_deps)} external services",
                "mitigation": "Consider reducing external dependencies or adding fallback mechanisms",
            })

        # Risk from high-criticality credentials
        high_crit_creds = [c for c in credentials if c["criticality"] == "high"]
        if high_crit_creds:
            risks.append({
                "risk": "high_criticality_credentials",
                "severity": "high",
                "description": f"{len(high_crit_creds)} high-criticality credential(s) in use",
                "mitigation": "Ensure credentials are securely stored and regularly rotated",
            })

        # Risk from SPOFs
        if spofs:
            risks.append({
                "risk": "single_points_of_failure",
                "severity": "high",
                "description": f"{len(spofs)} single point(s) of failure identified",
                "mitigation": "Add redundancy or fallback mechanisms for critical dependencies",
            })

        # Overall risk level
        if any(r["severity"] == "high" for r in risks):
            overall_risk = "high"
        elif risks:
            overall_risk = "medium"
        else:
            overall_risk = "low"

        return {
            "overall_risk": overall_risk,
            "risks": risks,
            "risk_count": len(risks),
        }

    @staticmethod
    def _generate_summary(
        internal_deps: List[Dict],
        external_deps: List[Dict],
        credentials: List[Dict],
        spofs: List[Dict]
    ) -> str:
        """Generate human-readable summary"""
        parts = []

        # Internal dependencies
        if internal_deps:
            workflow_calls = [d for d in internal_deps if d["type"] == "workflow_call"]
            if workflow_calls:
                parts.append(f"Calls {len(workflow_calls)} other workflow(s)")

        # External dependencies
        if external_deps:
            service_types = set(d.get("service_type", "unknown") for d in external_deps)
            parts.append(f"Depends on {len(external_deps)} external service(s): {', '.join(service_types)}")
        else:
            parts.append("No external service dependencies")

        # Credentials
        if credentials:
            parts.append(f"Requires {len(credentials)} credential(s)")
            high_crit = [c for c in credentials if c["criticality"] == "high"]
            if high_crit:
                parts.append(f"{len(high_crit)} high-criticality credential(s)")

        # SPOFs
        if spofs:
            parts.append(f"⚠️  {len(spofs)} single point(s) of failure identified")

        if not parts:
            return "No significant dependencies identified"

        return ". ".join(parts) + "."
