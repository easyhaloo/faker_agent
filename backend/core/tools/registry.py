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
    
    def filter_tools(self, strategy=None, tags=None) -> List[BaseTool]:
        """
        Filter tools using the specified strategy and optional tags.
        
        Args:
            strategy: The filter strategy to apply (not implemented in this basic version)
            tags: Optional list of tags to pre-filter by
            
        Returns:
            The filtered list of tool instances
        """
        tools = list(self.tools.values())
        
        # Filter by tags if specified
        if tags:
            filtered_tools = []
            tag_set = set(tags)
            for tool in tools:
                # Check if any tool tag matches requested tags
                if hasattr(tool.metadata, 'tags') and any(tag in tag_set for tag in tool.metadata.tags):
                    filtered_tools.append(tool)
            tools = filtered_tools
        
        return tools


# Global registry instance
tool_registry = ToolRegistry()