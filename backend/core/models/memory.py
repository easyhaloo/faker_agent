"""
Memory models for the Faker Agent.

This module defines data models for different types of memory in the agent system:
- Short-term (working memory)
- Session-level episodic memory
- Global profile memory

These models support a sophisticated memory management system that allows the agent
to maintain context within and across sessions.
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MemoryType(str, Enum):
    """Enum for different types of memory entries."""
    FACT = "fact"           # Factual information
    GOAL = "goal"           # Goals or objectives
    CONSTRAINT = "constraint"  # Constraints or limitations
    PREFERENCE = "preference"  # User preferences
    TERM = "term"           # Terminology or definitions
    DECISION = "decision"   # Decisions made
    SUMMARY = "summary"     # Conversation summary


class MemoryScope(str, Enum):
    """Enum for memory scope levels."""
    GLOBAL = "global"       # Global (user-level) memory
    PROJECT = "project"     # Project-level memory
    SESSION = "session"     # Session/conversation-level memory


class MemoryProfile(BaseModel):
    """
    Model for storing user preferences and global/project-level memory.
    Used for long-term memory that persists across conversations.
    """
    id: UUID = Field(default_factory=uuid4)
    user_id: Optional[str] = None
    scope: MemoryScope
    project_id: Optional[UUID] = None
    key: str = Field(..., description="Memory key identifier")
    value: str = Field(..., description="Memory value content")
    memory_type: MemoryType
    tags: List[str] = Field(default_factory=list)
    source_msg_id: Optional[UUID] = None
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = Field(default=None)
    
    class Config:
        from_attributes = True


class MemoryEpisode(BaseModel):
    """
    Model for storing conversation-specific memories.
    Used for session-level episodic memory.
    """
    id: UUID = Field(default_factory=uuid4)
    conversation_id: UUID
    memory_type: MemoryType
    title: str = Field(..., description="Short descriptive title for the memory")
    content: str = Field(..., description="Full memory content")
    tags: List[str] = Field(default_factory=list)
    source_msg_id: Optional[UUID] = None
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = Field(default=None)
    
    class Config:
        from_attributes = True


class ConversationSummary(BaseModel):
    """
    Model for storing conversation summaries for long conversations.
    Used for rolling summaries to maintain context while reducing token usage.
    """
    id: UUID = Field(default_factory=uuid4)
    conversation_id: UUID
    content: str = Field(..., description="Summary content")
    range_start_msg_id: UUID = Field(..., description="First message ID in the summarized range")
    range_end_msg_id: UUID = Field(..., description="Last message ID in the summarized range")
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = Field(default=None)
    
    class Config:
        from_attributes = True


class MemoryAudit(BaseModel):
    """
    Model for auditing memory operations.
    Used for tracking changes to memory for compliance and debugging.
    """
    id: UUID = Field(default_factory=uuid4)
    actor: str = Field(..., description="Who performed the action (user or system)")
    action: str = Field(..., description="Action performed (create, read, update, delete)")
    target_id: UUID = Field(..., description="ID of the affected memory")
    target_type: str = Field(..., description="Type of memory affected (profile, episode, summary)")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional details about the action")
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        from_attributes = True


# Request/Response Models

class MemoryProfileCreate(BaseModel):
    """Model for creating a new profile memory."""
    scope: MemoryScope
    project_id: Optional[UUID] = None
    key: str
    value: str
    memory_type: MemoryType
    tags: List[str] = Field(default_factory=list)
    source_msg_id: Optional[UUID] = None
    expires_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class MemoryProfileUpdate(BaseModel):
    """Model for updating an existing profile memory."""
    key: Optional[str] = None
    value: Optional[str] = None
    memory_type: Optional[MemoryType] = None
    tags: Optional[List[str]] = None
    expires_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class MemoryEpisodeCreate(BaseModel):
    """Model for creating a new episode memory."""
    conversation_id: UUID
    memory_type: MemoryType
    title: str
    content: str
    tags: List[str] = Field(default_factory=list)
    source_msg_id: Optional[UUID] = None
    expires_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class MemoryEpisodeUpdate(BaseModel):
    """Model for updating an existing episode memory."""
    memory_type: Optional[MemoryType] = None
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    expires_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class MemoryResponse(BaseModel):
    """Generic response model for memory operations."""
    status: str
    message: str
    data: Optional[Any] = None


class MemorySettings(BaseModel):
    """Model for memory settings configuration."""
    use_global_memory: bool = True
    use_project_memory: bool = True
    project_id: Optional[UUID] = None
    use_session_memory: bool = True
    enable_memory_writing: bool = True
    enable_rolling_summary: bool = True
    max_context_messages: int = 20
    summary_token_threshold: int = 4000
    
    class Config:
        from_attributes = True