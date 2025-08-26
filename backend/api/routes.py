"""
API routes for the Faker Agent.
"""
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from backend.core.agent import agent
from backend.core.registry.base_registry import registry
from backend.modules.weather.routes import router as weather_router

# Configure logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Include module routers
router.include_router(weather_router, prefix="/weather", tags=["weather"])


# Define request and response models
class TaskRequest(BaseModel):
    """Request to submit a task to the agent."""
    
    query: str
    context: Dict[str, Any] = {}
    stream: bool = False


class TaskResponse(BaseModel):
    """Response from the agent."""
    
    status: str = "success"
    data: Dict[str, Any] = {}
    error: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Error response."""
    
    code: str
    message: str


@router.post("/agent/task", response_model=TaskResponse)
async def submit_task(request: TaskRequest):
    """Submit a task to the agent."""
    try:
        # Process the query
        response = await agent.process_query(
            query=request.query,
            context=request.context
        )
        
        return TaskResponse(
            status="success",
            data={
                "task_id": response.task_id,
                "response": response.response,
                "actions": response.actions
            }
        )
        
    except Exception as e:
        logger.error(f"Error processing task: {e}")
        return TaskResponse(
            status="error",
            error={
                "code": "PROCESSING_ERROR",
                "message": str(e)
            }
        )


@router.get("/agent/task/{task_id}", response_model=TaskResponse)
async def get_task_status(task_id: str):
    """Get the status of a task."""
    # This is a placeholder - we'd need a task tracking system
    return TaskResponse(
        status="success",
        data={
            "task_id": task_id,
            "status": "completed",  # Mock status
            "progress": 100,
            "result": {}
        }
    )


@router.get("/tools", response_model=TaskResponse)
async def list_tools():
    """List all available tools."""
    try:
        tools = registry.list_tools()
        
        return TaskResponse(
            status="success",
            data={
                "tools": tools
            }
        )
        
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        return TaskResponse(
            status="error",
            error={
                "code": "TOOLS_ERROR",
                "message": str(e)
            }
        )


@router.get("/system/status", response_model=TaskResponse)
async def get_system_status():
    """Get system status."""
    try:
        return TaskResponse(
            status="success",
            data={
                "version": "0.1.0",
                "uptime": "0d 0h 0m",  # Placeholder
                "memory_usage": "0MB",  # Placeholder
                "active_tasks": 0  # Placeholder
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return TaskResponse(
            status="error",
            error={
                "code": "STATUS_ERROR",
                "message": str(e)
            }
        )