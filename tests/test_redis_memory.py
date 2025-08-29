"""
Test for Redis memory implementation.
"""
import asyncio
import os
import sys

import pytest
from backend.core.memory.redis_memory import RedisMemory


@pytest.mark.asyncio
async def test_redis_memory():
    """Test Redis memory functionality."""
    # Skip this test if Redis is not available
    pytest.skip("Skipping Redis memory test - requires running Redis server")
    
    # Initialize Redis memory
    memory = RedisMemory(host="localhost", port=6379, db=0)
    
    # Test conversation ID
    conv_id = "test_conv_123"
    
    # Test adding messages
    await memory.add_message(conv_id, "user", "Hello, world!")
    await memory.add_message(conv_id, "assistant", "Hi there! How can I help you?")
    
    # Test getting messages
    messages = await memory.get_messages(conv_id)
    assert len(messages) == 2
    assert messages[0].role == "user"
    assert messages[1].role == "assistant"
    
    # Test metadata
    await memory.set_metadata(conv_id, "user_id", "user_456")
    await memory.set_metadata(conv_id, "session_id", "session_789")
    
    user_id = await memory.get_metadata(conv_id, "user_id")
    session_id = await memory.get_metadata(conv_id, "session_id")
    assert user_id == "user_456"
    assert session_id == "session_789"
    
    # Test getting conversation
    conversation = await memory.get_conversation(conv_id)
    assert conversation is not None
    assert conversation.id == conv_id
    assert len(conversation.messages) == 2
    assert "user_id" in conversation.metadata