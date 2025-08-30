"""
Unit tests for the WebSocket protocol handler.
"""
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import json
import time

from fastapi import WebSocket

from backend.core.graph.event_types import Event, EventType
from backend.core.protocol.websocket_protocol import WebSocketProtocol


class TestWebSocketProtocol(unittest.TestCase):
    """Test cases for the WebSocketProtocol class."""

    def setUp(self):
        """Set up the test case."""
        self.protocol = WebSocketProtocol()
        
        # Create sample events
        start_time = time.time()
        self.event = Event(
            type=EventType.TOOL_CALL_START,
            tool_name="weather",
            tool_args={"city": "San Francisco"},
            tool_call_id="123",
            timestamp=start_time
        )
        
        self.error_event = Event(
            type=EventType.ERROR,
            error="Failed to execute tool",
            stack_trace="Traceback...",
            timestamp=start_time + 1
        )
        
        # Create a mock WebSocket
        self.websocket = AsyncMock(spec=WebSocket)

    async def test_format_event(self):
        """Test formatting an event for WebSocket."""
        formatted = await self.protocol.format_event(self.event)
        
        # Verify the event data
        self.assertEqual(formatted["type"], "tool_call_start")
        self.assertEqual(formatted["tool_name"], "weather")
        self.assertEqual(formatted["tool_args"], {"city": "San Francisco"})

    async def test_format_error(self):
        """Test formatting an error for WebSocket."""
        error = "Test error"
        details = {"code": "TEST_ERROR", "source": "test"}
        
        formatted = await self.protocol.format_error(error, details)
        
        # Verify the error data
        self.assertEqual(formatted["type"], "error")
        self.assertEqual(formatted["error"], "Test error")
        self.assertEqual(formatted["details"], details)

    async def test_handle_events(self):
        """Test handling events and sending them to the WebSocket."""
        # Create an async generator that yields events
        async def event_generator():
            yield self.event
            yield Event(
                type=EventType.FINAL,
                response="The weather in San Francisco is sunny.",
                timestamp=time.time() + 2
            )
            
        # Call handle_events
        await self.protocol.handle_events(event_generator(), self.websocket)
        
        # Verify that send_json was called for each event
        self.assertEqual(self.websocket.send_json.call_count, 2)
        
        # Verify the first event was sent correctly
        first_call_args = self.websocket.send_json.call_args_list[0][0][0]
        self.assertEqual(first_call_args["type"], "tool_call_start")
        self.assertEqual(first_call_args["tool_name"], "weather")

    async def test_handle_events_with_error(self):
        """Test handling events with an error."""
        # Create an async generator that raises an exception
        async def failing_generator():
            raise ValueError("Test error")
            yield self.event  # This won't be reached
            
        # Call handle_events
        await self.protocol.handle_events(failing_generator(), self.websocket)
        
        # Verify that send_json was called with an error event
        self.websocket.send_json.assert_called_once()
        error_event = self.websocket.send_json.call_args[0][0]
        self.assertEqual(error_event["type"], "error")
        self.assertEqual(error_event["error"], "Test error")

    async def test_handle_events_with_websocket_error(self):
        """Test handling WebSocket send errors."""
        # Create an async generator that yields events
        async def event_generator():
            yield self.event
            
        # Make the websocket.send_json raise an exception
        self.websocket.send_json.side_effect = Exception("Connection closed")
        
        # Call handle_events (should handle the exception gracefully)
        with self.assertLogs(level='ERROR') as cm:
            await self.protocol.handle_events(event_generator(), self.websocket)
            self.assertIn("Error in WebSocket event stream", cm.output[0])


if __name__ == '__main__':
    unittest.main()