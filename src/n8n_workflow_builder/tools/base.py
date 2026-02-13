#!/usr/bin/env python3
"""
Base classes and error handling for MCP tools
"""
from typing import Any, TYPE_CHECKING, Optional
from dataclasses import dataclass, field
import json

if TYPE_CHECKING:
    from ..dependencies import Dependencies

# Custom Exceptions
class WorkflowNotFoundError(Exception):
    """Raised when a workflow cannot be found"""
    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id
        super().__init__(f"Workflow '{workflow_id}' not found")


class ValidationError(Exception):
    """Raised when validation fails"""
    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class APIError(Exception):
    """Raised when n8n API returns an error"""
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[str] = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(message)


class AuthenticationError(Exception):
    """Raised when authentication fails"""
    pass


class PermissionDeniedError(Exception):
    """Raised when user lacks permission for an operation"""
    def __init__(self, operation: str, reason: Optional[str] = None):
        self.operation = operation
        self.reason = reason
        msg = f"Permission denied for operation: {operation}"
        if reason:
            msg += f" - {reason}"
        super().__init__(msg)


class ToolError(Exception):
    """Raised when a tool encounters an error during execution"""
    def __init__(self, error_type: str, message: str, details: Optional[dict] = None):
        self.error_type = error_type
        self.message = message
        self.details = details or {}
        super().__init__(f"[{error_type}] {message}")





@dataclass
class ToolErrorResponse:
    """Unified error response format for tools (use for serialization)"""
    code: str
    message: str
    details: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "error": self.code,
            "message": self.message,
            "details": self.details
        }
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class ToolResult:
    """Success response wrapper for tools"""
    data: Any
    metadata: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        result = {"data": self.data}
        if self.metadata:
            result["metadata"] = self.metadata
        return result


class BaseTool:
    """Abstract base class for all tool handlers"""
    
    def __init__(self, deps: 'Dependencies'):
        """Initialize tool with dependency container
        
        Args:
            deps: Dependency container with all required services
        """
        self.deps = deps
    
    async def handle(self, name: str, arguments: dict) -> Any:
        """Handle a tool call by routing to appropriate method
        
        Args:
            name: Tool name (e.g., "list_workflows")
            arguments: Tool arguments as dictionary
            
        Returns:
            Tool result (format depends on tool)
            
        Raises:
            ToolError: On tool execution error
            NotImplementedError: If tool handler not implemented
        """
        raise NotImplementedError(f"Tool handler must implement handle() method")
    
    def _error(self, code: str, message: str, **details) -> ToolErrorResponse:
        """Helper to create ToolErrorResponse
        
        Args:
            code: Error code (e.g., "WORKFLOW_NOT_FOUND")
            message: Human-readable error message
            **details: Additional error details
            
        Returns:
            ToolErrorResponse instance
        """
        return ToolErrorResponse(code=code, message=message, details=details)
    
    def _success(self, data: Any, **metadata) -> ToolResult:
        """Helper to create ToolResult
        
        Args:
            data: Result data
            **metadata: Additional metadata
            
        Returns:
            ToolResult instance
        """
        return ToolResult(data=data, metadata=metadata)
