"""
Protocol factory for creating protocol handlers.
"""
import logging
from enum import Enum
from typing import Optional

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
        self._protocols = {
            ProtocolType.HTTP: HTTPProtocol(),
            ProtocolType.SSE: SSEProtocol(),
            ProtocolType.WEBSOCKET: WebSocketProtocol()
        }
        logger.info("Initialized ProtocolFactory")
    
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


# Create global protocol factory instance
protocol_factory = ProtocolFactory()