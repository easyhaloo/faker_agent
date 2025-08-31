"""
API routes for conversation management.

This module provides the API endpoints for creating, retrieving, updating,
and deleting conversations, as well as adding messages to conversations.
"""
import uuid
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Path, Body, Depends

from backend.core.models.conversation import (
    ConversationCreate,
    ConversationUpdate,
    MessageCreate,
    ConversationResponse,
    ConversationListResponse
)
from backend.core.services.conversation_service import ConversationService
from backend.core.utils.logging import get_logger

# Configure logger
logger = get_logger(__name__)

# Create router
router = APIRouter()


@router.post("", response_model=ConversationResponse)
async def create_conversation(
    conversation_data: ConversationCreate = Body(...)
):
    """
    Create a new conversation.
    
    Args:
        conversation_data: Data for creating the conversation
        
    Returns:
        The created conversation
    """
    try:
        logger.info(f"Creating new conversation with title: {conversation_data.title}")
        conversation = await ConversationService.create_conversation(conversation_data)
        
        # Build response
        return ConversationResponse(
            id=conversation.id,
            title=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            metadata=conversation.metadata,
            message_count=0
        )
    except Exception as e:
        logger.error(f"Error creating conversation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create conversation: {str(e)}")


@router.get("", response_model=ConversationListResponse)
async def list_conversations(
    skip: int = Query(0, ge=0, description="Number of conversations to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of conversations to return")
):
    """
    List all conversations with pagination.
    
    Args:
        skip: Number of conversations to skip
        limit: Maximum number of conversations to return
        
    Returns:
        List of conversations
    """
    try:
        logger.info(f"Listing conversations with skip={skip}, limit={limit}")
        conversations = await ConversationService.list_conversations(skip, limit)
        
        # Determine total count (in a real implementation, this would be a database count)
        # For the in-memory implementation, we're just getting the length of all conversations
        from backend.core.services.conversation_service import conversations_db
        total = len(conversations_db)
        
        return ConversationListResponse(
            conversations=conversations,
            total=total,
            page=skip // limit + 1 if limit > 0 else 1,
            page_size=limit
        )
    except Exception as e:
        logger.error(f"Error listing conversations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list conversations: {str(e)}")


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: uuid.UUID = Path(..., description="The ID of the conversation to retrieve")
):
    """
    Get a conversation by ID.
    
    Args:
        conversation_id: The ID of the conversation to retrieve
        
    Returns:
        The conversation if found
    """
    try:
        logger.info(f"Getting conversation: {conversation_id}")
        conversation = await ConversationService.get_conversation(conversation_id)
        
        if not conversation:
            raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")
        
        # Build response
        return ConversationResponse(
            id=conversation.id,
            title=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            metadata=conversation.metadata,
            messages=conversation.messages,
            message_count=len(conversation.messages),
            last_message=conversation.messages[-1].content[:50] + "..." if conversation.messages else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation {conversation_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get conversation: {str(e)}")


@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: uuid.UUID = Path(..., description="The ID of the conversation to update"),
    conversation_data: ConversationUpdate = Body(...)
):
    """
    Update an existing conversation.
    
    Args:
        conversation_id: The ID of the conversation to update
        conversation_data: The data to update
        
    Returns:
        The updated conversation
    """
    try:
        logger.info(f"Updating conversation: {conversation_id}")
        conversation = await ConversationService.update_conversation(conversation_id, conversation_data)
        
        if not conversation:
            raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")
        
        # Get messages for this conversation to build the response
        messages = await ConversationService.get_messages(conversation_id)
        
        # Build response
        return ConversationResponse(
            id=conversation.id,
            title=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            metadata=conversation.metadata,
            message_count=len(messages),
            last_message=messages[-1].content[:50] + "..." if messages else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating conversation {conversation_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update conversation: {str(e)}")


@router.delete("/{conversation_id}", response_model=dict)
async def delete_conversation(
    conversation_id: uuid.UUID = Path(..., description="The ID of the conversation to delete")
):
    """
    Delete a conversation and all its messages.
    
    Args:
        conversation_id: The ID of the conversation to delete
        
    Returns:
        Success message
    """
    try:
        logger.info(f"Deleting conversation: {conversation_id}")
        deleted = await ConversationService.delete_conversation(conversation_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")
        
        return {"status": "success", "message": f"Conversation {conversation_id} deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation {conversation_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to delete conversation: {str(e)}")


@router.post("/{conversation_id}/messages", response_model=dict)
async def add_message(
    conversation_id: uuid.UUID = Path(..., description="The ID of the conversation"),
    message_data: MessageCreate = Body(...)
):
    """
    Add a message to a conversation.
    
    Args:
        conversation_id: The ID of the conversation
        message_data: The message data
        
    Returns:
        Success message and message ID
    """
    try:
        logger.info(f"Adding {message_data.role} message to conversation: {conversation_id}")
        message = await ConversationService.add_message(conversation_id, message_data)
        
        if not message:
            raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")
        
        # Process user messages and get AI responses
        if message_data.role == "user":
            # In a complete implementation, we would call the agent service here
            # to get an AI response, but for now we'll just add a placeholder
            # response to demonstrate the conversation flow
            
            # Create a placeholder AI response
            response_content = "This is a placeholder response. In a complete implementation, this would be a response from the agent."
            
            # Add the AI response to the conversation
            ai_message_data = MessageCreate(
                role="assistant",
                content=response_content
            )
            
            ai_message = await ConversationService.add_message(conversation_id, ai_message_data)
            
            return {
                "status": "success", 
                "message": "Message added and response generated",
                "message_id": str(message.id),
                "response_id": str(ai_message.id)
            }
        
        return {"status": "success", "message": "Message added", "message_id": str(message.id)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding message to conversation {conversation_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to add message: {str(e)}")


@router.put("/{conversation_id}/title", response_model=ConversationResponse)
async def update_conversation_title(
    conversation_id: uuid.UUID = Path(..., description="The ID of the conversation to update"),
    title_data: dict = Body(..., example={"title": "New Title"})
):
    """
    Update the title of a conversation.
    
    Args:
        conversation_id: The ID of the conversation to update
        title_data: The new title
        
    Returns:
        The updated conversation
    """
    try:
        title = title_data.get("title")
        if not title:
            raise HTTPException(status_code=400, detail="Title is required")
            
        logger.info(f"Updating title of conversation {conversation_id} to: {title}")
        
        # Create update data
        conversation_data = ConversationUpdate(title=title)
        
        # Update conversation
        conversation = await ConversationService.update_conversation(conversation_id, conversation_data)
        
        if not conversation:
            raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")
        
        # Get messages for this conversation to build the response
        messages = await ConversationService.get_messages(conversation_id)
        
        # Build response
        return ConversationResponse(
            id=conversation.id,
            title=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            metadata=conversation.metadata,
            message_count=len(messages),
            last_message=messages[-1].content[:50] + "..." if messages else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating conversation title {conversation_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update conversation title: {str(e)}")