"""
Protocol filtering strategies for the Faker Agent.

This module defines the base filter strategy class and several
implementations that can be used to filter protocol handlers
before they're used by the agent. These strategies provide
flexible control over which protocols are available in different
contexts and scenarios.
"""
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set, Type, Protocol, TYPE_CHECKING

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from backend.core.protocol.base_protocol import BaseProtocol

# Configure logger
logger = logging.getLogger(__name__)


class ProtocolFilterStrategy(ABC):
    """Base class for protocol filtering strategies."""
    
    @abstractmethod
    def should_allow(self, protocol_type: str, protocol: 'BaseProtocol') -> bool:
        """
        Determine if the protocol should be allowed based on the strategy.
        
        Args:
            protocol_type: The type of protocol
            protocol: The protocol handler instance
            
        Returns:
            True if the protocol should be allowed, False otherwise
        """
        pass


class AllowAllProtocolFilter(ProtocolFilterStrategy):
    """Filter strategy that allows all protocols."""
    
    def __init__(self):
        """Initialize the allow all filter."""
        logger.info("Initialized AllowAllProtocolFilter")
    
    def should_allow(self, protocol_type: str, protocol: 'BaseProtocol') -> bool:
        """
        Allow all protocols.
        
        Args:
            protocol_type: The type of protocol
            protocol: The protocol handler instance
            
        Returns:
            Always True
        """
        return True


class DenyAllProtocolFilter(ProtocolFilterStrategy):
    """Filter strategy that denies all protocols."""
    
    def __init__(self):
        """Initialize the deny all filter."""
        logger.info("Initialized DenyAllProtocolFilter")
    
    def should_allow(self, protocol_type: str, protocol: 'BaseProtocol') -> bool:
        """
        Deny all protocols.
        
        Args:
            protocol_type: The type of protocol
            protocol: The protocol handler instance
            
        Returns:
            Always False
        """
        return False


class WhitelistProtocolFilter(ProtocolFilterStrategy):
    """Filter strategy that allows only specified protocols."""
    
    def __init__(self, allowed_protocols: Set[str]):
        """
        Initialize the whitelist filter.
        
        Args:
            allowed_protocols: Set of protocol types to allow
        """
        self.allowed_protocols = {p.lower() for p in allowed_protocols}
        logger.info(f"Initialized WhitelistProtocolFilter with allowed_protocols={allowed_protocols}")
    
    def should_allow(self, protocol_type: str, protocol: 'BaseProtocol') -> bool:
        """
        Allow only protocols in the whitelist.
        
        Args:
            protocol_type: The type of protocol
            protocol: The protocol handler instance
            
        Returns:
            True if the protocol is in the whitelist, False otherwise
        """
        return protocol_type.lower() in self.allowed_protocols


class BlacklistProtocolFilter(ProtocolFilterStrategy):
    """Filter strategy that blocks specified protocols."""
    
    def __init__(self, blocked_protocols: Set[str]):
        """
        Initialize the blacklist filter.
        
        Args:
            blocked_protocols: Set of protocol types to block
        """
        self.blocked_protocols = {p.lower() for p in blocked_protocols}
        logger.info(f"Initialized BlacklistProtocolFilter with blocked_protocols={blocked_protocols}")
    
    def should_allow(self, protocol_type: str, protocol: 'BaseProtocol') -> bool:
        """
        Block protocols in the blacklist.
        
        Args:
            protocol_type: The type of protocol
            protocol: The protocol handler instance
            
        Returns:
            True if the protocol is not in the blacklist, False otherwise
        """
        return protocol_type.lower() not in self.blocked_protocols


class CompositeProtocolFilter(ProtocolFilterStrategy):
    """Composite filter that applies multiple strategies in sequence."""
    
    def __init__(self, strategies: List[ProtocolFilterStrategy]):
        """
        Initialize the composite filter.
        
        Args:
            strategies: List of filter strategies to apply in sequence
        """
        self.strategies = strategies
        logger.info(f"Initialized CompositeProtocolFilter with {len(strategies)} strategies")
    
    def should_allow(self, protocol_type: str, protocol: 'BaseProtocol') -> bool:
        """
        Apply multiple filter strategies in sequence.
        
        Args:
            protocol_type: The type of protocol
            protocol: The protocol handler instance
            
        Returns:
            True if all strategies allow the protocol, False otherwise
        """
        for strategy in self.strategies:
            if not strategy.should_allow(protocol_type, protocol):
                return False
        
        return True


# Factory function to create a filter strategy
def create_protocol_filter_strategy(strategy_type: str, **kwargs) -> ProtocolFilterStrategy:
    """
    Create a filter strategy instance based on the specified type.
    
    Args:
        strategy_type: The type of strategy to create
        **kwargs: Additional parameters for the strategy
        
    Returns:
        A ProtocolFilterStrategy instance
    """
    strategy_map: Dict[str, Type[ProtocolFilterStrategy]] = {
        'allow_all': AllowAllProtocolFilter,
        'deny_all': DenyAllProtocolFilter,
        'whitelist': WhitelistProtocolFilter,
        'blacklist': BlacklistProtocolFilter,
        'composite': CompositeProtocolFilter
    }
    
    if strategy_type not in strategy_map:
        raise ValueError(f"Unknown filter strategy type: {strategy_type}")
    
    strategy_class = strategy_map[strategy_type]
    return strategy_class(**kwargs)