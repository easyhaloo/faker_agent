"""
Filtered protocol registry for managing protocol handlers.

This module provides a filtered registry for protocol handlers,
allowing for dynamic registration and filtering of protocol handlers.
"""
import logging
from typing import Dict, List, Optional, Set, Type, TYPE_CHECKING, Any

from backend.core.contracts.protocol import ProtocolType
from backend.core.protocol.base_protocol import BaseProtocol
from backend.core.protocol.protocol_factory import ProtocolFactory

# Use TYPE_CHECKING to avoid circular imports during type checking
if TYPE_CHECKING:
    from backend.core.filters.filter_manager import FilterManager

# Configure logger
logger = logging.getLogger(__name__)


class FilteredProtocolRegistry:
    """
    Filtered registry for protocol handlers.
    
    This class extends the ProtocolFactory to provide filtering capabilities,
    allowing for dynamic registration and filtering of protocol handlers
    based on various criteria.
    """
    
    def __init__(self, protocol_factory: Optional[ProtocolFactory] = None):
        """
        Initialize the filtered protocol registry.
        
        Args:
            protocol_factory: Optional protocol factory to use, creates a new one if not provided
        """
        self._protocol_factory = protocol_factory or ProtocolFactory()
        # We'll set the filter_manager later to avoid circular imports
        self._filter_manager = None
        self._enabled_protocols: Set[str] = set()
        self._disabled_protocols: Set[str] = set()
        
        # By default, enable all registered protocols
        for protocol_type in ProtocolType:
            self._enabled_protocols.add(protocol_type.value)
            
        logger.info("Initialized FilteredProtocolRegistry")
    
    def register_protocol(self, protocol_type: str, protocol: BaseProtocol) -> None:
        """
        Register a protocol handler.
        
        Args:
            protocol_type: The type of protocol
            protocol: The protocol handler instance
        """
        self._protocol_factory.register_protocol(protocol_type, protocol)
        # Enable the protocol by default
        self._enabled_protocols.add(protocol_type.lower())
        logger.info(f"Registered protocol handler: {protocol_type}")
    
    def enable_protocol(self, protocol_type: str) -> None:
        """
        Enable a protocol handler.
        
        Args:
            protocol_type: The type of protocol to enable
        """
        protocol_type = protocol_type.lower()
        self._enabled_protocols.add(protocol_type)
        if protocol_type in self._disabled_protocols:
            self._disabled_protocols.remove(protocol_type)
        logger.info(f"Enabled protocol: {protocol_type}")
    
    def disable_protocol(self, protocol_type: str) -> None:
        """
        Disable a protocol handler.
        
        Args:
            protocol_type: The type of protocol to disable
        """
        protocol_type = protocol_type.lower()
        self._disabled_protocols.add(protocol_type)
        if protocol_type in self._enabled_protocols:
            self._enabled_protocols.remove(protocol_type)
        logger.info(f"Disabled protocol: {protocol_type}")
    
    def set_filter_manager(self, filter_manager: Any) -> None:
        """
        Set the filter manager.
        
        Args:
            filter_manager: The filter manager instance
        """
        self._filter_manager = filter_manager
        logger.info("Filter manager set for FilteredProtocolRegistry")
    
    def get_protocol(self, protocol_type: str) -> Optional[BaseProtocol]:
        """
        Get a protocol handler if it's enabled and passes all filters.
        
        Args:
            protocol_type: The type of protocol
            
        Returns:
            A protocol handler instance or None if not found or filtered out
        """
        protocol_type = protocol_type.lower()
        
        # Check if protocol is disabled
        if protocol_type in self._disabled_protocols:
            logger.debug(f"Protocol is disabled: {protocol_type}")
            return None
            
        # Check if protocol is enabled
        if protocol_type not in self._enabled_protocols:
            logger.debug(f"Protocol is not enabled: {protocol_type}")
            return None
        
        # Get the protocol handler from the factory
        protocol = self._protocol_factory.get_protocol(protocol_type)
        if not protocol:
            logger.debug(f"Protocol not found: {protocol_type}")
            return None
        
        # Apply filters if filter_manager is set
        if self._filter_manager is not None:
            if not self._filter_manager.should_allow_protocol(protocol_type, protocol):
                logger.debug(f"Protocol filtered out: {protocol_type}")
                return None
            
        return protocol
    
    def get_available_protocols(self) -> List[str]:
        """
        Get a list of available protocol types that are enabled and pass all filters.
        
        Returns:
            List of available protocol types
        """
        available_protocols = []
        
        for protocol_type in ProtocolType:
            protocol_value = protocol_type.value
            
            # Skip disabled protocols
            if protocol_value in self._disabled_protocols:
                continue
                
            # Check if protocol is enabled
            if protocol_value not in self._enabled_protocols:
                continue
            
            # Get the protocol handler
            protocol = self._protocol_factory.get_protocol(protocol_value)
            if not protocol:
                continue
            
            # Apply filters if filter_manager is set
            if self._filter_manager is None or self._filter_manager.should_allow_protocol(protocol_value, protocol):
                available_protocols.append(protocol_value)
                
        return available_protocols
    
    def reset_filters(self) -> None:
        """Reset all protocol filters to their default state."""
        if self._filter_manager is not None:
            self._filter_manager.reset()
            logger.info("Reset all protocol filters")
        else:
            logger.warning("Cannot reset filters: filter_manager not set")
    
    @property
    def protocol_factory(self) -> ProtocolFactory:
        """Get the underlying protocol factory."""
        return self._protocol_factory
    
    @property
    def filter_manager(self) -> Any:
        """Get the filter manager."""
        return self._filter_manager


# Create global filtered protocol registry instance
filtered_protocol_registry = FilteredProtocolRegistry()