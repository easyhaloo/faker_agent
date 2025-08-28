"""
Tool registry for managing LangChain-compatible tools.
"""
import logging
from typing import Any, Dict, List, Optional, Type

from backend.core.tools.base import BaseTool, ToolMetadata

# Configure logger
logger = logging.getLogger(__name__)


class ToolRegistry:
    """Registry for managing LangChain-compatible tools."""
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self.langchain_tools: Dict[str, Any] = {}  # LangChain tool adapters
        logger.info("Initialized ToolRegistry")
    
    def register_tool(self, tool: BaseTool) -> None:
        """Register a tool instance."""
        self.tools[tool.name] = tool
        # Also register the LangChain adapter
        self.langchain_tools[tool.name] = tool.to_langchain_tool()
        logger.info(f"Registered tool: {tool.name}")
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self.tools.get(name)
    
    def get_langchain_tool(self, name: str) -> Optional[Any]:
        """Get a LangChain tool adapter by name."""
        return self.langchain_tools.get(name)
    
    def list_tools(self) -> List[ToolMetadata]:
        """List all registered tools."""
        return [tool.metadata for tool in self.tools.values()]
    
    def get_all_langchain_tools(self) -> List[Any]:
        """Get all LangChain tool adapters."""
        return list(self.langchain_tools.values())


# Global registry instance
tool_registry = ToolRegistry()