"""
Conversation models for the Faker Agent.

This module defines the data models for conversations and messages
to support a multi-session management system with context retention.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator


class ToolCall(BaseModel):
    """Model representing a tool call made by the assistant."""
    id: str = Field(..., description="Tool call identifier")
    name: str = Field(..., description="Name of the tool being called")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Arguments passed to the tool")
    result: Optional[Any] = Field(None, description="Result of the tool call")
    error: Optional[str] = Field(None, description="Error message if the tool call failed")
    created_at: datetime = Field(default_factory=datetime.now)


class Message(BaseModel):
    """
    Message model representing a single message in a conversation.
    """
    id: UUID = Field(default_factory=uuid4)
    conversation_id: UUID
    role: str = Field(..., description="Message role: 'user', 'assistant', 'system', or 'tool'")
    content: str = Field(..., description="Message content")
    tool_calls: List[ToolCall] = Field(default_factory=list, description="Tool calls made in this message")
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata for the message")
    
    class Config:
        from_attributes = True
        
    @model_validator(mode='before')
    @classmethod
    def validate_from_orm(cls, data: Any) -> Any:
        """Validate and convert data from ORM model."""
        if hasattr(data, '__dict__'):
            # Handle tool_calls field - ensure it's always a list
            if hasattr(data, 'tool_calls'):
                if data.tool_calls is None:
                    data.tool_calls = []
                elif isinstance(data.tool_calls, str):
                    try:
                        import json
                        tool_calls_data = json.loads(data.tool_calls)
                        if isinstance(tool_calls_data, list):
                            data.tool_calls = tool_calls_data
                        else:
                            data.tool_calls = []
                    except:
                        data.tool_calls = []
                elif not isinstance(data.tool_calls, list):
                    data.tool_calls = []
            
            # Handle metadata/extra_data field - ensure it's always a dict or None
            if hasattr(data, 'extra_data'):
                if data.extra_data is None:
                    data.metadata = None
                elif isinstance(data.extra_data, str):
                    try:
                        import json
                        metadata_data = json.loads(data.extra_data)
                        if isinstance(metadata_data, dict):
                            data.metadata = metadata_data
                        else:
                            data.metadata = None
                    except:
                        data.metadata = None
                elif isinstance(data.extra_data, dict):
                    data.metadata = data.extra_data
                else:
                    data.metadata = None
            elif not hasattr(data, 'metadata'):
                data.metadata = None
                
        return data


class Conversation(BaseModel):
    """
    Conversation model representing a chat session.
    """
    id: UUID = Field(default_factory=uuid4)
    title: str = Field(..., description="Conversation title")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    messages: List[Message] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata for the conversation")
    
    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    """
    Model for creating a new conversation.
    """
    title: str = Field(default="New Conversation")
    metadata: Optional[Dict[str, Any]] = None


class ConversationUpdate(BaseModel):
    """
    Model for updating an existing conversation.
    """
    title: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class MessageCreate(BaseModel):
    """
    Model for creating a new message.
    """
    role: str
    content: str
    tool_calls: List[ToolCall] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None


class ConversationResponse(BaseModel):
    """
    Response model for conversation endpoints.
    """
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None
    messages: Optional[List[Message]] = None
    message_count: int = 0
    last_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    """
    Response model for listing conversations.
    """
    conversations: List[ConversationResponse]
    total: int
    page: int
    page_size: int