"""
Event types for the LangGraph orchestrator.
"""
from enum import Enum
from typing import Any, Dict, List, Optional, Union
import time

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Event types for the LangGraph orchestrator."""
    
    TOOL_CALL_START = "tool_call_start"
    TOOL_CALL_RESULT = "tool_call_result"
    TOKEN = "token"
    FINAL = "final"
    ERROR = "error"


class BaseEvent(BaseModel):
    """Base event model."""
    
    type: EventType
    timestamp: float = Field(default_factory=time.time)


class ToolCallStartEvent(BaseEvent):
    """Event for when a tool call starts."""
    
    type: EventType = EventType.TOOL_CALL_START
    tool_name: str
    tool_args: Dict[str, Any]
    tool_call_id: str


class ToolCallResultEvent(BaseEvent):
    """Event for when a tool call completes."""
    
    type: EventType = EventType.TOOL_CALL_RESULT
    tool_name: str
    tool_call_id: str
    result: Any
    error: Optional[str] = None


class TokenEvent(BaseEvent):
    """Event for when a token is generated."""
    
    type: EventType = EventType.TOKEN
    token: str
    is_partial: bool = False


class FinalEvent(BaseEvent):
    """Event for when the flow completes."""
    
    type: EventType = EventType.FINAL
    response: str
    actions: List[Dict[str, Any]] = []


class ErrorEvent(BaseEvent):
    """Event for when an error occurs."""
    
    type: EventType = EventType.ERROR
    error: str
    stack_trace: Optional[str] = None


Event = Union[
    ToolCallStartEvent,
    ToolCallResultEvent,
    TokenEvent,
    FinalEvent,
    ErrorEvent
]