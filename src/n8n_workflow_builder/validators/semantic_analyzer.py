#!/usr/bin/env python3
"""
Semantic Workflow Analyzer Module
Deep semantic analysis of workflow logic and anti-patterns
"""
import re
from typing import Dict, List, Set


class SemanticWorkflowAnalyzer:
    """Advanced semantic analysis for workflow logic and patterns"""

    @staticmethod
    def analyze_workflow_semantics(workflow: Dict) -> Dict:
        """Comprehensive semantic analysis of workflow

        Returns:
            Dict with 'issues', 'anti_patterns', 'recommendations', and 'llm_fixes'
        """
        result = {
            'issues': [],
            'anti_patterns': [],
            'recommendations': [],
            'llm_fixes': [],
            'severity': {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0
            }
        }

        nodes = workflow.get('nodes', [])
        connections = workflow.get('connections', {})

        # Run all semantic checks
        SemanticWorkflowAnalyzer._check_http_retry_patterns(nodes, result)
        SemanticWorkflowAnalyzer._check_split_in_batches_completion(nodes, connections, result)
        SemanticWorkflowAnalyzer._check_cron_timezone(nodes, result)
        SemanticWorkflowAnalyzer._check_if_node_default_path(nodes, connections, result)
        SemanticWorkflowAnalyzer._check_webhook_response_patterns(nodes, connections, result)
        SemanticWorkflowAnalyzer._check_loop_safety(nodes, connections, result)
        SemanticWorkflowAnalyzer._check_data_transformation_chains(nodes, connections, result)
        SemanticWorkflowAnalyzer._check_error_handling_completeness(nodes, result)
        SemanticWorkflowAnalyzer._check_credential_usage(nodes, result)
        SemanticWorkflowAnalyzer._check_performance_bottlenecks(nodes, connections, result)
        SemanticWorkflowAnalyzer._check_api_rate_limiting(nodes, result)
        SemanticWorkflowAnalyzer._check_data_validation_patterns(nodes, connections, result)

        return result

    @staticmethod
    def _add_issue(result: Dict, severity: str, category: str, node_name: str,
                   issue: str, explanation: str, llm_fix: str):
        """Add an issue with LLM-friendly fix suggestion"""
        result['issues'].append({
            'severity': severity,
            'category': category,
            'node': node_name,
            'issue': issue,
            'explanation': explanation
        })

        result['llm_fixes'].append({
            'node': node_name,
            'issue': issue,
            'fix': llm_fix,
            'category': category
        })

        result['severity'][severity] += 1

    @staticmethod
    def _check_http_retry_patterns(nodes: List[Dict], result: Dict):
        """Check HTTP Request nodes for missing retry logic"""
        for node in nodes:
            if node.get('type') == 'n8n-nodes-base.httpRequest':
                params = node.get('parameters', {})
                options = params.get('options', {})

                # Check if retry is configured
                if not options.get('retry'):
                    SemanticWorkflowAnalyzer._add_issue(
                        result,
                        severity='high',
                        category='reliability',
                        node_name=node.get('name', 'Unknown'),
                        issue='HTTP Request without retry logic',
                        explanation=(
                            'External API calls can fail due to network issues, rate limits, or '
                            'temporary service unavailability. Without retry logic, the workflow '
                            'will fail immediately on the first error.'
                        ),
                        llm_fix=(
                            f"Add retry configuration to node '{node.get('name')}':\n"
                            "```json\n"
                            "{\n"
                            "  \"parameters\": {\n"
                            "    \"options\": {\n"
                            "      \"retry\": {\n"
                            "        \"maxRetries\": 3,\n"
                            "        \"waitBetweenRetries\": 1000\n"
                            "      }\n"
                            "    }\n"
                            "  }\n"
                            "}\n"
                            "```"
                        )
                    )

                # Check if timeout is set
                if not params.get('timeout') and not options.get('timeout'):
                    SemanticWorkflowAnalyzer._add_issue(
                        result,
                        severity='medium',
                        category='reliability',
                        node_name=node.get('name', 'Unknown'),
                        issue='HTTP Request without timeout',
                        explanation=(
                            'Without a timeout, the request can hang indefinitely if the external '
                            'service becomes unresponsive, blocking the entire workflow execution.'
                        ),
                        llm_fix=(
                            f"Add timeout to node '{node.get('name')}':\n"
                            "```json\n"
                            "{\n"
                            "  \"parameters\": {\n"
                            "    \"timeout\": 30000\n"
                            "  }\n"
                            "}\n"
                            "```\n"
                            "Recommended: 30000ms (30 seconds) for most APIs"
                        )
                    )

    @staticmethod
    def _check_split_in_batches_completion(nodes: List[Dict], connections: Dict, result: Dict):
        """Check SplitInBatches nodes for proper completion"""
        for node in nodes:
            if node.get('type') == 'n8n-nodes-base.splitInBatches':
                node_name = node.get('name', 'Unknown')

                # Check if there's a connection back to complete the loop
                # SplitInBatches requires a loop back connection to process all batches
                has_loop_back = False

                # Check connections from downstream nodes back to this node
                for source, targets in connections.items():
                    if isinstance(targets, dict):
                        for output_type, target_list in targets.items():
                            if isinstance(target_list, list):
                                for target in target_list:
                                    if isinstance(target, dict) and target.get('node') == node_name:
                                        has_loop_back = True
                                        break

                if not has_loop_back:
                    SemanticWorkflowAnalyzer._add_issue(
                        result,
                        severity='critical',
                        category='logic_error',
                        node_name=node_name,
                        issue='SplitInBatches without completion loop',
                        explanation=(
                            'SplitInBatches requires a loop-back connection to process all batches. '
                            'Without it, only the first batch will be processed, and the workflow '
                            'will not complete properly. This is a common mistake that leads to '
                            'incomplete data processing.'
                        ),
                        llm_fix=(
                            f"Fix SplitInBatches loop for node '{node_name}':\n\n"
                            "1. Add processing nodes after SplitInBatches\n"
                            "2. Add a final node that connects BACK to SplitInBatches\n"
                            "3. Configure the connection to trigger on 'Done' output\n\n"
                            "Example structure:\n"
                            "```\n"
                            "SplitInBatches → Process Batch → [Loop Back to SplitInBatches]\n"
                            "                                  ↓ (when all batches done)\n"
                            "                              Continue Workflow\n"
                            "```\n\n"
                            "The loop-back connection must go to the SplitInBatches node itself."
                        )
                    )

    @staticmethod
    def _check_cron_timezone(nodes: List[Dict], result: Dict):
        """Check Schedule Trigger nodes for timezone configuration"""
        for node in nodes:
            if node.get('type') == 'n8n-nodes-base.scheduleTrigger':
                params = node.get('parameters', {})

                # Check if timezone is explicitly set
                if not params.get('timezone'):
                    SemanticWorkflowAnalyzer._add_issue(
                        result,
                        severity='medium',
                        category='configuration',
                        node_name=node.get('name', 'Unknown'),
                        issue='Schedule Trigger without explicit timezone',
                        explanation=(
                            'Without an explicit timezone, the schedule will use the server\'s timezone, '
                            'which can lead to unexpected execution times if the server is in a different '
                            'timezone than expected, or if the server timezone changes (e.g., due to DST or migration).'
                        ),
                        llm_fix=(
                            f"Add timezone to Schedule Trigger '{node.get('name')}':\n"
                            "```json\n"
                            "{\n"
                            "  \"parameters\": {\n"
                            "    \"timezone\": \"Europe/Berlin\",  // or your timezone\n"
                            "    \"rule\": {\n"
                            "      \"interval\": [...]\n"
                            "    }\n"
                            "  }\n"
                            "}\n"
                            "```\n\n"
                            "Common timezones: America/New_York, Europe/London, Asia/Tokyo, UTC"
                        )
                    )

                # Check for ambiguous cron expressions
                cron_expression = params.get('cronExpression', '')
                if cron_expression and '?' in cron_expression:
                    result['recommendations'].append({
                        'node': node.get('name', 'Unknown'),
                        'recommendation': (
                            'Cron expression contains wildcards (?). Consider using explicit values '
                            'for better predictability and debugging.'
                        )
                    })

    @staticmethod
    def _check_if_node_default_path(nodes: List[Dict], connections: Dict, result: Dict):
        """Check IF nodes for missing default/fallback paths"""
        for node in nodes:
            if node.get('type') == 'n8n-nodes-base.if':
                node_name = node.get('name', 'Unknown')

                # Check if node has both true and false outputs connected
                node_connections = connections.get(node_name, {})

                has_true_path = bool(node_connections.get('main', [[]])[0] if node_connections.get('main') else False)
                has_false_path = bool(node_connections.get('main', [[], []])[1] if len(node_connections.get('main', [])) > 1 else False)

                if has_true_path and not has_false_path:
                    SemanticWorkflowAnalyzer._add_issue(
                        result,
                        severity='high',
                        category='logic_error',
                        node_name=node_name,
                        issue='IF node without false path',
                        explanation=(
                            'When an IF condition is false and there\'s no false path, the workflow '
                            'execution stops silently. This can lead to incomplete processing and makes '
                            'debugging difficult. Always handle both branches explicitly.'
                        ),
                        llm_fix=(
                            f"Add false path to IF node '{node_name}':\n\n"
                            "1. Connect the 'false' output to a node (even if just a NoOp or Stop node)\n"
                            "2. Or add logging to track when condition is false\n"
                            "3. Or add a default action for the false case\n\n"
                            "Example: Connect false output to a Set node that logs the reason:\n"
                            "```json\n"
                            "{\n"
                            "  \"type\": \"n8n-nodes-base.set\",\n"
                            "  \"parameters\": {\n"
                            "    \"values\": {\n"
                            "      \"string\": [\n"
                            "        {\n"
                            "          \"name\": \"status\",\n"
                            "          \"value\": \"Condition not met - skipped processing\"\n"
                            "        }\n"
                            "      ]\n"
                            "    }\n"
                            "  }\n"
                            "}\n"
                            "```"
                        )
                    )
                elif not has_true_path and not has_false_path:
                    SemanticWorkflowAnalyzer._add_issue(
                        result,
                        severity='critical',
                        category='logic_error',
                        node_name=node_name,
                        issue='IF node without any output paths',
                        explanation=(
                            'IF node must have at least one output path connected. Without any paths, '
                            'the workflow will always stop at this node, making it non-functional.'
                        ),
                        llm_fix=(
                            f"Connect outputs of IF node '{node_name}':\n\n"
                            "Both true and false outputs should be connected to continue the workflow."
                        )
                    )

    @staticmethod
    def _check_webhook_response_patterns(nodes: List[Dict], connections: Dict, result: Dict):
        """Check Webhook nodes for proper response handling"""
        for node in nodes:
            if node.get('type') == 'n8n-nodes-base.webhook':
                node_name = node.get('name', 'Unknown')
                params = node.get('parameters', {})

                # Check if webhook expects a response
                response_mode = params.get('responseMode', 'onReceived')

                if response_mode == 'lastNode':
                    # Check if there's a clear path to an end node
                    # Find all leaf nodes (nodes with no outgoing connections)
                    all_nodes = {n.get('name'): n for n in nodes}
                    leaf_nodes = []

                    for node_check in nodes:
                        name_check = node_check.get('name')
                        if name_check not in connections or not connections[name_check]:
                            leaf_nodes.append(name_check)

                    if len(leaf_nodes) == 0:
                        SemanticWorkflowAnalyzer._add_issue(
                            result,
                            severity='high',
                            category='logic_error',
                            node_name=node_name,
                            issue='Webhook with lastNode response but no end node',
                            explanation=(
                                'Webhook is configured to respond with data from the last node, '
                                'but the workflow has no clear end point. This can cause timeout '
                                'errors or unexpected responses.'
                            ),
                            llm_fix=(
                                f"Fix webhook response handling for '{node_name}':\n\n"
                                "Option 1: Add explicit Respond to Webhook node at the end\n"
                                "```json\n"
                                "{\n"
                                "  \"type\": \"n8n-nodes-base.respondToWebhook\",\n"
                                "  \"parameters\": {\n"
                                "    \"respondWith\": \"json\",\n"
                                "    \"responseBody\": \"={{$json}}\"\n"
                                "  }\n"
                                "}\n"
                                "```\n\n"
                                "Option 2: Change responseMode to 'onReceived' if immediate response is acceptable"
                            )
                        )

                # Check authentication
                auth_method = params.get('authentication', 'none')
                if auth_method == 'none':
                    SemanticWorkflowAnalyzer._add_issue(
                        result,
                        severity='high',
                        category='security',
                        node_name=node_name,
                        issue='Webhook without authentication',
                        explanation=(
                            'Webhook is publicly accessible without authentication. This is a security '
                            'risk as anyone who discovers the URL can trigger the workflow, potentially '
                            'causing data leaks, resource abuse, or unauthorized actions.'
                        ),
                        llm_fix=(
                            f"Add authentication to webhook '{node_name}':\n\n"
                            "Recommended: Use headerAuth for API key validation\n"
                            "```json\n"
                            "{\n"
                            "  \"parameters\": {\n"
                            "    \"authentication\": \"headerAuth\",\n"
                            "    \"headerAuth\": {\n"
                            "      \"name\": \"X-API-Key\",\n"
                            "      \"value\": \"={{$credentials.apiKey}}\"\n"
                            "    }\n"
                            "  }\n"
                            "}\n"
                            "```\n\n"
                            "Or use other methods: basicAuth, jwtAuth, or custom validation with IF node"
                        )
                    )

    @staticmethod
    def _check_loop_safety(nodes: List[Dict], connections: Dict, result: Dict):
        """Check for infinite loop potential"""
        # Build connection graph
        graph = {}
        for source, targets in connections.items():
            graph[source] = []
            if isinstance(targets, dict):
                for output_type, target_list in targets.items():
                    if isinstance(target_list, list):
                        for target in target_list:
                            if isinstance(target, dict):
                                graph[source].append(target.get('node'))

        # Check for cycles that don't have loop control
        def has_cycle_without_control(node_name, visited, rec_stack, path):
            visited.add(node_name)
            rec_stack.add(node_name)
            path.append(node_name)

            for neighbor in graph.get(node_name, []):
                if neighbor not in visited:
                    if has_cycle_without_control(neighbor, visited, rec_stack, path):
                        return True
                elif neighbor in rec_stack:
                    # Found cycle - check if any node in cycle is SplitInBatches or Loop
                    cycle_nodes = path[path.index(neighbor):]
                    has_loop_control = any(
                        any(n.get('name') == cn and n.get('type') in [
                            'n8n-nodes-base.splitInBatches',
                            'n8n-nodes-base.loop'
                        ] for n in nodes)
                        for cn in cycle_nodes
                    )

                    if not has_loop_control:
                        return True

            path.pop()
            rec_stack.remove(node_name)
            return False

        visited = set()
        for node in nodes:
            node_name = node.get('name')
            if node_name not in visited:
                if has_cycle_without_control(node_name, visited, set(), []):
                    result['anti_patterns'].append({
                        'pattern': 'potential_infinite_loop',
                        'severity': 'critical',
                        'description': (
                            'Detected potential infinite loop in workflow. The workflow has a cycle '
                            'without proper loop control (SplitInBatches or Loop node). This can cause '
                            'the workflow to run indefinitely and consume resources.'
                        ),
                        'recommendation': (
                            'Use SplitInBatches node for controlled iteration or add explicit loop '
                            'exit conditions with IF nodes.'
                        )
                    })
                    result['severity']['critical'] += 1
                    break

    @staticmethod
    def _check_data_transformation_chains(nodes: List[Dict], connections: Dict, result: Dict):
        """Check for inefficient data transformation chains"""
        # Find chains of Set/Function/Code nodes
        transform_node_types = [
            'n8n-nodes-base.set',
            'n8n-nodes-base.function',
            'n8n-nodes-base.code'
        ]

        for node in nodes:
            if node.get('type') in transform_node_types:
                node_name = node.get('name')

                # Check how many consecutive transform nodes follow
                consecutive_count = 1
                current = node_name

                while current in connections:
                    targets = connections[current].get('main', [[]])[0] if connections[current].get('main') else []
                    if len(targets) == 1:
                        next_node_name = targets[0].get('node')
                        next_node = next((n for n in nodes if n.get('name') == next_node_name), None)
                        if next_node and next_node.get('type') in transform_node_types:
                            consecutive_count += 1
                            current = next_node_name
                        else:
                            break
                    else:
                        break

                if consecutive_count >= 3:
                    result['recommendations'].append({
                        'node': node_name,
                        'recommendation': (
                            f'Found {consecutive_count} consecutive data transformation nodes starting '
                            f'at "{node_name}". Consider consolidating these transformations into a '
                            'single Code or Function node for better performance and maintainability.'
                        )
                    })

    @staticmethod
    def _check_error_handling_completeness(nodes: List[Dict], result: Dict):
        """Check if workflow has comprehensive error handling"""
        has_error_trigger = any(n.get('type') == 'n8n-nodes-base.errorTrigger' for n in nodes)

        # Count critical nodes (HTTP, Database, etc.)
        critical_node_types = [
            'n8n-nodes-base.httpRequest',
            'n8n-nodes-base.postgres',
            'n8n-nodes-base.mysql',
            'n8n-nodes-base.redis'
        ]

        critical_nodes = [n for n in nodes if n.get('type') in critical_node_types]

        if len(critical_nodes) >= 2 and not has_error_trigger:
            result['recommendations'].append({
                'node': 'Workflow',
                'recommendation': (
                    f'Workflow has {len(critical_nodes)} nodes that can fail (HTTP requests, database operations) '
                    'but no Error Trigger node for centralized error handling. Consider adding an Error Trigger '
                    'workflow to catch and handle failures gracefully.'
                )
            })

    @staticmethod
    def _check_credential_usage(nodes: List[Dict], result: Dict):
        """Check for proper credential usage"""
        for node in nodes:
            params = node.get('parameters', {})
            params_str = json.dumps(params)

            # Check for hardcoded sensitive data patterns
            sensitive_patterns = [
                (r'api[_-]?key["\s:]+["\'][\w\-]{20,}', 'API key'),
                (r'password["\s:]+["\'][^"\']{3,}', 'password'),
                (r'bearer\s+[\w\-\.]{20,}', 'Bearer token'),
                (r'sk-[\w]{20,}', 'Secret key'),
            ]

            for pattern, name in sensitive_patterns:
                if re.search(pattern, params_str, re.IGNORECASE):
                    # Make sure it's not using credential reference
                    if '{{$credentials' not in params_str:
                        SemanticWorkflowAnalyzer._add_issue(
                            result,
                            severity='critical',
                            category='security',
                            node_name=node.get('name', 'Unknown'),
                            issue=f'Possible hardcoded {name} detected',
                            explanation=(
                                f'Node appears to contain a hardcoded {name}. Hardcoded credentials '
                                'are a severe security risk as they can be exposed in logs, backups, '
                                'or version control. Always use n8n credential system.'
                            ),
                            llm_fix=(
                                f"Replace hardcoded {name} in '{node.get('name')}' with credential reference:\n\n"
                                "1. Create credential in n8n UI (Settings > Credentials)\n"
                                "2. Reference it in the node:\n"
                                "```json\n"
                                "{\n"
                                "  \"credentials\": {\n"
                                "    \"apiKey\": {\n"
                                "      \"id\": \"1\",\n"
                                "      \"name\": \"My API Key\"\n"
                                "    }\n"
                                "  }\n"
                                "}\n"
                                "```\n\n"
                                "Or use expression: {{$credentials.credentialName}}"
                            )
                        )

    @staticmethod
    def _check_performance_bottlenecks(nodes: List[Dict], connections: Dict, result: Dict):
        """Check for common performance bottlenecks"""
        for node in nodes:
            node_type = node.get('type', '')

            # Check for n+1 query pattern (loop with database query inside)
            if node_type in ['n8n-nodes-base.postgres', 'n8n-nodes-base.mysql']:
                # Check if this node is inside a loop
                node_name = node.get('name')

                # Simple heuristic: check if node is downstream from SplitInBatches
                for upstream_node in nodes:
                    if upstream_node.get('type') == 'n8n-nodes-base.splitInBatches':
                        # This is a simplified check - in reality we'd trace connections
                        result['recommendations'].append({
                            'node': node_name,
                            'recommendation': (
                                f'Database query node "{node_name}" may be inside a loop. '
                                'This can cause N+1 query problems and severe performance degradation. '
                                'Consider: 1) Batch the queries, 2) Use a single query with IN clause, '
                                '3) Use JOIN to fetch related data upfront.'
                            )
                        })
                        break

    @staticmethod
    def _check_api_rate_limiting(nodes: List[Dict], result: Dict):
        """Check for proper rate limiting handling"""
        http_nodes = [n for n in nodes if n.get('type') == 'n8n-nodes-base.httpRequest']

        if len(http_nodes) >= 3:
            # Check if any Wait nodes exist between HTTP requests
            has_wait_nodes = any(n.get('type') == 'n8n-nodes-base.wait' for n in nodes)

            if not has_wait_nodes:
                result['recommendations'].append({
                    'node': 'Workflow',
                    'recommendation': (
                        f'Workflow makes {len(http_nodes)} HTTP requests but has no Wait nodes. '
                        'Consider adding delays between requests to respect API rate limits and '
                        'avoid 429 (Too Many Requests) errors.'
                    )
                })

    @staticmethod
    def _check_data_validation_patterns(nodes: List[Dict], connections: Dict, result: Dict):
        """Check for proper data validation after external inputs"""
        # Check nodes that receive external data
        external_input_types = [
            'n8n-nodes-base.webhook',
            'n8n-nodes-base.httpRequest',
            'n8n-nodes-base.gmail',
            'n8n-nodes-base.slack'
        ]

        for node in nodes:
            if node.get('type') in external_input_types:
                node_name = node.get('name')

                # Check if next node validates data
                if node_name in connections:
                    targets = connections[node_name].get('main', [[]])[0] if connections[node_name].get('main') else []

                    if targets:
                        next_node_name = targets[0].get('node')
                        next_node = next((n for n in nodes if n.get('name') == next_node_name), None)

                        # Check if next node is validation-related
                        is_validation = next_node and next_node.get('type') in [
                            'n8n-nodes-base.if',
                            'n8n-nodes-base.switch',
                            'n8n-nodes-base.set',
                            'n8n-nodes-base.code'
                        ]

                        if not is_validation:
                            result['recommendations'].append({
                                'node': node_name,
                                'recommendation': (
                                    f'Node "{node_name}" receives external data but doesn\'t validate it '
                                    'before processing. Consider adding an IF or Code node to validate '
                                    'required fields, data types, and value ranges to prevent errors '
                                    'downstream.'
                                )
                            })

    @staticmethod
    def format_analysis_report(analysis: Dict, workflow_name: str) -> str:
        """Format semantic analysis as LLM-friendly report"""
        report = f"# 🔬 Semantic Workflow Analysis: {workflow_name}\n\n"

        # Summary
        total_issues = sum(analysis['severity'].values())
        report += f"**Total Issues Found:** {total_issues}\n"
        report += f"- Critical: {analysis['severity']['critical']}\n"
        report += f"- High: {analysis['severity']['high']}\n"
        report += f"- Medium: {analysis['severity']['medium']}\n"
        report += f"- Low: {analysis['severity']['low']}\n\n"

        # Critical and High severity issues first
        critical_high = [i for i in analysis['issues'] if i['severity'] in ['critical', 'high']]
        if critical_high:
            report += "## 🚨 Critical & High Priority Issues\n\n"
            for idx, issue in enumerate(critical_high, 1):
                report += f"### {idx}. {issue['issue']} [{issue['severity'].upper()}]\n"
                report += f"**Node:** `{issue['node']}`\n"
                report += f"**Category:** {issue['category']}\n\n"
                report += f"**Why this matters:**\n{issue['explanation']}\n\n"

                # Find corresponding LLM fix
                fix = next((f for f in analysis['llm_fixes']
                           if f['node'] == issue['node'] and f['issue'] == issue['issue']), None)
                if fix:
                    report += f"**How to fix (copy-paste ready):**\n{fix['fix']}\n\n"
                report += "---\n\n"

        # Medium and Low issues
        medium_low = [i for i in analysis['issues'] if i['severity'] in ['medium', 'low']]
        if medium_low:
            report += "## ⚠️ Medium & Low Priority Issues\n\n"
            for idx, issue in enumerate(medium_low, 1):
                report += f"### {idx}. {issue['issue']} [{issue['severity'].upper()}]\n"
                report += f"**Node:** `{issue['node']}`\n"
                report += f"**Explanation:** {issue['explanation']}\n\n"

        # Anti-patterns
        if analysis['anti_patterns']:
            report += "## 🎭 Anti-Patterns Detected\n\n"
            for pattern in analysis['anti_patterns']:
                report += f"### {pattern['pattern']} [{pattern['severity'].upper()}]\n"
                report += f"{pattern['description']}\n\n"
                report += f"**Recommendation:** {pattern['recommendation']}\n\n"

        # Recommendations
        if analysis['recommendations']:
            report += "## 💡 Optimization Recommendations\n\n"
            for rec in analysis['recommendations']:
                report += f"- **{rec['node']}**: {rec['recommendation']}\n\n"

        # Summary for LLMs
        if analysis['llm_fixes']:
            report += "## 🤖 Quick Fix Summary (for AI agents)\n\n"
            report += "The following nodes need modifications:\n\n"
            for fix in analysis['llm_fixes']:
                report += f"- `{fix['node']}`: {fix['issue']}\n"
            report += "\nDetailed fix instructions are provided above for each issue.\n"

        if total_issues == 0:
            report += "## ✅ Excellent!\n\n"
            report += "No semantic issues found. Workflow follows best practices.\n"

        return report

