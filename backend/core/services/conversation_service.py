"""
Conversation service for the Faker Agent.

This module provides a service for managing conversations and messages,
supporting the multi-session management system.
"""
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from uuid import UUID, uuid4

from backend.core.models.conversation import (
    Conversation, 
    Message, 
    ConversationCreate, 
    ConversationUpdate,
    MessageCreate,
    ConversationResponse
)
from backend.core.utils.logging import get_logger

# Configure logger
logger = get_logger(__name__)

# In-memory storage for development/testing
# In a production environment, this would be replaced with a database
conversations_db: Dict[UUID, Conversation] = {}
messages_db: Dict[UUID, Message] = {}


class ConversationService:
    """Service for managing conversations and messages."""
    
    @staticmethod
    async def create_conversation(conversation_data: ConversationCreate) -> Conversation:
        """
        Create a new conversation.
        
        Args:
            conversation_data: Data for creating the conversation
            
        Returns:
            The created conversation
        """
        conversation_id = uuid4()
        new_conversation = Conversation(
            id=conversation_id,
            title=conversation_data.title,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata=conversation_data.metadata or {},
            messages=[]
        )
        
        conversations_db[conversation_id] = new_conversation
        logger.info(f"Created new conversation: {conversation_id} - {new_conversation.title}")
        
        return new_conversation
    
    @staticmethod
    async def get_conversation(conversation_id: UUID) -> Optional[Conversation]:
        """
        Get a conversation by ID.
        
        Args:
            conversation_id: The ID of the conversation to retrieve
            
        Returns:
            The conversation if found, None otherwise
        """
        conversation = conversations_db.get(conversation_id)
        if not conversation:
            logger.warning(f"Conversation not found: {conversation_id}")
            return None
            
        # Fetch all messages for this conversation
        conversation_messages = [
            message for message in messages_db.values()
            if message.conversation_id == conversation_id
        ]
        
        # Sort messages by creation time
        conversation_messages.sort(key=lambda m: m.created_at)
        
        # Update the conversation with its messages
        conversation.messages = conversation_messages
        
        return conversation
    
    @staticmethod
    async def list_conversations(
        skip: int = 0, 
        limit: int = 10
    ) -> List[ConversationResponse]:
        """
        List all conversations with pagination.
        
        Args:
            skip: Number of conversations to skip
            limit: Maximum number of conversations to return
            
        Returns:
            List of conversations
        """
        all_conversations = list(conversations_db.values())
        
        # Sort by updated_at (most recent first)
        all_conversations.sort(key=lambda c: c.updated_at, reverse=True)
        
        # Apply pagination
        paginated_conversations = all_conversations[skip:skip + limit]
        
        # Create response objects
        conversation_responses = []
        
        for conversation in paginated_conversations:
            # Get messages for this conversation
            conversation_messages = [
                message for message in messages_db.values()
                if message.conversation_id == conversation.id
            ]
            
            # Sort messages by creation time
            conversation_messages.sort(key=lambda m: m.created_at)
            
            # Create response with message count and last message preview
            last_message = None
            if conversation_messages:
                last_message_obj = conversation_messages[-1]
                last_message = last_message_obj.content[:50] + "..." if len(last_message_obj.content) > 50 else last_message_obj.content
            
            conversation_response = ConversationResponse(
                id=conversation.id,
                title=conversation.title,
                created_at=conversation.created_at,
                updated_at=conversation.updated_at,
                metadata=conversation.metadata,
                message_count=len(conversation_messages),
                last_message=last_message
            )
            
            conversation_responses.append(conversation_response)
        
        return conversation_responses
    
    @staticmethod
    async def update_conversation(
        conversation_id: UUID, 
        conversation_data: ConversationUpdate
    ) -> Optional[Conversation]:
        """
        Update an existing conversation.
        
        Args:
            conversation_id: The ID of the conversation to update
            conversation_data: The data to update
            
        Returns:
            The updated conversation if found, None otherwise
        """
        conversation = conversations_db.get(conversation_id)
        if not conversation:
            logger.warning(f"Cannot update: Conversation not found: {conversation_id}")
            return None
        
        # Update fields if provided
        if conversation_data.title is not None:
            conversation.title = conversation_data.title
            
        if conversation_data.metadata is not None:
            conversation.metadata = conversation_data.metadata
        
        # Update the timestamp
        conversation.updated_at = datetime.now()
        
        # Save the updated conversation
        conversations_db[conversation_id] = conversation
        logger.info(f"Updated conversation: {conversation_id}")
        
        return conversation
    
    @staticmethod
    async def delete_conversation(conversation_id: UUID) -> bool:
        """
        Delete a conversation and all its messages.
        
        Args:
            conversation_id: The ID of the conversation to delete
            
        Returns:
            True if deleted, False if not found
        """
        if conversation_id not in conversations_db:
            logger.warning(f"Cannot delete: Conversation not found: {conversation_id}")
            return False
        
        # Delete the conversation
        del conversations_db[conversation_id]
        
        # Delete all messages for this conversation
        message_ids_to_delete = [
            message_id for message_id, message in messages_db.items()
            if message.conversation_id == conversation_id
        ]
        
        for message_id in message_ids_to_delete:
            del messages_db[message_id]
        
        logger.info(f"Deleted conversation {conversation_id} and {len(message_ids_to_delete)} messages")
        
        return True
    
    @staticmethod
    async def add_message(
        conversation_id: UUID, 
        message_data: MessageCreate
    ) -> Optional[Message]:
        """
        Add a message to a conversation.
        
        Args:
            conversation_id: The ID of the conversation
            message_data: The message data
            
        Returns:
            The created message if successful, None if conversation not found
        """
        # Check if conversation exists
        if conversation_id not in conversations_db:
            logger.warning(f"Cannot add message: Conversation not found: {conversation_id}")
            return None
        
        # Create new message
        message_id = uuid4()
        new_message = Message(
            id=message_id,
            conversation_id=conversation_id,
            role=message_data.role,
            content=message_data.content,
            created_at=datetime.now(),
            metadata=message_data.metadata or {}
        )
        
        # Save the message
        messages_db[message_id] = new_message
        
        # Update conversation's updated_at timestamp
        conversation = conversations_db[conversation_id]
        conversation.updated_at = datetime.now()
        
        # Update conversation title for the first user message if it's a generic title
        if (
            message_data.role == "user" and 
            (conversation.title == "New Conversation" or not conversation.title) and
            not any(msg.role == "user" for msg in messages_db.values() if msg.conversation_id == conversation_id)
        ):
            # Use the first few words of the user's message as the title
            title_text = message_data.content[:30].strip()
            if len(title_text) < 10:  # If message is too short, use a date-based title
                title_text = f"Conversation - {datetime.now().strftime('%Y-%m-%d')}"
            
            conversation.title = title_text
            logger.info(f"Updated conversation title to: {title_text}")
        
        # Save the updated conversation
        conversations_db[conversation_id] = conversation
        
        logger.info(f"Added {message_data.role} message to conversation {conversation_id}")
        
        return new_message
    
    @staticmethod
    async def get_messages(
        conversation_id: UUID, 
        skip: int = 0, 
        limit: int = 50
    ) -> List[Message]:
        """
        Get messages for a conversation with pagination.
        
        Args:
            conversation_id: The ID of the conversation
            skip: Number of messages to skip
            limit: Maximum number of messages to return
            
        Returns:
            List of messages
        """
        # Get all messages for this conversation
        conversation_messages = [
            message for message in messages_db.values()
            if message.conversation_id == conversation_id
        ]
        
        # Sort by creation time
        conversation_messages.sort(key=lambda m: m.created_at)
        
        # Apply pagination
        paginated_messages = conversation_messages[skip:skip + limit]
        
        return paginated_messages