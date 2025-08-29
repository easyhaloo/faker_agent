"""
Enhanced tool registry with filtering support.
"""
import logging
from typing import Any, Dict, List, Optional, Set, Type

from pydantic import BaseModel

from backend.core.filters.tool_filter_strategy import ToolFilterStrategy, ThresholdToolFilter
from backend.core.tools.base import BaseTool
from backend.core.tools.registry import ToolRegistry

# Configure logger
logger = logging.getLogger(__name__)


class FilteredToolRegistry(ToolRegistry):
    """
    Enhanced tool registry with support for filtering strategies.
    
    This registry extends the base registry with the ability to
    apply filtering strategies to tools before they're used in
    the LangGraph flow.
    """
    
    def __init__(self):
        """Initialize the filtered tool registry."""
        super().__init__()
        self._default_filter_strategy = ThresholdToolFilter(max_tools=5)
        logger.info("Initialized FilteredToolRegistry with default filter strategy")
    
    def filter_tools(
        self, 
        strategy: Optional[ToolFilterStrategy] = None, 
        tags: Optional[List[str]] = None
    ) -> List[BaseTool]:
        """
        Filter tools using the specified strategy and optional tags.
        
        Args:
            strategy: The filter strategy to apply
            tags: Optional list of tags to pre-filter by
            
        Returns:
            The filtered list of tool instances
        """
        # Get all tools or filter by tags first
        tools = []
        
        for name, tool in self.tools.items():
            # Skip tools that don't match tags if specified
            if tags and not any(tag in tool.metadata.tags for tag in tags):
                continue
                
            # Add tool instance to list
            tools.append(tool)
        
        # Apply filter strategy if provided, otherwise use default
        filter_strategy = strategy or self._default_filter_strategy
        filtered_tools = filter_strategy.filter(tools)
        
        logger.info(f"Filtered tools from {len(tools)} to {len(filtered_tools)}")
        return filtered_tools
    
    def set_default_filter_strategy(self, strategy: ToolFilterStrategy):
        """Set the default filter strategy."""
        self._default_filter_strategy = strategy
        logger.info(f"Set default filter strategy to {strategy.__class__.__name__}")
    
    def get_filtered_tools_by_tag(self, tags: List[str]) -> List[Dict[str, Any]]:
        """
        Get tools filtered by tag.
        
        Args:
            tags: List of tags to filter by
            
        Returns:
            List of tool definitions matching the tags
        """
        filtered_tools = []
        tag_set = set(tags)
        
        for name, tool in self.tools.items():
            # Check if any tool tag matches requested tags
            if any(tag in tag_set for tag in tool.metadata.tags):
                filtered_tools.append({
                    "name": name,
                    "description": tool.metadata.description,
                    "parameters": [p.dict() for p in tool.metadata.parameters],
                    "tags": tool.metadata.tags,
                    "priority": tool.metadata.priority
                })
        
        return filtered_tools


# Create global enhanced registry instance
enhanced_registry = FilteredToolRegistry()