"""
SSE (Server-Sent Events) protocol handler for the Faker Agent.
"""
import json
import logging
from typing import Any, AsyncGenerator, Dict, Optional

from fastapi.responses import StreamingResponse

from backend.core.graph.event_types import Event, EventType
from backend.core.protocol.base_protocol import BaseProtocol

# Configure logger
logger = logging.getLogger(__name__)


class SSEProtocol(BaseProtocol):
    """
    SSE protocol handler.
    
    This handler formats events as SSE messages for streaming responses.
    """
    
    async def handle_events(self, events: AsyncGenerator[Event, None], **kwargs) -> StreamingResponse:
        """
        Stream events as SSE messages.
        
        Args:
            events: Async generator of events from the orchestrator
            **kwargs: Additional SSE-specific parameters
            
        Returns:
            A StreamingResponse with SSE-formatted events
        """
        
        async def event_stream():
            try:
                async for event in events:
                    # Format the event as SSE
                    formatted_event = await self.format_event(event)
                    yield formatted_event
                    
                    # If this is a final or error event, end the stream
                    if event.type in [EventType.FINAL, EventType.ERROR]:
                        break
                        
            except Exception as e:
                logger.error(f"Error in SSE event stream: {e}")
                error_event = await self.format_error(str(e))
                yield error_event
        
        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream"
        )
    
    async def format_event(self, event: Event) -> str:
        """
        Format an event as an SSE message.
        
        Args:
            event: The event to format
            
        Returns:
            SSE-formatted event
        """
        # Convert event to JSON
        event_json = json.dumps(event.dict())
        
        # Format as SSE message
        return f"data: {event_json}\n\n"
    
    async def format_error(self, error: str, details: Optional[Dict[str, Any]] = None) -> str:
        """
        Format an error as an SSE message.
        
        Args:
            error: The error message
            details: Optional error details
            
        Returns:
            SSE-formatted error
        """
        error_data = {
            "type": "error",
            "error": error
        }
        
        if details:
            error_data["details"] = details
            
        error_json = json.dumps(error_data)
        return f"data: {error_json}\n\n"