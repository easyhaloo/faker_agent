"""
Unit tests for the SSE protocol handler.
"""
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import json
import time

from fastapi.responses import StreamingResponse

from backend.core.graph.event_types import Event, EventType
from backend.core.protocol.sse_protocol import SSEProtocol


class TestSSEProtocol(unittest.TestCase):
    """Test cases for the SSEProtocol class."""

    def setUp(self):
        """Set up the test case."""
        self.protocol = SSEProtocol()
        
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
        
        # Create an async generator that yields events
        async def event_generator():
            yield self.event
            yield Event(
                type=EventType.FINAL,
                response="The weather in San Francisco is sunny.",
                timestamp=start_time + 2
            )
            
        self.events = event_generator()

    async def test_format_event(self):
        """Test formatting an event as SSE."""
        formatted = await self.protocol.format_event(self.event)
        
        # Should be in SSE format: data: {json}\n\n
        self.assertTrue(formatted.startswith("data: "))
        self.assertTrue(formatted.endswith("\n\n"))
        
        # Extract the JSON
        json_str = formatted[6:-2]  # Remove "data: " and "\n\n"
        event_data = json.loads(json_str)
        
        # Verify the event data
        self.assertEqual(event_data["type"], "tool_call_start")
        self.assertEqual(event_data["tool_name"], "weather")
        self.assertEqual(event_data["tool_args"], {"city": "San Francisco"})

    async def test_format_error(self):
        """Test formatting an error as SSE."""
        error = "Test error"
        details = {"code": "TEST_ERROR", "source": "test"}
        
        formatted = await self.protocol.format_error(error, details)
        
        # Should be in SSE format: data: {json}\n\n
        self.assertTrue(formatted.startswith("data: "))
        self.assertTrue(formatted.endswith("\n\n"))
        
        # Extract the JSON
        json_str = formatted[6:-2]  # Remove "data: " and "\n\n"
        error_data = json.loads(json_str)
        
        # Verify the error data
        self.assertEqual(error_data["type"], "error")
        self.assertEqual(error_data["error"], "Test error")
        self.assertEqual(error_data["details"], details)

    @patch("backend.core.protocol.sse_protocol.StreamingResponse")
    async def test_handle_events(self, mock_streaming_response):
        """Test handling events and returning a streaming response."""
        # Mock the StreamingResponse
        mock_response = MagicMock(spec=StreamingResponse)
        mock_streaming_response.return_value = mock_response
        
        # Call handle_events
        response = await self.protocol.handle_events(self.events)
        
        # Verify that StreamingResponse was called
        mock_streaming_response.assert_called_once()
        self.assertEqual(response, mock_response)
        
        # Verify media type
        mock_streaming_response.assert_called_with(
            mock_streaming_response.call_args[0][0],
            media_type="text/event-stream"
        )

    @patch("backend.core.protocol.sse_protocol.StreamingResponse")
    async def test_handle_events_with_error(self, mock_streaming_response):
        """Test handling events with an error."""
        # Create an async generator that raises an exception
        async def failing_generator():
            raise ValueError("Test error")
            
        # Mock the StreamingResponse to capture the event generator
        def capture_generator(gen, **kwargs):
            capture_generator.gen = gen
            return MagicMock(spec=StreamingResponse)
            
        mock_streaming_response.side_effect = capture_generator
        
        # Call handle_events
        await self.protocol.handle_events(failing_generator())
        
        # Get the generator that was passed to StreamingResponse
        event_stream = capture_generator.gen
        
        # Try to consume the first event (should be an error event)
        formatted_error = await event_stream.__anext__()
        
        # Verify it's an error event
        self.assertTrue(formatted_error.startswith("data: "))
        json_str = formatted_error[6:-2]  # Remove "data: " and "\n\n"
        error_data = json.loads(json_str)
        self.assertEqual(error_data["type"], "error")
        self.assertEqual(error_data["error"], "Test error")


if __name__ == '__main__':
    unittest.main()