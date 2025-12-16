#!/usr/bin/env python3
"""
Workflow Validator Module
Validates workflow structure and schema
"""
from typing import Dict, List


class WorkflowValidator:
    """Validates workflows before deployment"""

    # Required fields for workflow schema
    REQUIRED_WORKFLOW_FIELDS = ['name', 'nodes', 'connections']
    REQUIRED_NODE_FIELDS = ['name', 'type', 'position', 'parameters']

    # Node type patterns for validation
    TRIGGER_NODE_TYPES = ['n8n-nodes-base.webhook', 'n8n-nodes-base.scheduleTrigger', 'n8n-nodes-base.manualTrigger']

    @staticmethod
    def validate_workflow_schema(workflow: Dict) -> Dict[str, List[str]]:
        """Validate workflow schema structure

        Returns:
            Dict with 'errors' and 'warnings' lists
        """
        errors = []
        warnings = []

        # Check required workflow fields
        for field in WorkflowValidator.REQUIRED_WORKFLOW_FIELDS:
            if field not in workflow:
                errors.append(f"Missing required field: '{field}'")

        # Check if workflow has a name
        if 'name' in workflow:
            if not workflow['name'] or not workflow['name'].strip():
                errors.append("Workflow name cannot be empty")
            elif len(workflow['name']) > 200:
                warnings.append("Workflow name is very long (>200 chars)")

        # Validate nodes
        nodes = workflow.get('nodes', [])
        if not isinstance(nodes, list):
            errors.append("'nodes' must be a list")
        else:
            if len(nodes) == 0:
                errors.append("Workflow has no nodes")

            for idx, node in enumerate(nodes):
                if not isinstance(node, dict):
                    errors.append(f"Node at index {idx} is not a dictionary")
                    continue

                # Check required node fields
                for field in WorkflowValidator.REQUIRED_NODE_FIELDS:
                    if field not in node:
                        errors.append(f"Node '{node.get('name', f'at index {idx}')}': Missing required field '{field}'")

                # Validate node name
                if 'name' in node:
                    if not node['name'] or not node['name'].strip():
                        errors.append(f"Node at index {idx}: Name cannot be empty")

                # Validate node type
                if 'type' in node:
                    if not node['type'] or not node['type'].strip():
                        errors.append(f"Node '{node.get('name')}': Type cannot be empty")

                # Validate position
                if 'position' in node:
                    if not isinstance(node['position'], list) or len(node['position']) != 2:
                        errors.append(f"Node '{node.get('name')}': Position must be [x, y] array")

        # Validate connections
        connections = workflow.get('connections', {})
        if not isinstance(connections, dict):
            errors.append("'connections' must be a dictionary")

        return {'errors': errors, 'warnings': warnings}

    @staticmethod
    def validate_workflow_semantics(workflow: Dict) -> Dict[str, List[str]]:
        """Validate semantic rules (logic, best practices)

        Returns:
            Dict with 'errors' and 'warnings' lists
        """
        errors = []
        warnings = []
        nodes = workflow.get('nodes', [])
        connections = workflow.get('connections', {})

        # Check for at least one trigger node
        trigger_nodes = [n for n in nodes if n.get('type') in WorkflowValidator.TRIGGER_NODE_TYPES]
        if not trigger_nodes:
            errors.append("Workflow must have at least one trigger node (Webhook, Schedule, or Manual)")

        # Check for duplicate node names
        node_names = [n.get('name') for n in nodes if n.get('name')]
        duplicate_names = [name for name in node_names if node_names.count(name) > 1]
        if duplicate_names:
            errors.append(f"Duplicate node names found: {', '.join(set(duplicate_names))}")

        # Check for orphaned nodes (nodes without connections)
        if len(nodes) > 1:
            connected_nodes = set()
            for source_name, targets in connections.items():
                connected_nodes.add(source_name)
                if isinstance(targets, dict):
                    for target_list in targets.values():
                        if isinstance(target_list, list):
                            for target in target_list:
                                if isinstance(target, dict):
                                    connected_nodes.add(target.get('node'))

            orphaned = [n['name'] for n in nodes if n.get('name') and n['name'] not in connected_nodes and n.get('type') not in WorkflowValidator.TRIGGER_NODE_TYPES]
            if orphaned:
                warnings.append(f"Orphaned nodes (no connections): {', '.join(orphaned)}")

        # Check for default node names (bad practice)
        default_names = ['Webhook', 'HTTP Request', 'Set', 'IF', 'Function', 'Code']
        unnamed_nodes = [n['name'] for n in nodes if n.get('name') in default_names]
        if unnamed_nodes:
            warnings.append(f"Nodes with default names (should be renamed): {', '.join(set(unnamed_nodes))}")

        # Check for missing credentials in nodes that require them
        credential_nodes = ['n8n-nodes-base.httpRequest', 'n8n-nodes-base.postgres', 'n8n-nodes-base.redis']
        for node in nodes:
            if node.get('type') in credential_nodes:
                if not node.get('credentials') or len(node.get('credentials', {})) == 0:
                    warnings.append(f"Node '{node.get('name')}' may need credentials configured")

        # Check for hardcoded sensitive data
        for node in nodes:
            node_str = json.dumps(node.get('parameters', {}))
            if any(keyword in node_str.lower() for keyword in ['password', 'apikey', 'api_key', 'secret', 'token']) and '{{' not in node_str:
                warnings.append(f"Node '{node.get('name')}' may contain hardcoded sensitive data")

        # Check workflow complexity
        if len(nodes) > 30:
            warnings.append(f"Workflow is complex ({len(nodes)} nodes). Consider splitting into sub-workflows.")

        # Check for missing error handling
        error_trigger = any(n.get('type') == 'n8n-nodes-base.errorTrigger' for n in nodes)
        if len(nodes) > 5 and not error_trigger:
            warnings.append("Workflow lacks error handling (Error Trigger node)")

        return {'errors': errors, 'warnings': warnings}

    @staticmethod
    def validate_node_parameters(workflow: Dict) -> Dict[str, List[str]]:
        """Validate node-specific parameter requirements

        Returns:
            Dict with 'errors' and 'warnings' lists
        """
        errors = []
        warnings = []
        nodes = workflow.get('nodes', [])

        for node in nodes:
            node_type = node.get('type', '')
            node_name = node.get('name', 'Unknown')
            params = node.get('parameters', {})

            # Webhook node validation
            if node_type == 'n8n-nodes-base.webhook':
                if not params.get('path'):
                    errors.append(f"Webhook node '{node_name}': Missing 'path' parameter")

                auth_method = params.get('authentication')
                if not auth_method or auth_method == 'none':
                    warnings.append(f"Webhook node '{node_name}': No authentication enabled (security risk)")

            # HTTP Request node validation
            elif node_type == 'n8n-nodes-base.httpRequest':
                if not params.get('url'):
                    errors.append(f"HTTP Request node '{node_name}': Missing 'url' parameter")

                if not params.get('timeout'):
                    warnings.append(f"HTTP Request node '{node_name}': No timeout set (may hang)")

            # Schedule Trigger validation
            elif node_type == 'n8n-nodes-base.scheduleTrigger':
                if not params.get('rule') and not params.get('cronExpression'):
                    errors.append(f"Schedule Trigger node '{node_name}': Missing schedule configuration")

            # IF node validation
            elif node_type == 'n8n-nodes-base.if':
                conditions = params.get('conditions', {})
                if not conditions or len(conditions.get('boolean', [])) == 0:
                    warnings.append(f"IF node '{node_name}': No conditions defined")

            # Postgres node validation
            elif node_type == 'n8n-nodes-base.postgres':
                operation = params.get('operation')
                if operation in ['executeQuery', 'insert', 'update', 'delete']:
                    query = params.get('query', '')
                    if 'SELECT *' in query.upper():
                        warnings.append(f"Postgres node '{node_name}': Using SELECT * (bad practice)")
                    if operation != 'executeQuery' and '{{' not in query:
                        warnings.append(f"Postgres node '{node_name}': Query should use parameterized values")

            # Set node validation
            elif node_type == 'n8n-nodes-base.set':
                if not params.get('values'):
                    warnings.append(f"Set node '{node_name}': No values configured")

            # Code node validation
            elif node_type == 'n8n-nodes-base.code':
                code = params.get('jsCode', '')
                if not code or len(code.strip()) == 0:
                    errors.append(f"Code node '{node_name}': No code defined")

                # Check for common mistakes
                if 'return items' not in code and 'return [{' not in code:
                    warnings.append(f"Code node '{node_name}': Should return items array")

        return {'errors': errors, 'warnings': warnings}

    @classmethod
    def validate_workflow_full(cls, workflow: Dict) -> Dict:
        """Run all validations and combine results

        Returns:
            Dict with 'valid', 'errors', 'warnings', and 'summary'
        """
        schema_result = cls.validate_workflow_schema(workflow)
        semantic_result = cls.validate_workflow_semantics(workflow)
        param_result = cls.validate_node_parameters(workflow)

        all_errors = schema_result['errors'] + semantic_result['errors'] + param_result['errors']
        all_warnings = schema_result['warnings'] + semantic_result['warnings'] + param_result['warnings']

        is_valid = len(all_errors) == 0

        return {
            'valid': is_valid,
            'errors': all_errors,
            'warnings': all_warnings,
            'summary': {
                'total_errors': len(all_errors),
                'total_warnings': len(all_warnings),
                'schema_errors': len(schema_result['errors']),
                'semantic_errors': len(semantic_result['errors']),
                'parameter_errors': len(param_result['errors'])
            }
        }

