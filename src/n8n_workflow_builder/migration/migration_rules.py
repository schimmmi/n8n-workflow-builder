"""
Predefined Migration Rules

Collection of migration rules for common n8n node updates.
"""
from typing import Dict
from .migration_engine import MigrationRule


# HTTP Request Node: v2 -> v3
def migrate_http_v2_to_v3(node: Dict) -> Dict:
    """
    Migrate HTTP Request node from v2 to v3
    - Move authentication to credentials
    - Rename 'url' to 'requestUrl'
    - Rename 'method' to 'requestMethod'
    """
    parameters = node.get("parameters", {})

    # Rename parameters
    if "url" in parameters:
        parameters["requestUrl"] = parameters.pop("url")

    if "method" in parameters:
        parameters["requestMethod"] = parameters.pop("method")

    # Move authentication if present
    if "authentication" in parameters:
        auth_type = parameters["authentication"]
        if auth_type != "none":
            # Create credential reference (would need actual credential mapping)
            if "credentials" not in node:
                node["credentials"] = {}

            # Note: This is a simplified migration
            # Real implementation would need to handle actual credential migration
            logger.info(f"Authentication type '{auth_type}' needs credential setup")

    node["parameters"] = parameters
    return node


# HTTP Request Node: v3 -> v4
def migrate_http_v3_to_v4(node: Dict) -> Dict:
    """
    Migrate HTTP Request node from v3 to v4
    - Add new authentication options support
    - Update response handling
    """
    parameters = node.get("parameters", {})

    # Add new response handling options if not present
    if "options" not in parameters:
        parameters["options"] = {}

    # Migrate old response format settings
    if "responseFormat" in parameters:
        response_format = parameters.pop("responseFormat")
        parameters["options"]["response"] = {
            "response": {
                "responseFormat": response_format
            }
        }

    node["parameters"] = parameters
    return node


# Postgres Node: v1 -> v2
def migrate_postgres_v1_to_v2(node: Dict) -> Dict:
    """
    Migrate Postgres node from v1 to v2
    - Rename 'executeQuery' operation to 'query'
    - Update parameter structure
    """
    parameters = node.get("parameters", {})

    # Rename operation
    if parameters.get("operation") == "executeQuery":
        parameters["operation"] = "query"

    # Move query parameter if needed
    if "queryString" in parameters:
        parameters["query"] = parameters.pop("queryString")

    node["parameters"] = parameters
    return node


# Slack Node: v1 -> v2
def migrate_slack_v1_to_v2(node: Dict) -> Dict:
    """
    Migrate Slack node from v1 to v2
    - Update message formatting
    - New attachment structure
    """
    parameters = node.get("parameters", {})

    # Update message formatting
    if "message" in parameters:
        message = parameters["message"]
        # v2 uses markdown by default
        if "mrkdwn" not in parameters:
            parameters["mrkdwn"] = True

    # Migrate attachments if present
    if "attachments" in parameters:
        old_attachments = parameters["attachments"]
        # Convert to new format (simplified)
        if isinstance(old_attachments, str):
            import json
            try:
                parameters["attachments"] = json.loads(old_attachments)
            except:
                pass

    node["parameters"] = parameters
    return node


# Webhook Node: v1 -> v2
def migrate_webhook_v1_to_v2(node: Dict) -> Dict:
    """
    Migrate Webhook node from v1 to v2
    - New response options
    - Improved authentication
    """
    parameters = node.get("parameters", {})

    # Add new response options
    if "options" not in parameters:
        parameters["options"] = {}

    # Migrate response mode
    if "respondWith" in parameters:
        respond_with = parameters["respondWith"]
        if respond_with == "text":
            parameters["options"]["responseContentType"] = "text/plain"
        elif respond_with == "json":
            parameters["options"]["responseContentType"] = "application/json"

    node["parameters"] = parameters
    return node


# Set Node: v1 -> v2
def migrate_set_v1_to_v2(node: Dict) -> Dict:
    """
    Migrate Set node from v1 to v2
    - New value setting structure
    """
    parameters = node.get("parameters", {})

    # Migrate keepOnlySet parameter
    if "keepOnlySet" in parameters:
        keep_only = parameters.pop("keepOnlySet")
        if "options" not in parameters:
            parameters["options"] = {}
        parameters["options"]["keepOnlySet"] = keep_only

    node["parameters"] = parameters
    return node


