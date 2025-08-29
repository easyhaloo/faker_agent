"""
Base classes for LangChain-compatible tools.
"""
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type

from langchain_core.tools import BaseTool as LangChainBaseTool
from pydantic import BaseModel, Field

# Configure logger
logger = logging.getLogger(__name__)


class ToolParameter(BaseModel):
    """Parameter definition for a tool."""
    
    name: str
    type: str
    description: str
    required: bool = True
    default: Optional[Any] = None


class ToolMetadata(BaseModel):
    """Metadata for a tool."""
    
    name: str
    description: str
    parameters: List[ToolParameter] = Field(default_factory=list)
    return_schema: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    priority: int = 0


class BaseTool(ABC):
    """Base class for all tools compatible with LangChain."""
    
    name: str = "base_tool"
    description: str = "Base tool class"
    tags: List[str] = []
    priority: int = 0
    
    def __init__(self):
        self.metadata = ToolMetadata(
            name=self.name,
            description=self.description,
            parameters=self.get_parameters(),
            tags=self.tags,
            priority=self.priority
        )
    
    @abstractmethod
    async def run(self, **kwargs) -> Any:
        """Run the tool with the provided parameters."""
        pass
    
    def get_parameters(self) -> List[ToolParameter]:
        """Get the tool parameters."""
        return []
    
    def to_langchain_tool(self) -> LangChainBaseTool:
        """Convert to LangChain tool."""
        return LangChainToolAdapter(self)


class LangChainToolAdapter(LangChainBaseTool):
    """Adapter to convert our tools to LangChain tools."""
    
    def __init__(self, tool: BaseTool):
        super().__init__(
            name=tool.name,
            description=tool.description,
            args_schema=self._create_args_schema(tool.metadata.parameters)
        )
        self._tool = tool
    
    def _create_args_schema(self, parameters: List[ToolParameter]):
        """Create Pydantic schema from tool parameters."""
        # For simplicity, we'll create a basic schema
        # In a real implementation, this would dynamically create a Pydantic model
        class ArgsSchema(BaseModel):
            pass
        
        return ArgsSchema
    
    def _run(self, *args, **kwargs):
        """Synchronous run method required by LangChain."""
        raise NotImplementedError("Use async interface")
    
    async def _arun(self, *args, **kwargs):
        """Async run method."""
        return await self._tool.run(**kwargs)