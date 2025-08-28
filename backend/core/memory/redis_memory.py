"""
Redis-based storage for conversation history.
"""
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import redis
from pydantic import BaseModel, Field

from backend.core.memory.simple_memory import Message, Conversation

# Configure logger
logger = logging.getLogger(__name__)


class RedisMemory:
    """
    Redis-based storage for conversation history.
    """
    
    def __init__(
        self, 
        host: str = "localhost", 
        port: int = 6379, 
        db: int = 0,
        password: Optional[str] = None,
        max_conversations: int = 100
    ):
        """
        Initialize Redis memory.
        
        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            password: Redis password (if required)
            max_conversations: Maximum number of conversations to keep
        """
        self.redis_client = redis.Redis(
            host=host, 
            port=port, 
            db=db, 
            password=password,
            decode_responses=True
        )
        self.max_conversations = max_conversations
        logger.info(f"Initialized RedisMemory with host={host}:{port}, db={db}")
    
    async def add_message(self, conversation_id: str, role: str, content: str) -> None:
        """
        Add a message to a conversation.
        
        Args:
            conversation_id: The conversation ID
            role: The message role (user, assistant, system)
            content: The message content
        """
        # Create conversation if it doesn't exist
        conv_key = f"conversation:{conversation_id}"
        conv_exists = self.redis_client.exists(conv_key)
        
        if not conv_exists:
            conversation = Conversation(id=conversation_id)
            self.redis_client.hset(conv_key, mapping={
                "id": conversation.id,
                "messages": json.dumps([]),
                "metadata": json.dumps(conversation.metadata),
                "created_at": datetime.now().isoformat()
            })
        
        # Add message
        message = Message(role=role, content=content)
        message_data = message.model_dump()
        
        # Get existing messages
        messages_json = self.redis_client.hget(conv_key, "messages")
        messages = json.loads(messages_json) if messages_json else []
        
        # Add new message
        messages.append(message_data)
        self.redis_client.hset(conv_key, "messages", json.dumps(messages))
        
        logger.debug(f"Added message to conversation {conversation_id}")
        
        # Update conversation timestamp
        self.redis_client.hset(conv_key, "updated_at", datetime.now().isoformat())
        
        # Manage conversation limit
        self._manage_conversation_limit()
    
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Get a conversation by ID.
        
        Args:
            conversation_id: The conversation ID
            
        Returns:
            The conversation or None if not found
        """
        conv_key = f"conversation:{conversation_id}"
        conv_data = self.redis_client.hgetall(conv_key)
        
        if not conv_data:
            return None
        
        try:
            messages_data = json.loads(conv_data.get("messages", "[]"))
            metadata = json.loads(conv_data.get("metadata", "{}"))
            
            messages = [
                Message(**msg_data) 
                for msg_data in messages_data
            ]
            
            conversation = Conversation(
                id=conv_data["id"],
                messages=messages,
                metadata=metadata
            )
            
            return conversation
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error parsing conversation data: {e}")
            return None
    
    async def get_messages(
        self, 
        conversation_id: str, 
        limit: Optional[int] = None
    ) -> List[Message]:
        """
        Get messages from a conversation.
        
        Args:
            conversation_id: The conversation ID
            limit: Optional limit on the number of most recent messages
            
        Returns:
            List of messages
        """
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            return []
        
        messages = conversation.messages
        if limit:
            messages = messages[-limit:]
        
        return messages
    
    async def set_metadata(self, conversation_id: str, key: str, value: Any) -> None:
        """
        Set metadata for a conversation.
        
        Args:
            conversation_id: The conversation ID
            key: Metadata key
            value: Metadata value
        """
        conv_key = f"conversation:{conversation_id}"
        conv_exists = self.redis_client.exists(conv_key)
        
        if not conv_exists:
            conversation = Conversation(id=conversation_id)
            self.redis_client.hset(conv_key, mapping={
                "id": conversation.id,
                "messages": json.dumps([]),
                "metadata": json.dumps(conversation.metadata),
                "created_at": datetime.now().isoformat()
            })
        
        # Update metadata
        metadata_json = self.redis_client.hget(conv_key, "metadata")
        metadata = json.loads(metadata_json) if metadata_json else {}
        metadata[key] = value
        self.redis_client.hset(conv_key, "metadata", json.dumps(metadata))
    
    async def get_metadata(
        self, 
        conversation_id: str, 
        key: str, 
        default: Any = None
    ) -> Any:
        """
        Get metadata for a conversation.
        
        Args:
            conversation_id: The conversation ID
            key: Metadata key
            default: Default value if key not found
            
        Returns:
            The metadata value or default
        """
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            return default
        
        return conversation.metadata.get(key, default)
    
    def _manage_conversation_limit(self) -> None:
        """Manage conversation limit by removing oldest conversations."""
        # Get all conversation keys
        conv_keys = self.redis_client.keys("conversation:*")
        
        if len(conv_keys) <= self.max_conversations:
            return
        
        # Get conversation timestamps
        conv_timestamps = []
        for key in conv_keys:
            updated_at = self.redis_client.hget(key, "updated_at")
            if updated_at:
                conv_timestamps.append((key, updated_at))
        
        # Sort by timestamp (oldest first)
        conv_timestamps.sort(key=lambda x: x[1])
        
        # Remove oldest conversations
        num_to_remove = len(conv_timestamps) - self.max_conversations
        for i in range(num_to_remove):
            if i < len(conv_timestamps):
                conv_key = conv_timestamps[i][0]
                self.redis_client.delete(conv_key)
                logger.debug(f"Removed old conversation {conv_key}")


# Create global memory instance
memory = RedisMemory()