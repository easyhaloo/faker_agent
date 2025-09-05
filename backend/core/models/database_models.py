"""
SQLAlchemy database models for the Faker Agent.

This module defines the database models for conversations, messages, 
and memory storage using SQLAlchemy ORM.
"""
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON, Enum, Boolean, Integer
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator

from backend.core.infrastructure.database import Base
from backend.core.models.memory import MemoryType, MemoryScope


class UUID(TypeDecorator):
    """UUID type for SQLAlchemy"""
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """Convert UUID to string for storage"""
        if value is None:
            return None
        elif isinstance(value, uuid.UUID):
            return str(value)
        else:
            return str(uuid.UUID(value))

    def process_result_value(self, value, dialect):
        """Convert stored string to UUID"""
        if value is None:
            return None
        else:
            return uuid.UUID(value)


class ConversationDB(Base):
    """Database model for conversations."""
    __tablename__ = "conversations"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    extra_data = Column(SQLiteJSON, nullable=True)
    
    # Relationships
    messages = relationship("MessageDB", back_populates="conversation", cascade="all, delete-orphan")
    episode_memories = relationship("MemoryEpisodeDB", back_populates="conversation", cascade="all, delete-orphan")
    summaries = relationship("ConversationSummaryDB", back_populates="conversation", cascade="all, delete-orphan")


class MessageDB(Base):
    """Database model for messages."""
    __tablename__ = "messages"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    tool_calls = Column(SQLiteJSON, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    extra_data = Column(SQLiteJSON, nullable=True)

    # Relationships
    conversation = relationship("ConversationDB", back_populates="messages")


class MemoryProfileDB(Base):
    """Database model for memory profiles (global/project memory)."""
    __tablename__ = "memory_profiles"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=True)
    scope = Column(Enum(MemoryScope), nullable=False)
    project_id = Column(UUID, nullable=True)
    key = Column(String(255), nullable=False)
    value = Column(Text, nullable=False)
    memory_type = Column(Enum(MemoryType), nullable=False)
    tags = Column(SQLiteJSON, nullable=True)
    source_msg_id = Column(UUID, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime, nullable=True)
    extra_data = Column(SQLiteJSON, nullable=True)


class MemoryEpisodeDB(Base):
    """Database model for memory episodes (conversation-specific memory)."""
    __tablename__ = "memory_episodes"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID, ForeignKey("conversations.id"), nullable=False)
    memory_type = Column(Enum(MemoryType), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(SQLiteJSON, nullable=True)
    source_msg_id = Column(UUID, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime, nullable=True)
    extra_data = Column(SQLiteJSON, nullable=True)

    # Relationships
    conversation = relationship("ConversationDB", back_populates="episode_memories")


class ConversationSummaryDB(Base):
    """Database model for conversation summaries."""
    __tablename__ = "conversation_summaries"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID, ForeignKey("conversations.id"), nullable=False)
    content = Column(Text, nullable=False)
    range_start_msg_id = Column(UUID, nullable=False)
    range_end_msg_id = Column(UUID, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    extra_data = Column(SQLiteJSON, nullable=True)

    # Relationships
    conversation = relationship("ConversationDB", back_populates="summaries")


class MemoryAuditDB(Base):
    """Database model for memory audit logs."""
    __tablename__ = "memory_audit_logs"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    actor = Column(String(255), nullable=False)
    action = Column(String(50), nullable=False)
    target_id = Column(UUID, nullable=False)
    target_type = Column(String(50), nullable=False)
    details = Column(SQLiteJSON, nullable=True)
    created_at = Column(DateTime, default=datetime.now)


class MemorySettingsDB(Base):
    """Database model for memory settings."""
    __tablename__ = "memory_settings"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=True)
    use_global_memory = Column(Boolean, default=True)
    use_project_memory = Column(Boolean, default=True)
    project_id = Column(UUID, nullable=True)
    use_session_memory = Column(Boolean, default=True)
    enable_memory_writing = Column(Boolean, default=True)
    enable_rolling_summary = Column(Boolean, default=True)
    max_context_messages = Column(Integer, default=20)
    summary_token_threshold = Column(Integer, default=4000)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)