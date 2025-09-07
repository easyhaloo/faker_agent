"""
API routes for conversation management and agent integration.

This module provides endpoints for managing conversations and messages
with integrated agent processing.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
import json
from datetime import datetime

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel

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


class MessageRequest(BaseModel):
    """Request model for processing a message."""
    message: str
    metadata: Optional[Dict[str, Any]] = None


class MessageResponse(BaseModel):
    """Response model for message processing."""
    status: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


@router.post("/", response_model=Dict[str, Any], status_code=201)
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


@router.post("/{conversation_id}/messages", response_model=MessageResponse, status_code=201)
async def process_message(
    conversation_id: UUID,
    request: MessageRequest
) -> MessageResponse:
    """
    Process a user message within a conversation context.
    
    This endpoint integrates:
    1. Conversation management (adding messages)
    2. Memory retrieval (context, profiles, summaries)
    3. LLM processing with context
    4. Result storage (conversation updates)
    """
    try:
        result = await conversation_agent.process_message(conversation_id, request.message, request.metadata)
        if result["status"] == "error":
            if result["error"]["code"] == "CONVERSATION_NOT_FOUND":
                raise HTTPException(status_code=404, detail=result["error"]["message"])
            raise HTTPException(status_code=500, detail=result["error"]["message"])
        return MessageResponse(status="success", data=result["data"])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=Dict[str, Any])
async def list_conversations(
    skip: int = 0,
    limit: int = 10,
) -> Dict[str, Any]:
    """
    List conversations with pagination.
    """
    try:
        # Convert skip/limit to page/page_size
        page = (skip // limit) + 1 if limit > 0 else 1
        page_size = limit
        result = await conversation_agent.list_conversations(page, page_size)
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"]["message"])
        return result
    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{conversation_id}", response_model=Dict[str, Any])
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


@router.put("/{conversation_id}", response_model=Dict[str, Any])
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


@router.delete("/{conversation_id}", status_code=204)
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


@router.get("/{conversation_id}/export", response_model=Dict[str, Any])
async def export_conversation(
    conversation_id: UUID,
    format: str = "json"
) -> Dict[str, Any]:
    """
    Export a conversation in various formats (JSON, TXT, etc.).
    
    Args:
        conversation_id: The conversation ID to export
        format: Export format (json, txt, md)
    
    Returns:
        Dictionary containing the exported data and metadata
    """
    try:
        # Get conversation history
        result = await conversation_agent.get_conversation_history(conversation_id)
        if result["status"] == "error":
            if result["error"]["code"] == "CONVERSATION_NOT_FOUND":
                raise HTTPException(status_code=404, detail=result["error"]["message"])
            raise HTTPException(status_code=500, detail=result["error"]["message"])
        
        conversation_data = result["data"]
        conversation = conversation_data["conversation"]
        messages = conversation_data["messages"]
        
        # Format the export data based on requested format
        if format.lower() == "json":
            export_data = {
                "conversation": {
                    "id": str(conversation.id),
                    "title": conversation.title,
                    "created_at": conversation.created_at.isoformat(),
                    "updated_at": conversation.updated_at.isoformat(),
                    "metadata": conversation.metadata
                },
                "messages": [
                    {
                        "id": str(msg.id),
                        "role": msg.role,
                        "content": msg.content,
                        "created_at": msg.created_at.isoformat(),
                        "metadata": msg.metadata
                    }
                    for msg in messages
                ]
            }
            content_type = "application/json"
            filename = f"conversation_{conversation_id}.json"
            
        elif format.lower() == "txt":
            # Plain text format
            lines = [f"Conversation: {conversation.title}"]
            lines.append(f"Created: {conversation.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append(f"Updated: {conversation.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append("=" * 50)
            lines.append("")
            
            for msg in messages:
                role_label = "User" if msg.role == "user" else "Assistant"
                timestamp = msg.created_at.strftime('%Y-%m-%d %H:%M:%S')
                lines.append(f"[{timestamp}] {role_label}:")
                lines.append(msg.content)
                lines.append("")
                lines.append("-" * 30)
                lines.append("")
            
            export_data = "\n".join(lines)
            content_type = "text/plain"
            filename = f"conversation_{conversation_id}.txt"
            
        elif format.lower() == "md":
            # Markdown format
            lines = [f"# {conversation.title}"]
            lines.append("")
            lines.append(f"**Created:** {conversation.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append(f"**Updated:** {conversation.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append("")
            lines.append("---")
            lines.append("")
            
            for msg in messages:
                role_label = "**User**" if msg.role == "user" else "**Assistant**"
                timestamp = msg.created_at.strftime('%Y-%m-%d %H:%M:%S')
                lines.append(f"> **{role_label}** *{timestamp}*")
                lines.append(">")
                # Handle multi-line content in markdown quote format
                content_lines = msg.content.split('\n')
                for line in content_lines:
                    lines.append(f"> {line}")
                lines.append("")
                lines.append("---")
                lines.append("")
            
            export_data = "\n".join(lines)
            content_type = "text/markdown"
            filename = f"conversation_{conversation_id}.md"
            
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")
        
        return {
            "status": "success",
            "data": {
                "content": export_data,
                "filename": filename,
                "content_type": content_type,
                "format": format.lower(),
                "exported_at": datetime.now().isoformat(),
                "message_count": len(messages)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))