# Function Node: v1 -> v2
def migrate_function_v1_to_v2(node: Dict) -> Dict:
    """
    Migrate Function node from v1 to v2
    - Updated item access API
    - New error handling
    """
    parameters = node.get("parameters", {})

    # Add migration note in function code if present
    if "functionCode" in parameters:
        code = parameters["functionCode"]

        # Add comment about API changes
        migration_note = (
            "// NOTE: Migrated from v1 to v2\n"
            "// - $item() is now items[0]\n"
            "// - $items() is now items\n"
            "// - Consider updating code if using old API\n\n"
        )

        # Only add if not already present
        if "Migrated from v1" not in code:
            parameters["functionCode"] = migration_note + code

    node["parameters"] = parameters
    return node


# HTTP Request Node: v1 -> v2
def migrate_http_v1_to_v2(node: Dict) -> Dict:
    """
    Migrate HTTP Request node from v1 to v2
    - Same parameter structure, but version bump
    - Prepare for v2 deprecations
    """
    # v1 to v2 is mostly a version bump
    # The actual parameter changes happen in v2 to v3
    return node


# Create migration rules
MIGRATION_RULES = [
    # HTTP Request migrations
    MigrationRule(
        rule_id="http_v1_to_v2",
        name="HTTP Request v1 → v2",
        description="Migrate HTTP Request node from version 1 to 2",
        node_type="n8n-nodes-base.httpRequest",
        from_version=1,
        to_version=2,
        transform=migrate_http_v1_to_v2,
        severity="medium"
    ),
    MigrationRule(
        rule_id="http_v2_to_v3",
        name="HTTP Request v2 → v3",
        description="Migrate HTTP Request node from version 2 to 3 (parameter renames, auth changes)",
        node_type="n8n-nodes-base.httpRequest",
        from_version=2,
        to_version=3,
        transform=migrate_http_v2_to_v3,
        severity="high"
    ),
    MigrationRule(
        rule_id="http_v3_to_v4",
        name="HTTP Request v3 → v4",
        description="Migrate HTTP Request node from version 3 to 4 (new auth options)",
        node_type="n8n-nodes-base.httpRequest",
        from_version=3,
        to_version=4,
        transform=migrate_http_v3_to_v4,
        severity="medium"
    ),

    # Postgres migrations
    MigrationRule(
        rule_id="postgres_v1_to_v2",
        name="Postgres v1 → v2",
        description="Migrate Postgres node from version 1 to 2 (operation rename)",
        node_type="n8n-nodes-base.postgres",
        from_version=1,
        to_version=2,
        transform=migrate_postgres_v1_to_v2,
        severity="high"
    ),

    # Slack migrations
    MigrationRule(
        rule_id="slack_v1_to_v2",
        name="Slack v1 → v2",
        description="Migrate Slack node from version 1 to 2 (message formatting)",
        node_type="n8n-nodes-base.slack",
        from_version=1,
        to_version=2,
        transform=migrate_slack_v1_to_v2,
        severity="medium"
    ),

    # Webhook migrations
    MigrationRule(
        rule_id="webhook_v1_to_v2",
        name="Webhook v1 → v2",
        description="Migrate Webhook node from version 1 to 2 (response options)",
        node_type="n8n-nodes-base.webhook",
        from_version=1,
        to_version=2,
        transform=migrate_webhook_v1_to_v2,
        severity="low"
    ),

    # Set node migrations
    MigrationRule(
        rule_id="set_v1_to_v2",
        name="Set v1 → v2",
        description="Migrate Set node from version 1 to 2 (options structure)",
        node_type="n8n-nodes-base.set",
        from_version=1,
        to_version=2,
        transform=migrate_set_v1_to_v2,
        severity="low"
    ),

    # Function node migrations
    MigrationRule(
        rule_id="function_v1_to_v2",
        name="Function v1 → v2",
        description="Migrate Function node from version 1 to 2 (API changes)",
        node_type="n8n-nodes-base.function",
        from_version=1,
        to_version=2,
        transform=migrate_function_v1_to_v2,
        severity="critical"
    ),
]


# Helper function to get rule by ID
def get_rule_by_id(rule_id: str) -> MigrationRule:
    """Get migration rule by ID"""
    for rule in MIGRATION_RULES:
        if rule.rule_id == rule_id:
            return rule
    raise ValueError(f"Migration rule '{rule_id}' not found")


# Helper function to get rules for node type
def get_rules_for_node(node_type: str) -> list[MigrationRule]:
    """Get all migration rules for a specific node type"""
    return [rule for rule in MIGRATION_RULES if rule.node_type == node_type]


import logging
logger = logging.getLogger("n8n-workflow-builder")
