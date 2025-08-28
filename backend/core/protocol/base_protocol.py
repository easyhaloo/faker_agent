"""
Base protocol class for the Faker Agent.
"""
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from backend.core.graph.event_types import Event

# Configure logger
logger = logging.getLogger(__name__)


class BaseProtocol(ABC):
    """
    Base class for all communication protocols.
    
    This class defines the interface for all protocol handlers,
    which are responsible for converting the unified event format
    to protocol-specific responses.
    """
    
    @abstractmethod
    async def handle_events(self, events, **kwargs):
        """
        Handle events from the orchestrator.
        
        Args:
            events: Events from the orchestrator
            **kwargs: Additional protocol-specific parameters
            
        Returns:
            Protocol-specific response
        """
        pass
    
    @abstractmethod
    async def format_event(self, event: Event) -> Any:
        """
        Format an event for the specific protocol.
        
        Args:
            event: The event to format
            
        Returns:
            Protocol-specific formatted event
        """
        pass
    
    @abstractmethod
    async def format_error(self, error: str, details: Optional[Dict[str, Any]] = None) -> Any:
        """
        Format an error response for the specific protocol.
        
        Args:
            error: The error message
            details: Optional error details
            
        Returns:
            Protocol-specific error response
        """
        pass