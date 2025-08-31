"""
Conversation models for the Faker Agent.

This module defines the data models for conversations and messages
to support a multi-session management system with context retention.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Message(BaseModel):
    """
    Message model representing a single message in a conversation.
    """
    id: UUID = Field(default_factory=uuid4)
    conversation_id: UUID
    role: str = Field(..., description="Message role: 'user', 'assistant', 'system', or 'tool'")
    content: str = Field(..., description="Message content")
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata for the message")
    
    class Config:
        orm_mode = True


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
        orm_mode = True


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
        orm_mode = True


class ConversationListResponse(BaseModel):
    """
    Response model for listing conversations.
    """
    conversations: List[ConversationResponse]
    total: int
    page: int
    page_size: int