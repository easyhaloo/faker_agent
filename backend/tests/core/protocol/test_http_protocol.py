"""
Unit tests for the HTTP protocol handler.
"""
import unittest
from unittest.mock import patch, MagicMock
import time

from backend.core.graph.event_types import Event, EventType
from backend.core.protocol.http_protocol import HTTPProtocol


class TestHTTPProtocol(unittest.TestCase):
    """Test cases for the HTTPProtocol class."""

    def setUp(self):
        """Set up the test case."""
        self.protocol = HTTPProtocol()
        
        # Create sample events
        start_time = time.time()
        self.events = [
            Event(
                type=EventType.TOOL_CALL_START,
                tool_name="weather",
                tool_args={"city": "San Francisco"},
                tool_call_id="123",
                timestamp=start_time
            ),
            Event(
                type=EventType.TOOL_CALL_RESULT,
                tool_call_id="123",
                result={"temperature": 72, "condition": "sunny"},
                error=None,
                timestamp=start_time + 1
            ),
            Event(
                type=EventType.FINAL,
                response="The weather in San Francisco is sunny with a temperature of 72°F.",
                timestamp=start_time + 2
            )
        ]
        
        # Sample error event
        self.error_event = Event(
            type=EventType.ERROR,
            error="Failed to execute tool",
            stack_trace="Traceback...",
            timestamp=start_time + 1
        )

    async def test_handle_events(self):
        """Test handling a list of events."""
        result = await self.protocol.handle_events(self.events)
        
        # Check for success status
        self.assertEqual(result["status"], "success")
        
        # Check for correct response
        self.assertEqual(
            result["data"]["response"], 
            "The weather in San Francisco is sunny with a temperature of 72°F."
        )
        
        # Check for correct tool calls
        tool_calls = result["data"]["tool_calls"]
        self.assertEqual(len(tool_calls), 1)
        self.assertEqual(tool_calls[0]["tool_name"], "weather")
        self.assertEqual(tool_calls[0]["tool_args"], {"city": "San Francisco"})
        self.assertEqual(tool_calls[0]["status"], "completed")
        self.assertEqual(tool_calls[0]["result"], {"temperature": 72, "condition": "sunny"})

    async def test_handle_error_event(self):
        """Test handling an error event."""
        result = await self.protocol.handle_events([self.error_event])
        
        # Check for error status
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error"]["message"], "Failed to execute tool")

    async def test_format_event(self):
        """Test formatting an event."""
        event = self.events[0]
        formatted = await self.protocol.format_event(event)
        
        # Verify the event was formatted correctly
        self.assertEqual(formatted["type"], "tool_call_start")
        self.assertEqual(formatted["tool_name"], "weather")
        self.assertEqual(formatted["tool_args"], {"city": "San Francisco"})

    async def test_format_error(self):
        """Test formatting an error."""
        error = "Test error"
        details = {"code": "TEST_ERROR", "source": "test"}
        
        error_response = await self.protocol.format_error(error, details)
        
        # Verify error format
        self.assertEqual(error_response["status"], "error")
        self.assertEqual(error_response["error"]["code"], "PROTOCOL_ERROR")
        self.assertEqual(error_response["error"]["message"], "Test error")
        self.assertEqual(error_response["error"]["details"], details)


if __name__ == '__main__':
    unittest.main()