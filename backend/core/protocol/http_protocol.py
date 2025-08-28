"""
HTTP protocol handler for the Faker Agent.
"""
import logging
from typing import Any, Dict, List, Optional

from backend.core.graph.event_types import Event, EventType
from backend.core.protocol.base_protocol import BaseProtocol

# Configure logger
logger = logging.getLogger(__name__)


class HTTPProtocol(BaseProtocol):
    """
    HTTP protocol handler.
    
    This handler collects all events and returns a single JSON response
    when the execution is complete.
    """
    
    async def handle_events(self, events: List[Event], **kwargs) -> Dict[str, Any]:
        """
        Collect all events and return a single response.
        
        Args:
            events: List of events from the orchestrator
            **kwargs: Additional HTTP-specific parameters
            
        Returns:
            A JSON response with the final result and actions
        """
        # Collect tool calls and their results
        tool_calls = []
        for event in events:
            if event.type == EventType.TOOL_CALL_START:
                tool_calls.append({
                    "tool_name": event.tool_name,
                    "tool_args": event.tool_args,
                    "tool_call_id": event.tool_call_id,
                    "status": "started",
                    "timestamp": event.timestamp
                })
            elif event.type == EventType.TOOL_CALL_RESULT:
                # Update existing tool call with result
                for tool_call in tool_calls:
                    if tool_call["tool_call_id"] == event.tool_call_id:
                        tool_call["status"] = "completed"
                        tool_call["result"] = event.result
                        tool_call["error"] = event.error
                        break
        
        # Get the final response
        final_response = None
        error = None
        for event in events:
            if event.type == EventType.FINAL:
                final_response = event.response
                break
            elif event.type == EventType.ERROR:
                error = event.error
                break
        
        # Build the response
        if error:
            return {
                "status": "error",
                "error": {
                    "code": "EXECUTION_ERROR",
                    "message": error
                }
            }
        else:
            return {
                "status": "success",
                "data": {
                    "response": final_response,
                    "tool_calls": tool_calls,
                    "execution_time": events[-1].timestamp - events[0].timestamp if events else 0
                }
            }
    
    async def format_event(self, event: Event) -> Dict[str, Any]:
        """
        Format an event for HTTP response.
        
        Note: This is mainly for internal use, as HTTP protocol
        combines all events into a single response.
        
        Args:
            event: The event to format
            
        Returns:
            Formatted event as JSON
        """
        return event.dict()
    
    async def format_error(self, error: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Format an error response for HTTP.
        
        Args:
            error: The error message
            details: Optional error details
            
        Returns:
            Error response as JSON
        """
        response = {
            "status": "error",
            "error": {
                "code": "PROTOCOL_ERROR",
                "message": error
            }
        }
        
        if details:
            response["error"]["details"] = details
            
        return response