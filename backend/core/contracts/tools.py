"""
Tool contracts for the Faker Agent.

This module provides contract classes for tool specifications
and parameters, enabling standardized tool registration and usage.
"""
import logging
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

# Configure logger
logger = logging.getLogger(__name__)


class ToolParameter(BaseModel):
    """
    Definition of a tool parameter.
    
    This class represents a parameter that can be passed to a tool,
    including its name, type, description, and other metadata.
    """
    
    name: str
    description: str
    type: str
    required: bool = True
    default: Optional[Any] = None
    enum: Optional[List[Any]] = None
    
    def dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "required": self.required
        }
        
        if self.default is not None:
            result["default"] = self.default
            
        if self.enum:
            result["enum"] = self.enum
            
        return result


class ToolSpec(BaseModel):
    """
    Tool specification contract.
    
    This class provides a standardized representation of a tool,
    including its name, description, parameters, and other metadata.
    """
    
    name: str
    description: str
    parameters: List[ToolParameter] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    priority: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": [param.dict() for param in self.parameters],
            "tags": self.tags,
            "priority": self.priority,
            "metadata": self.metadata
        }


class ToolInvocation(BaseModel):
    """
    Tool invocation request.
    
    This class represents a request to invoke a tool with specific parameters.
    """
    
    id: Optional[str] = None
    tool_name: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    def dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "tool_name": self.tool_name,
            "parameters": self.parameters
        }
        
        if self.id:
            result["id"] = self.id
            
        return result


class ToolResult(BaseModel):
    """
    Tool execution result.
    
    This class represents the result of a tool execution, including
    success/failure status and the actual result or error message.
    """
    
    tool_name: str
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    invocation_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "tool_name": self.tool_name,
            "success": self.success,
            "metadata": self.metadata
        }
        
        if self.result is not None:
            result["result"] = self.result
            
        if self.error:
            result["error"] = self.error
            
        if self.invocation_id:
            result["invocation_id"] = self.invocation_id
            
        return result