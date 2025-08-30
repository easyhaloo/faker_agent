"""
Tool registry for managing LangChain-compatible tools.

This module provides a central registry for all tools in the Faker Agent system,
allowing for easy discovery, retrieval, and management of tools.
"""
import logging
from typing import Any, Dict, List, Optional, Type, Union

from backend.core.contracts.tools import ToolSpec
from backend.core.tools.base import BaseTool

# Configure logger
logger = logging.getLogger(__name__)


class ToolRegistry:
    """Registry for managing LangChain-compatible tools.
    
    This class serves as a central registry for all tools in the Faker Agent system,
    providing methods to register, retrieve, and list available tools. It also
    supports conversion to LangChain format for compatibility.
    """
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self.langchain_tools: Dict[str, Any] = {}  # LangChain tool adapters
        logger.info("Initialized ToolRegistry")
    
    def register_tool(self, tool: BaseTool) -> None:
        """
        Register a tool instance.
        
        Args:
            tool: The tool instance to register
        """
        self.tools[tool.name] = tool
        # Also register the LangChain adapter
        self.langchain_tools[tool.name] = tool.to_langchain_tool()
        logger.info(f"Registered tool: {tool.name}")
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """
        Get a tool by name.
        
        Args:
            name: The name of the tool
            
        Returns:
            The tool instance or None if not found
        """
        return self.tools.get(name)
    
    def get_langchain_tool(self, name: str) -> Optional[Any]:
        """
        Get a LangChain tool adapter by name.
        
        Args:
            name: The name of the tool
            
        Returns:
            The LangChain tool adapter or None if not found
        """
        return self.langchain_tools.get(name)
    
    def list_tools(self) -> List[ToolSpec]:
        """
        List all registered tools.
        
        Returns:
            List of tool specifications
        """
        return [tool.spec for tool in self.tools.values()]
    
    def get_all_langchain_tools(self) -> List[Any]:
        """
        Get all LangChain tool adapters.
        
        Returns:
            List of LangChain tool adapters
        """
        return list(self.langchain_tools.values())
    
    def filter_tools(self, strategy=None, tags=None) -> List[BaseTool]:
        """
        Filter tools using the specified strategy and optional tags.
        
        Args:
            strategy: The filter strategy to apply
            tags: Optional list of tags to pre-filter by
            
        Returns:
            The filtered list of tool instances
        """
        tools = list(self.tools.values())
        
        # Pre-filter by tags if specified
        if tags:
            filtered_tools = []
            tag_set = set(tags)
            for tool in tools:
                # Check if any tool tag matches requested tags
                if any(tag in tag_set for tag in tool.tags):
                    filtered_tools.append(tool)
            tools = filtered_tools
        
        # Apply filter strategy if provided
        if strategy:
            tools = strategy.filter(tools)
        
        return tools


# Global registry instance
tool_registry = ToolRegistry()