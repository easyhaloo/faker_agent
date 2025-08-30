"""
Filtered tool registry with support for advanced filtering strategies.

This module extends the base tool registry with filtering capabilities,
allowing tools to be selected based on various criteria such as tags,
priority, and threshold limits before being used in the LangGraph flow.
"""
import logging
from typing import Any, Dict, List, Optional, Set, Type

from backend.core.contracts.tools import ToolSpec
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
        # Get tools (optionally pre-filtered by tags)
        tools = super().filter_tools(strategy=None, tags=tags)
        
        # Apply filter strategy if provided, otherwise use default
        filter_strategy = strategy or self._default_filter_strategy
        filtered_tools = filter_strategy.filter(tools)
        
        logger.info(f"Filtered tools from {len(tools)} to {len(filtered_tools)} using {filter_strategy.__class__.__name__}")
        return filtered_tools
    
    def set_default_filter_strategy(self, strategy: ToolFilterStrategy) -> None:
        """
        Set the default filter strategy.
        
        Args:
            strategy: The filter strategy to use as default
        """
        self._default_filter_strategy = strategy
        logger.info(f"Set default filter strategy to {strategy.__class__.__name__}")
    
    def get_filtered_specs(
        self,
        strategy: Optional[ToolFilterStrategy] = None,
        tags: Optional[List[str]] = None
    ) -> List[ToolSpec]:
        """
        Get tool specifications after filtering.
        
        Args:
            strategy: The filter strategy to apply
            tags: Optional list of tags to pre-filter by
            
        Returns:
            List of filtered tool specifications
        """
        # Get filtered tools
        filtered_tools = self.filter_tools(strategy=strategy, tags=tags)
        
        # Return their specs
        return [tool.spec for tool in filtered_tools]


# Global filtered registry instance
filtered_registry = FilteredToolRegistry()