"""
SSE (Server-Sent Events) protocol handler for the Faker Agent.
"""
import json
import logging
import time
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
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
                "X-Accel-Buffering": "no"
            }
        )
    
    async def format_event(self, event: Event) -> str:
        """
        Format an event as an SSE message.
        
        Args:
            event: The event to format
            
        Returns:
            SSE-formatted event
        """
        try:
            # Convert event to JSON
            # Use model_dump for newer Pydantic or dict() for older versions
            if hasattr(event, "model_dump"):
                event_data = event.model_dump()
            elif hasattr(event, "dict"):
                event_data = event.dict()
            else:
                # Fallback for non-Pydantic objects
                event_data = {
                    "type": str(event.type),
                    "timestamp": getattr(event, "timestamp", time.time())
                }
                
                # Add other attributes based on event type
                if hasattr(event, "response"):
                    event_data["response"] = event.response
                if hasattr(event, "actions"):
                    event_data["actions"] = event.actions
                if hasattr(event, "tool_name"):
                    event_data["tool_name"] = event.tool_name
                if hasattr(event, "tool_args"):
                    event_data["tool_args"] = event.tool_args
                if hasattr(event, "tool_call_id"):
                    event_data["tool_call_id"] = event.tool_call_id
                if hasattr(event, "result"):
                    event_data["result"] = event.result
                if hasattr(event, "error"):
                    event_data["error"] = event.error
                if hasattr(event, "token"):
                    event_data["token"] = event.token
                if hasattr(event, "is_partial"):
                    event_data["is_partial"] = event.is_partial
            
            # Convert to JSON with error handling
            event_json = json.dumps(event_data)
            
            # Format as SSE message
            return f"data: {event_json}\n\n"
            
        except Exception as e:
            logger.error(f"Error formatting SSE event: {e}")
            # Return a simplified error event as fallback
            error_data = {
                "type": "error",
                "timestamp": time.time(),
                "error": f"Error formatting event: {str(e)}"
            }
            return f"data: {json.dumps(error_data)}\n\n"
    
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