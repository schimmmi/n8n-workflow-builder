"""
Unit tests for WorkflowTools handler - SIMPLIFIED VERSION.

Tests core functionality of each tool in the WorkflowTools handler.
"""
import pytest
from mcp.types import TextContent
from n8n_workflow_builder.tools.workflow_tools import WorkflowTools


class TestWorkflowTools:
    """Test suite for WorkflowTools handler."""
    
    @pytest.fixture
    def workflow_tools(self, deps):
        """Create WorkflowTools instance with mocked dependencies."""
        return WorkflowTools(deps=deps)
    
    async def test_suggest_workflow_nodes(self, workflow_tools):
        """Test suggest_workflow_nodes returns workflow outline."""
        arguments = {"description": "Send notification to Slack"}
        
        result = await workflow_tools.handle("suggest_workflow_nodes", arguments)
        
        assert len(result) == 1
        assert result[0].type == "text"
        # Method returns workflow outline, not just nodes
        assert "Webhook" in result[0].text
    
    async def test_list_workflows(self, workflow_tools, mock_n8n_client):
        """Test list_workflows fetches from API."""
        arguments = {}
        
        result = await workflow_tools.handle("list_workflows", arguments)
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Workflow 1" in result[0].text
        mock_n8n_client.get_workflows.assert_called_once()
    
    async def test_create_workflow(self, workflow_tools, mock_n8n_client):
        """Test create_workflow."""
        arguments = {"name": "My New Workflow", "nodes": [], "connections": {}}
        
        result = await workflow_tools.handle("create_workflow", arguments)
        
        assert len(result) == 1
        assert result[0].type == "text"
        mock_n8n_client.create_workflow.assert_called_once()
    
    async def test_validate_workflow(self, workflow_tools, mock_workflow_validator):
        """Test workflow validation."""
        arguments = {"workflow_id": "wf-1"}
        
        result = await workflow_tools.handle("validate_workflow", arguments)
        
        assert len(result) == 1
        assert result[0].type == "text"
        # Validation calls validator
        mock_workflow_validator.validate.assert_called()
