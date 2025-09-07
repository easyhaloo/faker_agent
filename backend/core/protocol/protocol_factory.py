"""
Protocol factory for creating protocol handlers.
"""
import logging
from enum import Enum
from typing import Optional, Any

from backend.core.protocol.base_protocol import BaseProtocol
from backend.core.protocol.http_protocol import HTTPProtocol
from backend.core.protocol.sse_protocol import SSEProtocol
from backend.core.protocol.websocket_protocol import WebSocketProtocol

# Configure logger
logger = logging.getLogger(__name__)


class ProtocolType(str, Enum):
    """Protocol types supported by the factory."""
    
    HTTP = "http"
    SSE = "sse"
    WEBSOCKET = "websocket"


class ProtocolFactory:
    """
    Factory for creating protocol handlers.
    
    This class provides a central point for creating protocol handlers
    based on the requested protocol type.
    """
    
    def __init__(self):
        """Initialize the protocol factory."""
        self._protocols = {}
        self._filtered_registry = None  # Will be set later to avoid circular imports
        
        # Use elegant logging for initialization (moved to avoid circular imports)
        # log_initialization will be called after all imports are complete
    
    def get_protocol(self, protocol_type: str) -> Optional[BaseProtocol]:
        """
        Get a protocol handler by type.
        
        Args:
            protocol_type: The type of protocol
            
        Returns:
            A protocol handler instance or None if not found
        """
        try:
            protocol_enum = ProtocolType(protocol_type.lower())
            return self._protocols.get(protocol_enum)
        except ValueError:
            logger.warning(f"Unknown protocol type: {protocol_type}")
            return None
    
    def register_protocol(self, protocol_type: str, protocol: BaseProtocol) -> None:
        """
        Register a custom protocol handler.
        
        Args:
            protocol_type: The type of protocol
            protocol: The protocol handler instance
        """
        try:
            protocol_enum = ProtocolType(protocol_type.lower())
            self._protocols[protocol_enum] = protocol
            logger.info(f"Registered custom protocol: {protocol_type}")
        except ValueError:
            logger.warning(f"Invalid protocol type: {protocol_type}")
    
    def set_filtered_registry(self, filtered_registry: Any) -> None:
        """
        Set the filtered registry to avoid circular imports.
        
        Args:
            filtered_registry: The filtered protocol registry instance
        """
        self._filtered_registry = filtered_registry
        logger.info("Set filtered registry for protocol factory")


# Create global protocol factory instance
protocol_factory = ProtocolFactory()