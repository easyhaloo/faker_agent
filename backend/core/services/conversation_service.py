"""
Conversation service for the Faker Agent.

This module provides a service for managing conversations and messages
with integrated memory management and context optimization.
"""
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from backend.core.infrastructure.database import db_session
from backend.core.models.conversation import (
    Conversation, 
    Message, 
    ConversationCreate, 
    ConversationUpdate,
    MessageCreate,
    ConversationResponse,
    ToolCall
)
from backend.core.models.database_models import ConversationDB, MessageDB
from backend.core.utils.logging import get_logger

# Configure logger
logger = get_logger(__name__)


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
        with db_session() as db:
            # Create database record
            db_conversation = ConversationDB(
                title=conversation_data.title,
                extra_data=conversation_data.metadata
            )
            db.add(db_conversation)
            db.commit()
            db.refresh(db_conversation)
            
            # Convert to Pydantic model
            conversation = Conversation(
                id=db_conversation.id,
                title=db_conversation.title,
                created_at=db_conversation.created_at,
                updated_at=db_conversation.updated_at,
                metadata=db_conversation.extra_data,
                messages=[]
            )
            
        logger.info(f"Created new conversation: {conversation.id} - {conversation.title}")
        return conversation
    
    @staticmethod
    async def get_conversation(conversation_id: UUID) -> Optional[ConversationResponse]:
        """
        Get a conversation by ID.
        
        Args:
            conversation_id: The ID of the conversation to retrieve
            
        Returns:
            The conversation if found, None otherwise
        """
        with db_session() as db:
            # Get conversation from database
            db_conversation = db.query(ConversationDB).filter(
                ConversationDB.id == conversation_id
            ).first()
            
            if not db_conversation:
                logger.warning(f"Conversation not found: {conversation_id}")
                return None
            
            # Get messages count
            message_count = db.query(MessageDB).filter(
                MessageDB.conversation_id == conversation_id
            ).count()
            
            # Get last message for preview
            last_message_db = db.query(MessageDB).filter(
                MessageDB.conversation_id == conversation_id
            ).order_by(MessageDB.created_at.desc()).first()
            
            last_message = None
            if last_message_db:
                last_message = (
                    last_message_db.content[:50] + "..." 
                    if len(last_message_db.content) > 50 
                    else last_message_db.content
                )
            
            # Create response object
            conversation_response = ConversationResponse(
                id=db_conversation.id,
                title=db_conversation.title,
                created_at=db_conversation.created_at,
                updated_at=db_conversation.updated_at,
                metadata=db_conversation.extra_data,
                message_count=message_count,
                last_message=last_message
            )
            
            return conversation_response
    
    @staticmethod
    async def list_conversations(
        page: int = 1, 
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        List all conversations with pagination.
        
        Args:
            page: Page number (1-based)
            page_size: Number of conversations per page
            
        Returns:
            Dictionary with conversations and pagination info
        """
        with db_session() as db:
            # Calculate offset
            offset = (page - 1) * page_size
            
            # Get total count
            total = db.query(ConversationDB).count()
            
            # Get conversations with pagination
            db_conversations = db.query(ConversationDB).order_by(
                ConversationDB.updated_at.desc()
            ).offset(offset).limit(page_size).all()
            
            # Create response objects
            conversation_responses = []
            
            for db_conversation in db_conversations:
                # Get messages count
                message_count = db.query(MessageDB).filter(
                    MessageDB.conversation_id == db_conversation.id
                ).count()
                
                # Get last message for preview
                last_message_db = db.query(MessageDB).filter(
                    MessageDB.conversation_id == db_conversation.id
                ).order_by(MessageDB.created_at.desc()).first()
                
                last_message = None
                if last_message_db:
                    last_message = (
                        last_message_db.content[:50] + "..." 
                        if len(last_message_db.content) > 50 
                        else last_message_db.content
                    )
                
                conversation_response = ConversationResponse(
                    id=db_conversation.id,
                    title=db_conversation.title,
                    created_at=db_conversation.created_at,
                    updated_at=db_conversation.updated_at,
                    metadata=db_conversation.extra_data,
                    message_count=message_count,
                    last_message=last_message
                )
                
                conversation_responses.append(conversation_response)
            
            return {
                "conversations": conversation_responses,
                "total": total,
                "page": page,
                "page_size": page_size
            }
    
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
        with db_session() as db:
            # Get conversation from database
            db_conversation = db.query(ConversationDB).filter(
                ConversationDB.id == conversation_id
            ).first()
            
            if not db_conversation:
                logger.warning(f"Cannot update: Conversation not found: {conversation_id}")
                return None
            
            # Update fields if provided
            if conversation_data.title is not None:
                db_conversation.title = conversation_data.title
                
            if conversation_data.metadata is not None:
                db_conversation.extra_data = conversation_data.metadata
            
            # Update the timestamp
            db_conversation.updated_at = datetime.now()
            
            db.commit()
            db.refresh(db_conversation)
            
            # Convert to Pydantic model
            conversation = Conversation(
                id=db_conversation.id,
                title=db_conversation.title,
                created_at=db_conversation.created_at,
                updated_at=db_conversation.updated_at,
                metadata=db_conversation.extra_data,
                messages=[]
            )
            
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
        with db_session() as db:
            # Get conversation from database
            db_conversation = db.query(ConversationDB).filter(
                ConversationDB.id == conversation_id
            ).first()
            
            if not db_conversation:
                logger.warning(f"Cannot delete: Conversation not found: {conversation_id}")
                return False
            
            # Delete the conversation (cascade will delete messages)
            db.delete(db_conversation)
            db.commit()
            
            logger.info(f"Deleted conversation {conversation_id}")
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
        with db_session() as db:
            # Check if conversation exists
            db_conversation = db.query(ConversationDB).filter(
                ConversationDB.id == conversation_id
            ).first()
            
            if not db_conversation:
                logger.warning(f"Cannot add message: Conversation not found: {conversation_id}")
                return None
            
            # Convert tool calls to dict format for storage
            tool_calls_dict = []
            for tool_call in message_data.tool_calls:
                tool_calls_dict.append({
                    "id": tool_call.id,
                    "name": tool_call.name,
                    "arguments": tool_call.arguments,
                    "result": tool_call.result,
                    "error": tool_call.error,
                    "created_at": tool_call.created_at.isoformat() if tool_call.created_at else None
                })
            
            # Create database record
            db_message = MessageDB(
                conversation_id=conversation_id,
                role=message_data.role,
                content=message_data.content,
                tool_calls=tool_calls_dict if tool_calls_dict else None,
                extra_data=message_data.metadata
            )
            db.add(db_message)
            db.commit()
            db.refresh(db_message)
            
            # Convert tool calls back to model format
            tool_calls = []
            if db_message.tool_calls:
                for tool_call_dict in db_message.tool_calls:
                    tool_calls.append(ToolCall(
                        id=tool_call_dict["id"],
                        name=tool_call_dict["name"],
                        arguments=tool_call_dict["arguments"],
                        result=tool_call_dict["result"],
                        error=tool_call_dict["error"],
                        created_at=datetime.fromisoformat(tool_call_dict["created_at"]) if tool_call_dict["created_at"] else datetime.now()
                    ))
            
            # Convert to Pydantic model
            message = Message(
                id=db_message.id,
                conversation_id=db_message.conversation_id,
                role=db_message.role,
                content=db_message.content,
                tool_calls=tool_calls,
                created_at=db_message.created_at,
                metadata=db_message.extra_data
            )
            
            # Update conversation's updated_at timestamp
            db_conversation.updated_at = datetime.now()
            
            # Update conversation title for the first user message if it's a generic title
            if (
                message_data.role == "user" and 
                (db_conversation.title == "New Conversation" or not db_conversation.title)
            ):
                # Check if this is the first user message
                user_message_count = db.query(MessageDB).filter(
                    MessageDB.conversation_id == conversation_id,
                    MessageDB.role == "user"
                ).count()
                
                if user_message_count <= 1:  # This is the first or only user message
                    # Use the first few words of the user's message as the title
                    title_text = message_data.content[:30].strip()
                    if len(title_text) < 10:  # If message is too short, use a date-based title
                        title_text = f"Conversation - {datetime.now().strftime('%Y-%m-%d')}"
                    
                    db_conversation.title = title_text
                    logger.info(f"Updated conversation title to: {title_text}")
            
            db.commit()
            
            logger.info(f"Added {message_data.role} message to conversation {conversation_id}")
            return message
    
    @staticmethod
    async def get_messages(
        conversation_id: UUID, 
        limit: int = 50,
        offset: int = 0
    ) -> List[Message]:
        """
        Get messages for a conversation with pagination.
        
        Args:
            conversation_id: The ID of the conversation
            limit: Maximum number of messages to return
            offset: Number of messages to skip
            
        Returns:
            List of messages
        """
        with db_session() as db:
            # Check if conversation exists
            db_conversation = db.query(ConversationDB).filter(
                ConversationDB.id == conversation_id
            ).first()
            
            if not db_conversation:
                logger.warning(f"Cannot get messages: Conversation not found: {conversation_id}")
                return []
            
            # Get messages with pagination
            db_messages = db.query(MessageDB).filter(
                MessageDB.conversation_id == conversation_id
            ).order_by(MessageDB.created_at.asc()).offset(offset).limit(limit).all()
            
            # Convert to Pydantic models
            messages = []
            for db_message in db_messages:
                # Convert tool calls back to model format
                tool_calls = []
                if db_message.tool_calls:
                    for tool_call_dict in db_message.tool_calls:
                        tool_calls.append(ToolCall(
                            id=tool_call_dict["id"],
                            name=tool_call_dict["name"],
                            arguments=tool_call_dict["arguments"],
                            result=tool_call_dict["result"],
                            error=tool_call_dict["error"],
                            created_at=datetime.fromisoformat(tool_call_dict["created_at"]) if tool_call_dict["created_at"] else datetime.now()
                        ))
                
                message = Message(
                    id=db_message.id,
                    conversation_id=db_message.conversation_id,
                    role=db_message.role,
                    content=db_message.content,
                    tool_calls=tool_calls,
                    created_at=db_message.created_at,
                    metadata=db_message.extra_data
                )
                messages.append(message)
            
            return messages


# Singleton instance
conversation_service = ConversationService()