"""
Protocol-related contracts for the Faker Agent system.
"""
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class ProtocolType(str, Enum):
    """Supported protocol types."""
    
    HTTP = "http"
    SSE = "sse"
    WEBSOCKET = "websocket"


class ProtocolRequest(BaseModel):
    """Base model for protocol-specific requests."""
    
    protocol_type: ProtocolType = Field(
        ..., 
        description="Type of protocol to use for this request"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Protocol-specific metadata"
    )


class HTTPRequest(ProtocolRequest):
    """HTTP protocol specific request."""
    
    protocol_type: ProtocolType = ProtocolType.HTTP
    headers: Dict[str, str] = Field(
        default_factory=dict,
        description="HTTP headers"
    )


class SSERequest(ProtocolRequest):
    """SSE protocol specific request."""
    
    protocol_type: ProtocolType = ProtocolType.SSE
    headers: Dict[str, str] = Field(
        default_factory=dict,
        description="HTTP headers for SSE connection"
    )
    reconnect_time: Optional[int] = Field(
        None,
        description="Reconnection time in milliseconds"
    )


class WebSocketRequest(ProtocolRequest):
    """WebSocket protocol specific request."""
    
    protocol_type: ProtocolType = ProtocolType.WEBSOCKET
    headers: Dict[str, str] = Field(
        default_factory=dict,
        description="Headers for WebSocket handshake"
    )
    subprotocols: List[str] = Field(
        default_factory=list,
        description="WebSocket subprotocols"
    )


class ProtocolResponse(BaseModel):
    """Base model for protocol-specific responses."""
    
    protocol_type: ProtocolType = Field(
        ..., 
        description="Type of protocol used for this response"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Protocol-specific metadata"
    )


class HTTPResponse(ProtocolResponse):
    """HTTP protocol specific response."""
    
    protocol_type: ProtocolType = ProtocolType.HTTP
    status_code: int = Field(
        200,
        description="HTTP status code"
    )
    headers: Dict[str, str] = Field(
        default_factory=dict,
        description="HTTP response headers"
    )
    content: Dict[str, Any] = Field(
        default_factory=dict,
        description="Response content"
    )


class SSEResponse(ProtocolResponse):
    """SSE protocol specific response."""
    
    protocol_type: ProtocolType = ProtocolType.SSE
    headers: Dict[str, str] = Field(
        default_factory=dict,
        description="HTTP headers for SSE response"
    )
    retry: Optional[int] = Field(
        None,
        description="Reconnection time in milliseconds"
    )
    events: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="SSE events"
    )


class WebSocketResponse(ProtocolResponse):
    """WebSocket protocol specific response."""
    
    protocol_type: ProtocolType = ProtocolType.WEBSOCKET
    messages: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="WebSocket messages"
    )
    close_code: Optional[int] = Field(
        None,
        description="WebSocket close code if connection is closed"
    )
    close_reason: Optional[str] = Field(
        None,
        description="WebSocket close reason if connection is closed"
    )