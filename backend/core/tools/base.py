"""
Base classes for LangChain-compatible tools.

This module defines the core tool abstractions for the Faker Agent system,
providing a standard interface for all tools that can be used by the
LangGraph orchestrator.
"""
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type

from langchain_core.tools import BaseTool as LangChainBaseTool
from pydantic import BaseModel, Field

from backend.core.contracts.tools import ToolSpec, ToolInvocation, ToolResult
from backend.core.errors import ToolError

# Configure logger
logger = logging.getLogger(__name__)


class ToolParameter(BaseModel):
    """Parameter definition for a tool.
    
    This class defines the metadata for a single parameter that a tool accepts,
    including its name, type, description, and whether it's required.
    """
    
    name: str = Field(..., description="Name of the parameter")
    type: str = Field(..., description="Data type of the parameter")
    description: str = Field(..., description="Description of what the parameter does")
    required: bool = Field(True, description="Whether the parameter is required")
    default: Optional[Any] = Field(None, description="Default value if not provided")


class BaseTool(ABC):
    """Base class for all tools compatible with LangChain.
    
    This abstract class defines the standard interface that all tools must implement
    to be used in the Faker Agent system. Tools represent discrete operations that
    the agent can perform to interact with external systems or compute results.
    """
    
    name: str = "base_tool"
    description: str = "Base tool class"
    tags: List[str] = []
    priority: int = 0
    
    def __init__(self):
        """Initialize the tool with its specification."""
        self.spec = ToolSpec(
            name=self.name,
            description=self.description,
            parameters=self._get_parameter_schema(),
            tags=self.tags,
            priority=self.priority
        )
    
    @abstractmethod
    async def run(self, **kwargs) -> Any:
        """Run the tool with the provided parameters.
        
        Args:
            **kwargs: Parameters specific to this tool
            
        Returns:
            The result of the tool execution
            
        Raises:
            ToolError: If the tool execution fails
        """
        pass
    
    def get_parameters(self) -> List[ToolParameter]:
        """Get the tool parameters."""
        return []
    
    def _get_parameter_schema(self) -> List[Any]:
        """Convert tool parameters to schema format."""
        from backend.core.contracts.tools import ToolParameter
        
        parameters = []
        for param in self.get_parameters():
            # If we already have a ToolParameter instance, use it directly
            if isinstance(param, ToolParameter):
                parameters.append(param)
            # Otherwise, convert dict to ToolParameter
            elif isinstance(param, dict):
                parameters.append(ToolParameter(**param))
            
        return parameters
    
    def to_langchain_tool(self) -> LangChainBaseTool:
        """Convert to LangChain tool."""
        return LangChainToolAdapter(self)
    
    async def invoke(self, invocation: ToolInvocation) -> ToolResult:
        """
        Invoke the tool with the given parameters.
        
        This method standardizes the invocation process for all tools, handling
        parameter passing and error handling in a consistent way.
        
        Args:
            invocation: The tool invocation request containing parameters
            
        Returns:
            The result of the tool execution wrapped in a ToolResult
        """
        try:
            # Execute the tool
            result = await self.run(**invocation.parameters)
            
            # Return success result
            return ToolResult(
                tool_name=self.name,
                success=True,
                result=result,
                invocation_id=invocation.id,
                metadata={"execution_time": "measurement_placeholder"}
            )
        except Exception as e:
            logger.error(f"Error executing tool {self.name}: {e}")
            # Return error result
            return ToolResult(
                tool_name=self.name,
                success=False,
                result=None,
                error=str(e),
                invocation_id=invocation.id,
                metadata={"error_type": type(e).__name__}
            )


class LangChainToolAdapter(LangChainBaseTool):
    """Adapter to convert our tools to LangChain tools.
    
    This adapter allows our custom tools to be used with LangChain's tool
    calling framework, bridging the gap between our tool system and LangChain's
    expectations.
    """
    
    def __init__(self, tool: BaseTool):
        super().__init__(
            name=tool.name,
            description=tool.description,
            args_schema=self._create_args_schema(tool.get_parameters())
        )
        self._tool = tool
    
    def _create_args_schema(self, parameters: List[Any]) -> Type[BaseModel]:
        """Create Pydantic schema from tool parameters."""
        # Define a simple schema class
        class ArgsSchema(BaseModel):
            model_config = {"extra": "allow"}
            pass
        
        # Instead of trying to dynamically create the class, just return a simple schema
        return ArgsSchema
    
    def _run(self, *args, **kwargs) -> Any:
        """Synchronous run method required by LangChain."""
        raise NotImplementedError("Use async interface")
    
    async def _arun(self, *args, **kwargs) -> Any:
        """Async run method."""
        return await self._tool.run(**kwargs)