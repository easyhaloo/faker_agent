"""
Unit tests for protocol filter strategies.
"""
import unittest
from unittest.mock import patch, MagicMock

from backend.core.filters.protocol_filter_strategy import (
    AllowAllProtocolFilter,
    BlacklistProtocolFilter,
    CompositeProtocolFilter,
    DenyAllProtocolFilter,
    ProtocolFilterStrategy,
    WhitelistProtocolFilter,
    create_protocol_filter_strategy
)
from backend.core.protocol.base_protocol import BaseProtocol


class TestProtocolFilterStrategies(unittest.TestCase):
    """Test cases for protocol filtering strategies."""

    def setUp(self):
        """Set up the test case."""
        # Create a mock protocol
        self.protocol = MagicMock(spec=BaseProtocol)

    def test_allow_all_filter(self):
        """Test the AllowAllProtocolFilter."""
        filter_strategy = AllowAllProtocolFilter()
        self.assertTrue(filter_strategy.should_allow("http", self.protocol))
        self.assertTrue(filter_strategy.should_allow("sse", self.protocol))
        self.assertTrue(filter_strategy.should_allow("websocket", self.protocol))

    def test_deny_all_filter(self):
        """Test the DenyAllProtocolFilter."""
        filter_strategy = DenyAllProtocolFilter()
        self.assertFalse(filter_strategy.should_allow("http", self.protocol))
        self.assertFalse(filter_strategy.should_allow("sse", self.protocol))
        self.assertFalse(filter_strategy.should_allow("websocket", self.protocol))

    def test_whitelist_filter(self):
        """Test the WhitelistProtocolFilter."""
        filter_strategy = WhitelistProtocolFilter({"http", "sse"})
        self.assertTrue(filter_strategy.should_allow("http", self.protocol))
        self.assertTrue(filter_strategy.should_allow("sse", self.protocol))
        self.assertFalse(filter_strategy.should_allow("websocket", self.protocol))

    def test_whitelist_filter_case_insensitive(self):
        """Test that the whitelist filter is case insensitive."""
        filter_strategy = WhitelistProtocolFilter({"http"})
        self.assertTrue(filter_strategy.should_allow("HTTP", self.protocol))

    def test_blacklist_filter(self):
        """Test the BlacklistProtocolFilter."""
        filter_strategy = BlacklistProtocolFilter({"websocket"})
        self.assertTrue(filter_strategy.should_allow("http", self.protocol))
        self.assertTrue(filter_strategy.should_allow("sse", self.protocol))
        self.assertFalse(filter_strategy.should_allow("websocket", self.protocol))

    def test_blacklist_filter_case_insensitive(self):
        """Test that the blacklist filter is case insensitive."""
        filter_strategy = BlacklistProtocolFilter({"http"})
        self.assertFalse(filter_strategy.should_allow("HTTP", self.protocol))

    def test_composite_filter_all_allow(self):
        """Test the CompositeProtocolFilter when all strategies allow."""
        strategies = [
            AllowAllProtocolFilter(),
            WhitelistProtocolFilter({"http", "sse", "websocket"})
        ]
        filter_strategy = CompositeProtocolFilter(strategies)
        self.assertTrue(filter_strategy.should_allow("http", self.protocol))
        self.assertTrue(filter_strategy.should_allow("sse", self.protocol))
        self.assertTrue(filter_strategy.should_allow("websocket", self.protocol))

    def test_composite_filter_one_denies(self):
        """Test the CompositeProtocolFilter when one strategy denies."""
        strategies = [
            AllowAllProtocolFilter(),
            BlacklistProtocolFilter({"websocket"})
        ]
        filter_strategy = CompositeProtocolFilter(strategies)
        self.assertTrue(filter_strategy.should_allow("http", self.protocol))
        self.assertTrue(filter_strategy.should_allow("sse", self.protocol))
        self.assertFalse(filter_strategy.should_allow("websocket", self.protocol))

    def test_create_filter_strategy(self):
        """Test creating filter strategies with the factory function."""
        # Test allow_all
        allow_all = create_protocol_filter_strategy("allow_all")
        self.assertIsInstance(allow_all, AllowAllProtocolFilter)
        
        # Test deny_all
        deny_all = create_protocol_filter_strategy("deny_all")
        self.assertIsInstance(deny_all, DenyAllProtocolFilter)
        
        # Test whitelist
        whitelist = create_protocol_filter_strategy("whitelist", allowed_protocols={"http"})
        self.assertIsInstance(whitelist, WhitelistProtocolFilter)
        self.assertTrue(whitelist.should_allow("http", self.protocol))
        self.assertFalse(whitelist.should_allow("sse", self.protocol))
        
        # Test blacklist
        blacklist = create_protocol_filter_strategy("blacklist", blocked_protocols={"websocket"})
        self.assertIsInstance(blacklist, BlacklistProtocolFilter)
        self.assertTrue(blacklist.should_allow("http", self.protocol))
        self.assertFalse(blacklist.should_allow("websocket", self.protocol))
        
        # Test composite
        strategies = [allow_all, blacklist]
        composite = create_protocol_filter_strategy("composite", strategies=strategies)
        self.assertIsInstance(composite, CompositeProtocolFilter)
        self.assertEqual(len(composite.strategies), 2)

    def test_create_invalid_strategy(self):
        """Test creating an invalid strategy type."""
        with self.assertRaises(ValueError):
            create_protocol_filter_strategy("invalid")


if __name__ == '__main__':
    unittest.main()