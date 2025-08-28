"""
WebSocket protocol handler for the Faker Agent.
"""
import json
import logging
from typing import Any, AsyncGenerator, Dict, Optional

from fastapi import WebSocket

from backend.core.graph.event_types import Event
from backend.core.protocol.base_protocol import BaseProtocol

# Configure logger
logger = logging.getLogger(__name__)


class WebSocketProtocol(BaseProtocol):
    """
    WebSocket protocol handler.
    
    This handler formats events as WebSocket messages for real-time
    bidirectional communication.
    """
    
    async def handle_events(
        self, 
        events: AsyncGenerator[Event, None], 
        websocket: WebSocket,
        **kwargs
    ) -> None:
        """
        Stream events as WebSocket messages.
        
        Args:
            events: Async generator of events from the orchestrator
            websocket: The WebSocket connection
            **kwargs: Additional WebSocket-specific parameters
        """
        try:
            async for event in events:
                # Format the event for WebSocket
                formatted_event = await self.format_event(event)
                
                # Send the event to the client
                await websocket.send_json(formatted_event)
                
        except Exception as e:
            logger.error(f"Error in WebSocket event stream: {e}")
            error_event = await self.format_error(str(e))
            
            try:
                await websocket.send_json(error_event)
            except Exception as send_error:
                logger.error(f"Error sending error event: {send_error}")
    
    async def format_event(self, event: Event) -> Dict[str, Any]:
        """
        Format an event for WebSocket transmission.
        
        Args:
            event: The event to format
            
        Returns:
            Formatted event as a dictionary
        """
        return event.dict()
    
    async def format_error(self, error: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Format an error for WebSocket transmission.
        
        Args:
            error: The error message
            details: Optional error details
            
        Returns:
            Formatted error as a dictionary
        """
        error_data = {
            "type": "error",
            "error": error
        }
        
        if details:
            error_data["details"] = details
            
        return error_data