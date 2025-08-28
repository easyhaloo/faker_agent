"""
Test for Redis memory implementation.
"""
import asyncio
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.core.memory.redis_memory import RedisMemory


async def test_redis_memory():
    """Test Redis memory functionality."""
    # Initialize Redis memory
    memory = RedisMemory(host="localhost", port=6379, db=0)
    
    # Test conversation ID
    conv_id = "test_conv_123"
    
    # Test adding messages
    print("Adding messages...")
    await memory.add_message(conv_id, "user", "Hello, world!")
    await memory.add_message(conv_id, "assistant", "Hi there! How can I help you?")
    
    # Test getting messages
    print("Getting messages...")
    messages = await memory.get_messages(conv_id)
    for msg in messages:
        print(f"{msg.role}: {msg.content}")
    
    # Test metadata
    print("Setting metadata...")
    await memory.set_metadata(conv_id, "user_id", "user_456")
    await memory.set_metadata(conv_id, "session_id", "session_789")
    
    print("Getting metadata...")
    user_id = await memory.get_metadata(conv_id, "user_id")
    session_id = await memory.get_metadata(conv_id, "session_id")
    print(f"User ID: {user_id}")
    print(f"Session ID: {session_id}")
    
    # Test getting conversation
    print("Getting conversation...")
    conversation = await memory.get_conversation(conv_id)
    if conversation:
        print(f"Conversation ID: {conversation.id}")
        print(f"Messages count: {len(conversation.messages)}")
        print(f"Metadata: {conversation.metadata}")
    
    print("Test completed!")


if __name__ == "__main__":
    asyncio.run(test_redis_memory())