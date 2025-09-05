"""
API routes for conversation management and agent integration.

This module provides endpoints for managing conversations and messages
with integrated agent processing.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import APIRouter, HTTPException

from backend.core.agent import conversation_agent
from backend.core.models.conversation import (
    Conversation, ConversationCreate, ConversationUpdate, 
    Message, MessageCreate, ConversationResponse, ConversationListResponse
)
from backend.core.utils.logging import get_logger

# Configure logger
logger = get_logger(__name__)

# Create router
router = APIRouter()


@router.post("/conversations", response_model=Dict[str, Any], status_code=201)
async def create_conversation(
    title: str = "New Conversation",
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a new conversation.
    """
    try:
        result = await conversation_agent.create_conversation(title, metadata)
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"]["message"])
        return result
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conversations/{conversation_id}/messages", response_model=Dict[str, Any], status_code=201)
async def process_message(
    conversation_id: UUID,
    message: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process a user message within a conversation context.
    
    This endpoint integrates:
    1. Conversation management (adding messages)
    2. Memory retrieval (context, profiles, summaries)
    3. LLM processing with context
    4. Result storage (conversation updates)
    """
    try:
        result = await conversation_agent.process_message(conversation_id, message, metadata)
        if result["status"] == "error":
            if result["error"]["code"] == "CONVERSATION_NOT_FOUND":
                raise HTTPException(status_code=404, detail=result["error"]["message"])
            raise HTTPException(status_code=500, detail=result["error"]["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations", response_model=Dict[str, Any])
async def list_conversations(
    page: int = 1,
    page_size: int = 20,
) -> Dict[str, Any]:
    """
    List conversations with pagination.
    """
    try:
        result = await conversation_agent.list_conversations(page, page_size)
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"]["message"])
        return result
    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}", response_model=Dict[str, Any])
async def get_conversation_history(
    conversation_id: UUID,
    limit: int = 50,
    offset: int = 0,
) -> Dict[str, Any]:
    """
    Get conversation history with messages.
    """
    try:
        result = await conversation_agent.get_conversation_history(conversation_id, limit, offset)
        if result["status"] == "error":
            if result["error"]["code"] == "CONVERSATION_NOT_FOUND":
                raise HTTPException(status_code=404, detail=result["error"]["message"])
            raise HTTPException(status_code=500, detail=result["error"]["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving conversation history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/conversations/{conversation_id}", response_model=Dict[str, Any])
async def update_conversation(
    conversation_id: UUID,
    title: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Update an existing conversation.
    """
    try:
        result = await conversation_agent.update_conversation(conversation_id, title, metadata)
        if result["status"] == "error":
            if result["error"]["code"] == "CONVERSATION_NOT_FOUND":
                raise HTTPException(status_code=404, detail=result["error"]["message"])
            raise HTTPException(status_code=500, detail=result["error"]["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversations/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: UUID,
) -> None:
    """
    Delete a conversation and all its messages.
    """
    try:
        result = await conversation_agent.delete_conversation(conversation_id)
        if result["status"] == "error":
            if result["error"]["code"] == "CONVERSATION_NOT_FOUND":
                raise HTTPException(status_code=404, detail=result["error"]["message"])
            raise HTTPException(status_code=500, detail=result["error"]["message"])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))