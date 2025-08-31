"""
Main router for the Faker Agent API.

This module provides the central router that includes all API routes.
"""
from fastapi import APIRouter

from backend.api.agent_routes import router as agent_router
from backend.api.conversation_routes import router as conversation_router
from backend.api.memory_routes import router as memory_router
from backend.core.utils.logging import get_logger

# Configure logger
logger = get_logger(__name__)

# Create router
router = APIRouter()

# Include module routers
router.include_router(agent_router, prefix="/agent/v1", tags=["agent"])
router.include_router(conversation_router, prefix="/conversations", tags=["conversations"])
router.include_router(memory_router, prefix="/memory", tags=["memory"])

logger.info("Initialized main API router with agent, conversation, and memory routes")