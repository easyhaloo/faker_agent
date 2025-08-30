"""
Unit tests for the protocol factory.
"""
import unittest
from unittest.mock import patch, MagicMock

from backend.core.protocol.base_protocol import BaseProtocol
from backend.core.protocol.http_protocol import HTTPProtocol
from backend.core.protocol.protocol_factory import ProtocolFactory, ProtocolType
from backend.core.protocol.sse_protocol import SSEProtocol
from backend.core.protocol.websocket_protocol import WebSocketProtocol


class TestProtocolFactory(unittest.TestCase):
    """Test cases for the ProtocolFactory class."""

    def setUp(self):
        """Set up the test case."""
        self.factory = ProtocolFactory()

    def test_initialization(self):
        """Test that the factory initializes with correct protocols."""
        self.assertIsInstance(self.factory._protocols[ProtocolType.HTTP], HTTPProtocol)
        self.assertIsInstance(self.factory._protocols[ProtocolType.SSE], SSEProtocol)
        self.assertIsInstance(self.factory._protocols[ProtocolType.WEBSOCKET], WebSocketProtocol)

    def test_get_protocol(self):
        """Test getting protocols by type."""
        http_protocol = self.factory.get_protocol("http")
        sse_protocol = self.factory.get_protocol("sse")
        ws_protocol = self.factory.get_protocol("websocket")

        self.assertIsInstance(http_protocol, HTTPProtocol)
        self.assertIsInstance(sse_protocol, SSEProtocol)
        self.assertIsInstance(ws_protocol, WebSocketProtocol)

    def test_get_protocol_case_insensitive(self):
        """Test that protocol type is case insensitive."""
        http_protocol = self.factory.get_protocol("HTTP")
        self.assertIsInstance(http_protocol, HTTPProtocol)

    def test_get_invalid_protocol(self):
        """Test getting an invalid protocol type."""
        with self.assertLogs(level='WARNING') as cm:
            protocol = self.factory.get_protocol("invalid")
            self.assertIsNone(protocol)
            self.assertIn("Unknown protocol type: invalid", cm.output[0])

    def test_register_protocol(self):
        """Test registering a custom protocol."""
        # Create a mock protocol
        mock_protocol = MagicMock(spec=BaseProtocol)
        
        # Register the mock protocol
        self.factory.register_protocol("http", mock_protocol)
        
        # Get the protocol and verify it's our mock
        protocol = self.factory.get_protocol("http")
        self.assertEqual(protocol, mock_protocol)

    def test_register_invalid_protocol(self):
        """Test registering with an invalid protocol type."""
        mock_protocol = MagicMock(spec=BaseProtocol)
        
        with self.assertLogs(level='WARNING') as cm:
            self.factory.register_protocol("invalid", mock_protocol)
            self.assertIn("Invalid protocol type: invalid", cm.output[0])


if __name__ == '__main__':
    unittest.main()