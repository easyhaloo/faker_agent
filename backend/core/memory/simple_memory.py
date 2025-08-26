"""
Simple in-memory storage for conversation history.
"""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# Configure logger
logger = logging.getLogger(__name__)


class Message(BaseModel):
    """A single message in a conversation."""
    
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class Conversation(BaseModel):
    """A conversation with messages."""
    
    id: str
    messages: List[Message] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SimpleMemory:
    """
    Simple in-memory storage for conversation history.
    """
    
    def __init__(self, max_conversations: int = 100):
        self.conversations: Dict[str, Conversation] = {}
        self.max_conversations = max_conversations
        logger.info(f"Initialized SimpleMemory with max_conversations={max_conversations}")
    
    async def add_message(self, conversation_id: str, role: str, content: str) -> None:
        """
        Add a message to a conversation.
        
        Args:
            conversation_id: The conversation ID
            role: The message role (user, assistant, system)
            content: The message content
        """
        # Create conversation if it doesn't exist
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = Conversation(id=conversation_id)
        
        # Add message
        message = Message(role=role, content=content)
        self.conversations[conversation_id].messages.append(message)
        logger.debug(f"Added message to conversation {conversation_id}")
        
        # Manage conversation limit
        if len(self.conversations) > self.max_conversations:
            self._cleanup_old_conversations()
    
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Get a conversation by ID.
        
        Args:
            conversation_id: The conversation ID
            
        Returns:
            The conversation or None if not found
        """
        return self.conversations.get(conversation_id)
    
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
        conversation = self.conversations.get(conversation_id)
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
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = Conversation(id=conversation_id)
        
        self.conversations[conversation_id].metadata[key] = value
    
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
        conversation = self.conversations.get(conversation_id)
        if not conversation:
            return default
        
        return conversation.metadata.get(key, default)
    
    def _cleanup_old_conversations(self) -> None:
        """Remove oldest conversations when limit is reached."""
        if len(self.conversations) <= self.max_conversations:
            return
        
        # Sort by last message timestamp
        sorted_convs = sorted(
            self.conversations.items(),
            key=lambda x: x[1].messages[-1].timestamp if x[1].messages else datetime.min
        )
        
        # Remove oldest
        num_to_remove = len(self.conversations) - self.max_conversations
        for i in range(num_to_remove):
            if i < len(sorted_convs):
                conv_id = sorted_convs[i][0]
                del self.conversations[conv_id]
                logger.debug(f"Removed old conversation {conv_id}")


# Create global memory instance
memory = SimpleMemory()