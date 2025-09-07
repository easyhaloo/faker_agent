"""
Memory management API routes for the Faker Agent.

This module provides endpoints for managing different types of memory:
- Global/project profile memory
- Session-level episodic memory
- Conversation summaries
- Memory settings
"""
from typing import Dict, List, Optional, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.core.infrastructure.database import get_db
from backend.core.models.memory import (
    MemoryProfile, MemoryEpisode, ConversationSummary, MemoryAudit,
    MemoryProfileCreate, MemoryEpisodeCreate, MemorySettings,
    MemoryProfileUpdate, MemoryEpisodeUpdate, MemoryResponse,
    MemoryType, MemoryScope
)
from backend.core.services.memory_service import enhanced_memory_service as memory_service
from backend.core.utils.logging import get_logger

# Configure logger
logger = get_logger(__name__)

# Create router
router = APIRouter()


# Memory Profile (Global/Project Memory) Routes

@router.post("/profile", response_model=MemoryProfile, status_code=201)
async def create_profile_memory(
    memory: MemoryProfileCreate,
) -> MemoryProfile:
    """
    Create a new profile memory (global or project-level).
    """
    try:
        result = await memory_service.create_profile_memory(memory)
        logger.info(f"Created profile memory: {result.key}")
        return result
    except Exception as e:
        logger.error(f"Error creating profile memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile", response_model=List[MemoryProfile])
async def get_profile_memories(
    scope: Optional[MemoryScope] = None,
    project_id: Optional[UUID] = None,
    memory_type: Optional[MemoryType] = None,
    key: Optional[str] = None,
    user_id: str = "default_user",
) -> List[MemoryProfile]:
    """
    Get profile memories based on filters.
    """
    try:
        memories = await memory_service.get_profile_memories(
            scope=scope,
            project_id=project_id,
            memory_type=memory_type,
            key=key,
            user_id=user_id
        )
        return memories
    except Exception as e:
        logger.error(f"Error retrieving profile memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/profile/{memory_id}", response_model=MemoryProfile)
async def update_profile_memory(
    memory_id: UUID,
    updates: MemoryProfileUpdate,
) -> MemoryProfile:
    """
    Update an existing profile memory.
    """
    try:
        result = await memory_service.update_profile_memory(
            memory_id=memory_id,
            updates=updates.dict(exclude_unset=True)
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Memory not found")
            
        logger.info(f"Updated profile memory: {memory_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating profile memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/profile/{memory_id}", response_model=MemoryResponse)
async def delete_profile_memory(
    memory_id: UUID,
) -> MemoryResponse:
    """
    Delete a profile memory.
    """
    try:
        success = await memory_service.delete_profile_memory(memory_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Memory not found")
            
        logger.info(f"Deleted profile memory: {memory_id}")
        return MemoryResponse(
            status="success",
            message="Memory deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting profile memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Memory Episode (Session Memory) Routes

@router.post("/episode", response_model=MemoryEpisode, status_code=201)
async def create_episode_memory(
    memory: MemoryEpisodeCreate,
) -> MemoryEpisode:
    """
    Create a new episode memory for a conversation.
    """
    try:
        result = await memory_service.create_episode_memory(memory)
        logger.info(f"Created episode memory: {result.title}")
        return result
    except Exception as e:
        logger.error(f"Error creating episode memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/episode/{conversation_id}", response_model=List[MemoryEpisode])
async def get_episode_memories(
    conversation_id: UUID,
    memory_type: Optional[MemoryType] = None,
) -> List[MemoryEpisode]:
    """
    Get episode memories for a conversation.
    """
    try:
        memories = await memory_service.get_episode_memories(
            conversation_id=conversation_id,
            memory_type=memory_type
        )
        return memories
    except Exception as e:
        logger.error(f"Error retrieving episode memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/episode/{memory_id}", response_model=MemoryEpisode)
async def update_episode_memory(
    memory_id: UUID,
    updates: MemoryEpisodeUpdate,
) -> MemoryEpisode:
    """
    Update an existing episode memory.
    """
    try:
        result = await memory_service.update_episode_memory(
            memory_id=memory_id,
            updates=updates.dict(exclude_unset=True)
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Memory not found")
            
        logger.info(f"Updated episode memory: {memory_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating episode memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/episode/{memory_id}", response_model=MemoryResponse)
async def delete_episode_memory(
    memory_id: UUID,
) -> MemoryResponse:
    """
    Delete an episode memory.
    """
    try:
        success = await memory_service.delete_episode_memory(memory_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Memory not found")
            
        logger.info(f"Deleted episode memory: {memory_id}")
        return MemoryResponse(
            status="success",
            message="Memory deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting episode memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Summary Routes

@router.get("/summary/{conversation_id}", response_model=Optional[ConversationSummary])
async def get_conversation_summary(
    conversation_id: UUID,
) -> Optional[ConversationSummary]:
    """
    Get the latest summary for a conversation.
    """
    try:
        summary = await memory_service.get_latest_summary(conversation_id)
        return summary
    except Exception as e:
        logger.error(f"Error retrieving conversation summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Memory Settings Routes

@router.post("/settings", response_model=MemorySettings)
async def create_or_update_memory_settings(
    settings: MemorySettings,
    user_id: str = "default_user",
) -> MemorySettings:
    """
    Create or update memory settings.
    """
    try:
        result = await memory_service.create_or_update_memory_settings(
            settings=settings,
            user_id=user_id
        )
        logger.info(f"Updated memory settings for user: {user_id}")
        return result
    except Exception as e:
        logger.error(f"Error updating memory settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/settings", response_model=MemorySettings)
async def get_memory_settings(
    user_id: str = "default_user",
) -> MemorySettings:
    """
    Get memory settings.
    """
    try:
        settings = await memory_service.get_memory_settings(user_id=user_id)
        return settings
    except Exception as e:
        logger.error(f"Error retrieving memory settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Audit Routes

@router.get("/audit", response_model=List[MemoryAudit])
async def get_memory_audit_logs(
    target_type: Optional[str] = None,
    action: Optional[str] = None,
    limit: int = 100,
) -> List[MemoryAudit]:
    """
    Get memory audit logs.
    """
    try:
        logs = await memory_service.get_memory_audit_logs(
            target_type=target_type,
            action=action,
            limit=limit
        )
        return logs
    except Exception as e:
        logger.error(f"Error retrieving memory audit logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))