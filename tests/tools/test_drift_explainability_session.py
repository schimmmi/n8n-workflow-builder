"""
Unit tests for DriftTools, ExplainabilityTools, and SessionTools handlers.
"""
import pytest
from mcp.types import TextContent

from n8n_workflow_builder.tools.drift_tools import DriftTools
from n8n_workflow_builder.tools.explainability_tools import ExplainabilityTools  
from n8n_workflow_builder.tools.session_tools import SessionTools


class TestDriftTools:
    """Test suite for DriftTools handler."""
    
    @pytest.fixture
    def drift_tools(self, mock_drift_detector, mock_n8n_client):
        """Create DriftTools instance with mocked dependencies."""
        return DriftTools(
            drift_detector=mock_drift_detector,
            client=mock_n8n_client
        )
    
    async def test_detect_workflow_drift(self, drift_tools, mock_drift_detector):
        """Test drift detection."""
        arguments = {
            "workflow_id": "wf-1",
            "baseline_version": "v1.0"
        }
        
        result = await drift_tools.handle("detect_workflow_drift", arguments)
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "drift" in result[0].text.lower()
        mock_drift_detector.detect_drift.assert_called_once()
    
    async def test_analyze_drift_pattern(self, drift_tools, mock_drift_detector):
        """Test drift pattern analysis."""
        arguments = {"drift_data": {"changes": []}}
        
        result = await drift_tools.handle("analyze_drift_pattern", arguments)
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "pattern" in result[0].text.lower()
        mock_drift_detector.analyze_pattern.assert_called_once()


class TestExplainabilityTools:
    """Test suite for ExplainabilityTools handler."""
    
    @pytest.fixture
    def explainability_tools(self, mock_workflow_builder, mock_n8n_client):
        """Create ExplainabilityTools instance."""
        return ExplainabilityTools(
            workflow_builder=mock_workflow_builder,
            client=mock_n8n_client
        )
    
    async def test_explain_node(self, explainability_tools):
        """Test node explanation."""
        arguments = {"node_type": "webhook"}
        
        result = await explainability_tools.handle("explain_node", arguments)
        
        assert len(result) == 1
        assert result[0].type == "text"
    
    async def test_explain_workflow(self, explainability_tools, mock_n8n_client):
        """Test workflow explanation."""
        arguments = {"workflow_id": "wf-1"}
        
        result = await explainability_tools.handle("explain_workflow", arguments)
        
        assert len(result) == 1
        assert result[0].type == "text"
        mock_n8n_client.get_workflow.assert_called_once()


class TestSessionTools:
    """Test suite for SessionTools handler."""
    
    @pytest.fixture
    def session_tools(self, mock_state_manager):
        """Create SessionTools instance."""
        return SessionTools(state_manager=mock_state_manager)
    
    async def test_get_session_state(self, session_tools, mock_state_manager):
        """Test session state retrieval."""
        arguments = {}
        
        result = await session_tools.handle("get_session_state", arguments)
        
        assert len(result) == 1
        assert result[0].type == "text"
        mock_state_manager.get_state.assert_called_once()
    
    async def test_set_active_workflow(self, session_tools, mock_state_manager):
        """Test setting active workflow."""
        arguments = {"workflow_id": "wf-1"}
        
        result = await session_tools.handle("set_active_workflow", arguments)
        
        assert len(result) == 1
        assert result[0].type == "text"
        mock_state_manager.set_active_workflow.assert_called_once()
    
    async def test_clear_session_state(self, session_tools, mock_state_manager):
        """Test session state clearing."""
        arguments = {}
        
        result = await session_tools.handle("clear_session_state", arguments)
        
        assert len(result) == 1
        assert result[0].type == "text"
        mock_state_manager.clear_state.assert_called_once()
