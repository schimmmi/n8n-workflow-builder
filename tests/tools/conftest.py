"""
Pytest configuration and fixtures for tool handler tests.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock
from mcp.types import TextContent
from n8n_workflow_builder.dependencies import Dependencies


@pytest.fixture
def mock_n8n_client():
    """Mock N8nClient."""
    client = MagicMock()
    client.get_workflow = AsyncMock(return_value={"id": "wf-1", "name": "Test", "active": True, "nodes": [], "connections": {}})
    client.get_workflows = AsyncMock(return_value=[{"id": "wf-1", "name": "Workflow 1", "active": True, "nodes": [], "updatedAt": "2024-01-01"}])
    client.create_workflow = AsyncMock(return_value={"id": "new-wf-1", "name": "New", "active": False})
    client.update_workflow = AsyncMock(return_value={"id": "wf-1", "name": "Updated", "active": True, "nodes": [], "updatedAt": "2024-01-01"})
    client.delete_workflow = AsyncMock(return_value={"success": True})
    client.activate_workflow = AsyncMock(return_value={"active": True})
    client.deactivate_workflow = AsyncMock(return_value={"active": False})
    client.get_executions = AsyncMock(return_value=[{"id": "exec-1", "finished": True, "workflowData": {"name": "Test"}}])
    return client


@pytest.fixture
def mock_workflow_builder():
    """Mock WorkflowBuilder."""
    builder = MagicMock()
    builder.suggest_nodes = MagicMock(return_value=[{"name": "Webhook", "type": "webhook"}])
    builder.generate_workflow_outline = MagicMock(return_value="# Workflow\\n- Webhook")
    builder.analyze_workflow = MagicMock(return_value={"total_nodes": 2, "complexity": "low", "issues": [], "suggestions": []})
    return builder


@pytest.fixture
def mock_state_manager():
    """Mock StateManager."""
    manager = MagicMock()
    manager.get_state = MagicMock(return_value={"active_workflow_id": "wf-1"})
    manager.set_current_workflow = MagicMock()
    manager.set_last_execution = MagicMock()
    manager.log_action = MagicMock()
    return manager


@pytest.fixture
def mock_workflow_validator():
    """Mock WorkflowValidator."""
    validator = MagicMock()
    validator.validate = MagicMock(return_value={"valid": True, "errors": [], "warnings": []})
    return validator


@pytest.fixture
def deps(mock_n8n_client, mock_workflow_builder, mock_state_manager, mock_workflow_validator):
    """Dependencies container."""
    return Dependencies(
        client=mock_n8n_client,
        state_manager=mock_state_manager,
        workflow_builder=mock_workflow_builder,
        workflow_validator=mock_workflow_validator
    )


@pytest.fixture
def sample_workflow():
    """Sample workflow."""
    return {"id": "wf-1", "name": "Sample", "active": True, "nodes": [], "connections": {}}
