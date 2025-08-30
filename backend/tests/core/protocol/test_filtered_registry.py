"""
Unit tests for the filtered protocol registry.
"""
import unittest
from unittest.mock import patch, MagicMock

from backend.core.contracts.protocol import ProtocolType
from backend.core.filters.filter_manager import FilterManager
from backend.core.protocol.base_protocol import BaseProtocol
from backend.core.protocol.filtered_registry import FilteredProtocolRegistry
from backend.core.protocol.protocol_factory import ProtocolFactory


class TestFilteredProtocolRegistry(unittest.TestCase):
    """Test cases for the FilteredProtocolRegistry class."""

    def setUp(self):
        """Set up the test case."""
        self.protocol_factory = MagicMock(spec=ProtocolFactory)
        self.filter_manager = MagicMock(spec=FilterManager)
        
        # Create mock protocols
        self.http_protocol = MagicMock(spec=BaseProtocol)
        self.sse_protocol = MagicMock(spec=BaseProtocol)
        self.ws_protocol = MagicMock(spec=BaseProtocol)
        
        # Configure protocol factory mock
        self.protocol_factory.get_protocol.side_effect = lambda pt: {
            "http": self.http_protocol,
            "sse": self.sse_protocol,
            "websocket": self.ws_protocol
        }.get(pt.lower())
        
        # Create registry with mocked dependencies
        with patch('backend.core.protocol.filtered_registry.FilterManager', return_value=self.filter_manager):
            self.registry = FilteredProtocolRegistry(protocol_factory=self.protocol_factory)

    def test_initialization(self):
        """Test that the registry initializes with all protocols enabled."""
        # Check all protocols are enabled
        for protocol_type in ProtocolType:
            self.assertIn(protocol_type.value, self.registry._enabled_protocols)
            self.assertNotIn(protocol_type.value, self.registry._disabled_protocols)

    def test_register_protocol(self):
        """Test registering a protocol."""
        mock_protocol = MagicMock(spec=BaseProtocol)
        self.registry.register_protocol("custom", mock_protocol)
        
        # Check that protocol was registered
        self.protocol_factory.register_protocol.assert_called_once_with("custom", mock_protocol)
        self.assertIn("custom", self.registry._enabled_protocols)

    def test_enable_disable_protocol(self):
        """Test enabling and disabling protocols."""
        # Disable a protocol
        self.registry.disable_protocol("http")
        self.assertNotIn("http", self.registry._enabled_protocols)
        self.assertIn("http", self.registry._disabled_protocols)
        
        # Enable it again
        self.registry.enable_protocol("http")
        self.assertIn("http", self.registry._enabled_protocols)
        self.assertNotIn("http", self.registry._disabled_protocols)

    def test_get_protocol(self):
        """Test getting a protocol that passes all checks."""
        # Configure filter manager to allow the protocol
        self.filter_manager.should_allow_protocol.return_value = True
        
        # Get a protocol
        protocol = self.registry.get_protocol("http")
        
        # Verify correct protocol was returned
        self.assertEqual(protocol, self.http_protocol)
        self.filter_manager.should_allow_protocol.assert_called_once_with("http", self.http_protocol)

    def test_get_disabled_protocol(self):
        """Test getting a disabled protocol."""
        # Disable the protocol
        self.registry.disable_protocol("http")
        
        # Get the protocol
        protocol = self.registry.get_protocol("http")
        
        # Verify None was returned
        self.assertIsNone(protocol)
        self.filter_manager.should_allow_protocol.assert_not_called()

    def test_get_filtered_protocol(self):
        """Test getting a protocol that doesn't pass filters."""
        # Configure filter manager to block the protocol
        self.filter_manager.should_allow_protocol.return_value = False
        
        # Get a protocol
        protocol = self.registry.get_protocol("http")
        
        # Verify None was returned
        self.assertIsNone(protocol)
        self.filter_manager.should_allow_protocol.assert_called_once_with("http", self.http_protocol)

    def test_get_unavailable_protocol(self):
        """Test getting a protocol that doesn't exist."""
        # Configure protocol factory to return None
        self.protocol_factory.get_protocol.return_value = None
        
        # Get a protocol
        protocol = self.registry.get_protocol("nonexistent")
        
        # Verify None was returned
        self.assertIsNone(protocol)

    def test_get_available_protocols(self):
        """Test getting available protocols."""
        # Configure filter manager to allow http and sse but block websocket
        self.filter_manager.should_allow_protocol.side_effect = lambda pt, p: pt != "websocket"
        
        # Get available protocols
        available = self.registry.get_available_protocols()
        
        # Verify correct protocols were returned
        self.assertIn("http", available)
        self.assertIn("sse", available)
        self.assertNotIn("websocket", available)

    def test_reset_filters(self):
        """Test resetting filters."""
        self.registry.reset_filters()
        self.filter_manager.reset.assert_called_once()


if __name__ == '__main__':
    unittest.main()