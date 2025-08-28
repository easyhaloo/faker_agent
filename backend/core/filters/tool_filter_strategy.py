"""
Tool filtering strategies for the Faker Agent.

This module defines the base filter strategy class and several
implementations that can be used to filter the tool collection
before binding them to the LangGraph orchestrator.
"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Set, Type

from backend.core.registry.base_registry import BaseTool

# Configure logger
logger = logging.getLogger(__name__)


class ToolFilterStrategy(ABC):
    """Base class for tool filtering strategies."""
    
    @abstractmethod
    def filter(self, tools: List[BaseTool]) -> List[BaseTool]:
        """
        Filter the given tools based on the strategy.
        
        Args:
            tools: The list of tools to filter
            
        Returns:
            The filtered list of tools
        """
        pass


class ThresholdToolFilter(ToolFilterStrategy):
    """Filter strategy that limits the number of tools."""
    
    def __init__(self, max_tools: int = 5):
        """
        Initialize the threshold filter.
        
        Args:
            max_tools: Maximum number of tools to include
        """
        self.max_tools = max_tools
        logger.info(f"Initialized ThresholdToolFilter with max_tools={max_tools}")
    
    def filter(self, tools: List[BaseTool]) -> List[BaseTool]:
        """
        Limit the number of tools to the specified maximum.
        
        Args:
            tools: The list of tools to filter
            
        Returns:
            The filtered list of tools (limited to max_tools)
        """
        if len(tools) <= self.max_tools:
            return tools
        
        filtered_tools = tools[:self.max_tools]
        logger.info(f"Filtered tools from {len(tools)} to {len(filtered_tools)} using threshold strategy")
        return filtered_tools


class TagToolFilter(ToolFilterStrategy):
    """Filter strategy based on tool tags."""
    
    def __init__(self, included_tags: Set[str] = None, excluded_tags: Set[str] = None):
        """
        Initialize the tag filter.
        
        Args:
            included_tags: Set of tags to include (whitelist)
            excluded_tags: Set of tags to exclude (blacklist)
        """
        self.included_tags = included_tags or set()
        self.excluded_tags = excluded_tags or set()
        logger.info(f"Initialized TagToolFilter with included_tags={included_tags}, excluded_tags={excluded_tags}")
    
    def filter(self, tools: List[BaseTool]) -> List[BaseTool]:
        """
        Filter tools based on their tags.
        
        Args:
            tools: The list of tools to filter
            
        Returns:
            The filtered list of tools matching the tag criteria
        """
        filtered_tools = []
        
        for tool in tools:
            # Get tool tags (if the tool class has a tags attribute)
            tool_tags = getattr(tool, 'tags', set())
            
            # Check if we should include this tool
            if self.included_tags and not any(tag in self.included_tags for tag in tool_tags):
                continue
                
            # Check if we should exclude this tool
            if self.excluded_tags and any(tag in self.excluded_tags for tag in tool_tags):
                continue
                
            # Include this tool
            filtered_tools.append(tool)
        
        logger.info(f"Filtered tools from {len(tools)} to {len(filtered_tools)} using tag strategy")
        return filtered_tools


class PriorityToolFilter(ToolFilterStrategy):
    """Filter strategy based on tool priority."""
    
    def __init__(self, max_tools: int = 5):
        """
        Initialize the priority filter.
        
        Args:
            max_tools: Maximum number of tools to include
        """
        self.max_tools = max_tools
        logger.info(f"Initialized PriorityToolFilter with max_tools={max_tools}")
    
    def filter(self, tools: List[BaseTool]) -> List[BaseTool]:
        """
        Filter tools based on their priority.
        
        Args:
            tools: The list of tools to filter
            
        Returns:
            The filtered list of tools with highest priority
        """
        # Sort tools by priority (if the tool class has a priority attribute)
        sorted_tools = sorted(
            tools,
            key=lambda tool: getattr(tool, 'priority', 0),
            reverse=True  # Higher priority first
        )
        
        # Take the top N tools
        filtered_tools = sorted_tools[:self.max_tools]
        
        logger.info(f"Filtered tools from {len(tools)} to {len(filtered_tools)} using priority strategy")
        return filtered_tools


class CompositeToolFilter(ToolFilterStrategy):
    """Composite filter that applies multiple strategies in sequence."""
    
    def __init__(self, strategies: List[ToolFilterStrategy]):
        """
        Initialize the composite filter.
        
        Args:
            strategies: List of filter strategies to apply in sequence
        """
        self.strategies = strategies
        logger.info(f"Initialized CompositeToolFilter with {len(strategies)} strategies")
    
    def filter(self, tools: List[BaseTool]) -> List[BaseTool]:
        """
        Apply multiple filter strategies in sequence.
        
        Args:
            tools: The list of tools to filter
            
        Returns:
            The filtered list of tools after applying all strategies
        """
        filtered_tools = tools
        
        for strategy in self.strategies:
            filtered_tools = strategy.filter(filtered_tools)
        
        logger.info(f"Filtered tools from {len(tools)} to {len(filtered_tools)} using composite strategy")
        return filtered_tools


# Factory function to create a filter strategy
def create_filter_strategy(strategy_type: str, **kwargs) -> ToolFilterStrategy:
    """
    Create a filter strategy instance based on the specified type.
    
    Args:
        strategy_type: The type of strategy to create
        **kwargs: Additional parameters for the strategy
        
    Returns:
        A ToolFilterStrategy instance
    """
    strategy_map: Dict[str, Type[ToolFilterStrategy]] = {
        'threshold': ThresholdToolFilter,
        'tag': TagToolFilter,
        'priority': PriorityToolFilter,
        'composite': CompositeToolFilter
    }
    
    if strategy_type not in strategy_map:
        raise ValueError(f"Unknown filter strategy type: {strategy_type}")
    
    strategy_class = strategy_map[strategy_type]
    return strategy_class(**kwargs)