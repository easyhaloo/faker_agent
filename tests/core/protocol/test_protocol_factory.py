"""
Tests for the protocol factory.
"""
import pytest

from backend.core.protocol.http_protocol import HTTPProtocol
from backend.core.protocol.protocol_factory import (
    ProtocolFactory,
    ProtocolType,
    protocol_factory
)
from backend.core.protocol.sse_protocol import SSEProtocol
from backend.core.protocol.websocket_protocol import WebSocketProtocol


def test_protocol_factory_initialization():
    """Test that the protocol factory is initialized correctly."""
    # Create a new protocol factory
    factory = ProtocolFactory()
    
    # Check that it has the expected protocols
    assert isinstance(factory.get_protocol(ProtocolType.HTTP), HTTPProtocol)
    assert isinstance(factory.get_protocol(ProtocolType.SSE), SSEProtocol)
    assert isinstance(factory.get_protocol(ProtocolType.WEBSOCKET), WebSocketProtocol)


def test_global_protocol_factory():
    """Test the global protocol factory instance."""
    # Check that the global instance has the expected protocols
    assert isinstance(protocol_factory.get_protocol(ProtocolType.HTTP), HTTPProtocol)
    assert isinstance(protocol_factory.get_protocol(ProtocolType.SSE), SSEProtocol)
    assert isinstance(protocol_factory.get_protocol(ProtocolType.WEBSOCKET), WebSocketProtocol)


def test_get_protocol_case_insensitive():
    """Test that protocol names are case-insensitive."""
    # Check with different case
    assert isinstance(protocol_factory.get_protocol("http"), HTTPProtocol)
    assert isinstance(protocol_factory.get_protocol("HTTP"), HTTPProtocol)
    assert isinstance(protocol_factory.get_protocol("Http"), HTTPProtocol)


def test_get_protocol_unknown():
    """Test that unknown protocol names return None."""
    # Check with unknown protocol
    assert protocol_factory.get_protocol("unknown") is None


def test_register_protocol():
    """Test registering a custom protocol."""
    # Create a new protocol factory
    factory = ProtocolFactory()
    
    # Create a mock protocol
    class MockProtocol(HTTPProtocol):
        pass
    
    # Register the mock protocol
    factory.register_protocol("http", MockProtocol())
    
    # Check that the protocol was registered
    assert isinstance(factory.get_protocol("http"), MockProtocol)