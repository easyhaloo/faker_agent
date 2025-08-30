"""
Filter manager for the Faker Agent.

This module provides a manager for filtering strategies, allowing
for dynamic creation, registration, and application of filter strategies
to tools and protocols before they're used in the system.
"""
import logging
from typing import Dict, List, Optional, Set, Type, TYPE_CHECKING, Any

from backend.core.filters.tool_filter_strategy import (
    CompositeToolFilter,
    PriorityToolFilter,
    TagToolFilter,
    ThresholdToolFilter,
    ToolFilterStrategy,
    create_filter_strategy
)
from backend.core.filters.protocol_filter_strategy import (
    AllowAllProtocolFilter,
    BlacklistProtocolFilter,
    CompositeProtocolFilter,
    DenyAllProtocolFilter,
    ProtocolFilterStrategy,
    WhitelistProtocolFilter,
    create_protocol_filter_strategy
)
from backend.core.protocol.base_protocol import BaseProtocol
from backend.core.tools.base import BaseTool

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from backend.core.tools.filtered_registry import FilteredToolRegistry

# Configure logger
logger = logging.getLogger(__name__)


class FilterManager:
    """
    Manager for tool and protocol filtering strategies.
    
    This class provides a central point for creating and applying
    filter strategies to tools and protocols before they're used
    in the system.
    """
    
    def __init__(self):
        """Initialize the filter manager."""
        self.registry = None  # Will be set later to avoid circular import
        self.tool_strategies: Dict[str, ToolFilterStrategy] = {}
        self.protocol_strategies: Dict[str, ProtocolFilterStrategy] = {}
        
        # Register default tool strategies
        self.register_tool_strategy("threshold_5", ThresholdToolFilter(max_tools=5))
        self.register_tool_strategy("threshold_10", ThresholdToolFilter(max_tools=10))
        self.register_tool_strategy("priority", PriorityToolFilter(max_tools=5))
        
        # Register default protocol strategies
        self.register_protocol_strategy("allow_all", AllowAllProtocolFilter())
        self.register_protocol_strategy("deny_all", DenyAllProtocolFilter())
        self.register_protocol_strategy("http_only", WhitelistProtocolFilter({"http"}))
        self.register_protocol_strategy("sse_only", WhitelistProtocolFilter({"sse"}))
        self.register_protocol_strategy("websocket_only", WhitelistProtocolFilter({"websocket"}))
        
        logger.info("Initialized FilterManager with default strategies")
    
    # Tool filtering methods
    
    def register_tool_strategy(self, name: str, strategy: ToolFilterStrategy) -> None:
        """
        Register a tool filter strategy.
        
        Args:
            name: The name of the strategy
            strategy: The filter strategy instance
        """
        self.tool_strategies[name] = strategy
        logger.info(f"Registered tool filter strategy: {name}")
    
    def get_tool_strategy(self, name: str) -> Optional[ToolFilterStrategy]:
        """
        Get a tool filter strategy by name.
        
        Args:
            name: The name of the strategy
            
        Returns:
            The filter strategy or None if not found
        """
        return self.tool_strategies.get(name)
    
    def create_composite_tool_strategy(
        self,
        strategy_names: List[str],
        name: Optional[str] = None
    ) -> ToolFilterStrategy:
        """
        Create a composite tool strategy from multiple strategies.
        
        Args:
            strategy_names: List of strategy names to combine
            name: Optional name to register the composite strategy
            
        Returns:
            The composite filter strategy
        """
        strategies = []
        
        for strategy_name in strategy_names:
            strategy = self.get_tool_strategy(strategy_name)
            if strategy:
                strategies.append(strategy)
            else:
                logger.warning(f"Tool strategy not found: {strategy_name}")
        
        if not strategies:
            logger.warning("No valid tool strategies found, using default threshold")
            strategies = [ThresholdToolFilter(max_tools=5)]
        
        composite = CompositeToolFilter(strategies)
        
        if name:
            self.register_tool_strategy(name, composite)
            
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
            self.register_tool_strategy(name, strategy)
            
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
            strategy = self.get_tool_strategy(strategy_name)
            if not strategy:
                logger.warning(f"Tool strategy not found: {strategy_name}, using default")
        
        # Import here to avoid circular imports
        if self.registry is None:
            from backend.core.tools.filtered_registry import filtered_registry
            self.registry = filtered_registry
            
        return self.registry.filter_tools(strategy=strategy, tags=tags)
    
    def list_tool_strategies(self) -> List[str]:
        """
        List all registered tool strategy names.
        
        Returns:
            List of tool strategy names
        """
        return list(self.tool_strategies.keys())
    
    # Protocol filtering methods
    
    def register_protocol_strategy(self, name: str, strategy: ProtocolFilterStrategy) -> None:
        """
        Register a protocol filter strategy.
        
        Args:
            name: The name of the strategy
            strategy: The filter strategy instance
        """
        self.protocol_strategies[name] = strategy
        logger.info(f"Registered protocol filter strategy: {name}")
    
    def get_protocol_strategy(self, name: str) -> Optional[ProtocolFilterStrategy]:
        """
        Get a protocol filter strategy by name.
        
        Args:
            name: The name of the strategy
            
        Returns:
            The filter strategy or None if not found
        """
        return self.protocol_strategies.get(name)
    
    def create_composite_protocol_strategy(
        self,
        strategy_names: List[str],
        name: Optional[str] = None
    ) -> ProtocolFilterStrategy:
        """
        Create a composite protocol strategy from multiple strategies.
        
        Args:
            strategy_names: List of strategy names to combine
            name: Optional name to register the composite strategy
            
        Returns:
            The composite filter strategy
        """
        strategies = []
        
        for strategy_name in strategy_names:
            strategy = self.get_protocol_strategy(strategy_name)
            if strategy:
                strategies.append(strategy)
            else:
                logger.warning(f"Protocol strategy not found: {strategy_name}")
        
        if not strategies:
            logger.warning("No valid protocol strategies found, using allow all")
            strategies = [AllowAllProtocolFilter()]
        
        composite = CompositeProtocolFilter(strategies)
        
        if name:
            self.register_protocol_strategy(name, composite)
            
        return composite
    
    def create_whitelist_protocol_strategy(
        self,
        allowed_protocols: Set[str],
        name: Optional[str] = None
    ) -> ProtocolFilterStrategy:
        """
        Create a whitelist protocol filter strategy.
        
        Args:
            allowed_protocols: Set of protocol types to allow
            name: Optional name to register the strategy
            
        Returns:
            The whitelist filter strategy
        """
        strategy = WhitelistProtocolFilter(allowed_protocols)
        
        if name:
            self.register_protocol_strategy(name, strategy)
            
        return strategy
    
    def create_blacklist_protocol_strategy(
        self,
        blocked_protocols: Set[str],
        name: Optional[str] = None
    ) -> ProtocolFilterStrategy:
        """
        Create a blacklist protocol filter strategy.
        
        Args:
            blocked_protocols: Set of protocol types to block
            name: Optional name to register the strategy
            
        Returns:
            The blacklist filter strategy
        """
        strategy = BlacklistProtocolFilter(blocked_protocols)
        
        if name:
            self.register_protocol_strategy(name, strategy)
            
        return strategy
    
    def should_allow_protocol(
        self,
        protocol_type: str,
        protocol: BaseProtocol,
        strategy_name: Optional[str] = None
    ) -> bool:
        """
        Check if a protocol should be allowed using the specified strategy.
        
        Args:
            protocol_type: The type of protocol
            protocol: The protocol handler instance
            strategy_name: The name of the strategy to use
            
        Returns:
            True if the protocol should be allowed, False otherwise
        """
        strategy = None
        if strategy_name:
            strategy = self.get_protocol_strategy(strategy_name)
            if not strategy:
                logger.warning(f"Protocol strategy not found: {strategy_name}, using allow all")
                strategy = AllowAllProtocolFilter()
        else:
            strategy = AllowAllProtocolFilter()
        
        return strategy.should_allow(protocol_type, protocol)
    
    def list_protocol_strategies(self) -> List[str]:
        """
        List all registered protocol strategy names.
        
        Returns:
            List of protocol strategy names
        """
        return list(self.protocol_strategies.keys())
    
    def reset(self) -> None:
        """Reset all filters to their default state."""
        self.tool_strategies.clear()
        self.protocol_strategies.clear()
        
        # Register default tool strategies
        self.register_tool_strategy("threshold_5", ThresholdToolFilter(max_tools=5))
        self.register_tool_strategy("threshold_10", ThresholdToolFilter(max_tools=10))
        self.register_tool_strategy("priority", PriorityToolFilter(max_tools=5))
        
        # Register default protocol strategies
        self.register_protocol_strategy("allow_all", AllowAllProtocolFilter())
        self.register_protocol_strategy("deny_all", DenyAllProtocolFilter())
        self.register_protocol_strategy("http_only", WhitelistProtocolFilter({"http"}))
        self.register_protocol_strategy("sse_only", WhitelistProtocolFilter({"sse"}))
        self.register_protocol_strategy("websocket_only", WhitelistProtocolFilter({"websocket"}))
        
        # Ensure registry is available
        if self.registry is None:
            from backend.core.tools.filtered_registry import filtered_registry
            self.registry = filtered_registry
            
        logger.info("Reset all filter strategies to defaults")


# Create global filter manager instance
filter_manager = FilterManager()