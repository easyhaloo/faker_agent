"""
Tool filter manager for the Faker Agent.

This module provides a manager for tool filtering strategies.
"""
import logging
from typing import Dict, List, Optional, Set, Type

from backend.core.filters.tool_filter_strategy import (
    CompositeToolFilter,
    PriorityToolFilter,
    TagToolFilter,
    ThresholdToolFilter,
    ToolFilterStrategy,
    create_filter_strategy
)
from backend.core.registry.base_registry import BaseTool
from backend.core.registry.enhanced_registry import enhanced_registry

# Configure logger
logger = logging.getLogger(__name__)


class ToolFilterManager:
    """
    Manager for tool filtering strategies.
    
    This class provides a central point for creating and applying
    filter strategies to tools before they're used in the LangGraph
    orchestrator.
    """
    
    def __init__(self):
        """Initialize the filter manager."""
        self.registry = enhanced_registry
        self.strategies: Dict[str, ToolFilterStrategy] = {}
        
        # Register default strategies
        self.register_strategy("threshold_5", ThresholdToolFilter(max_tools=5))
        self.register_strategy("threshold_10", ThresholdToolFilter(max_tools=10))
        self.register_strategy("priority", PriorityToolFilter(max_tools=5))
        
        logger.info("Initialized ToolFilterManager with default strategies")
    
    def register_strategy(self, name: str, strategy: ToolFilterStrategy) -> None:
        """
        Register a filter strategy.
        
        Args:
            name: The name of the strategy
            strategy: The filter strategy instance
        """
        self.strategies[name] = strategy
        logger.info(f"Registered filter strategy: {name}")
    
    def get_strategy(self, name: str) -> Optional[ToolFilterStrategy]:
        """
        Get a filter strategy by name.
        
        Args:
            name: The name of the strategy
            
        Returns:
            The filter strategy or None if not found
        """
        return self.strategies.get(name)
    
    def create_composite_strategy(
        self,
        strategy_names: List[str],
        name: Optional[str] = None
    ) -> ToolFilterStrategy:
        """
        Create a composite strategy from multiple strategies.
        
        Args:
            strategy_names: List of strategy names to combine
            name: Optional name to register the composite strategy
            
        Returns:
            The composite filter strategy
        """
        strategies = []
        
        for strategy_name in strategy_names:
            strategy = self.get_strategy(strategy_name)
            if strategy:
                strategies.append(strategy)
            else:
                logger.warning(f"Strategy not found: {strategy_name}")
        
        if not strategies:
            logger.warning("No valid strategies found, using default threshold")
            strategies = [ThresholdToolFilter(max_tools=5)]
        
        composite = CompositeToolFilter(strategies)
        
        if name:
            self.register_strategy(name, composite)
            
        return composite
    
    def create_tag_strategy(
        self,
        included_tags: Optional[Set[str]] = None,
        excluded_tags: Optional[Set[str]] = None,
        name: Optional[str] = None
    ) -> ToolFilterStrategy:
        """
        Create a tag-based filter strategy.
        
        Args:
            included_tags: Set of tags to include
            excluded_tags: Set of tags to exclude
            name: Optional name to register the strategy
            
        Returns:
            The tag filter strategy
        """
        strategy = TagToolFilter(
            included_tags=included_tags or set(),
            excluded_tags=excluded_tags or set()
        )
        
        if name:
            self.register_strategy(name, strategy)
            
        return strategy
    
    def filter_tools(
        self,
        strategy_name: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[BaseTool]:
        """
        Filter tools using the specified strategy.
        
        Args:
            strategy_name: The name of the strategy to use
            tags: Optional list of tags to pre-filter by
            
        Returns:
            The filtered list of tool instances
        """
        strategy = None
        if strategy_name:
            strategy = self.get_strategy(strategy_name)
            if not strategy:
                logger.warning(f"Strategy not found: {strategy_name}, using default")
        
        return self.registry.filter_tools(strategy=strategy, tags=tags)


# Create global filter manager instance
filter_manager = ToolFilterManager()