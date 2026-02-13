"""
Unit tests for SecurityTools handler.
"""
import pytest
from mcp.types import TextContent

from n8n_workflow_builder.tools.security_tools import SecurityTools


class TestSecurityTools:
    """Test suite for SecurityTools handler."""
    
    @pytest.fixture
    def security_tools(self, mock_security_auditor, mock_rbac_enforcer, mock_n8n_client):
        """Create SecurityTools instance with mocked dependencies."""
        return SecurityTools(
            security_auditor=mock_security_auditor,
            rbac_enforcer=mock_rbac_enforcer,
            client=mock_n8n_client
        )
    
    async def test_audit_workflow_security(self, security_tools, mock_security_auditor):
        """Test audit_workflow_security performs security audit."""
        arguments = {"workflow_id": "wf-1"}
        
        result = await security_tools.handle("audit_workflow_security", arguments)
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "wf-1" in result[0].text
        assert "risk" in result[0].text.lower()
        mock_security_auditor.audit_workflow.assert_called_once()
    
    async def test_get_security_summary(self, security_tools, mock_security_auditor):
        """Test get_security_summary returns summary."""
        arguments = {}
        
        result = await security_tools.handle("get_security_summary", arguments)
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "workflows" in result[0].text.lower()
        mock_security_auditor.get_summary.assert_called_once()
    
    async def test_rbac_check_permission(self, security_tools, mock_rbac_enforcer):
        """Test RBAC permission checking."""
        arguments = {
            "user_id": "user-1",
            "resource_type": "workflow",
            "action": "update"
        }
        
        result = await security_tools.handle("rbac_check_permission", arguments)
        
        assert len(result) == 1
        assert result[0].type == "text"
        mock_rbac_enforcer.check_permission.assert_called_once()
    
    async def test_rbac_create_approval_request(self, security_tools, mock_rbac_enforcer):
        """Test creating approval request."""
        arguments = {
            "user_id": "user-1",
            "action_type": "deploy",
            "resource_id": "wf-1"
        }
        
        result = await security_tools.handle("rbac_create_approval_request", arguments)
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "req-1" in result[0].text
        mock_rbac_enforcer.create_approval_request.assert_called_once()


"""
Unit tests for TemplateTools handler.
"""
import pytest
from mcp.types import TextContent

from n8n_workflow_builder.tools.template_tools import TemplateTools


class TestTemplateTools:
    """Test suite for TemplateTools handler."""
    
    @pytest.fixture
    def template_tools(self, mock_template_recommender):
        """Create TemplateTools instance with mocked dependencies."""
        return TemplateTools(template_recommender=mock_template_recommender)
    
    async def test_recommend_templates(self, template_tools, mock_template_recommender):
        """Test template recommendation."""
        arguments = {"description": "notify team on slack"}
        
        result = await template_tools.handle("recommend_templates", arguments)
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Slack" in result[0].text
        mock_template_recommender.recommend.assert_called_once()
    
    async def test_search_templates(self, template_tools, mock_template_recommender):
        """Test template search."""
        arguments = {"query": "data sync"}
        
        result = await template_tools.handle("search_templates", arguments)
        
        assert len(result) == 1
        assert result[0].type == "text"
        mock_template_recommender.search.assert_called_once()


"""
Unit tests for ExecutionTools handler.
"""
import pytest
from mcp.types import TextContent

from n8n_workflow_builder.tools.execution_tools import ExecutionTools


class TestExecutionTools:
    """Test suite for ExecutionTools handler."""
    
    @pytest.fixture
    def execution_tools(self, mock_n8n_client, mock_error_analyzer):
        """Create ExecutionTools instance with mocked dependencies."""
        return ExecutionTools(
            client=mock_n8n_client,
            error_analyzer=mock_error_analyzer
        )
    
    async def test_get_executions(self, execution_tools, mock_n8n_client):
        """Test get_executions retrieves execution history."""
        arguments = {"workflow_id": "wf-1", "limit": 10}
        
        result = await execution_tools.handle("get_executions", arguments)
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "exec-1" in result[0].text
        mock_n8n_client.get_executions.assert_called_once()
    
    async def test_analyze_execution_errors(self, execution_tools, mock_error_analyzer):
        """Test execution error analysis."""
        arguments = {"execution_id": "exec-1"}
        
        result = await execution_tools.handle("analyze_execution_errors", arguments)
        
        assert len(result) == 1
        assert result[0].type == "text"
        mock_error_analyzer.analyze_errors.assert_called_once()
