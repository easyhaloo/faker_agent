"""
Enhanced API routes for the Faker Agent with real-time task status support.
"""
import asyncio
import logging
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.api.agent_routes import router as agent_router
from backend.core.simple_agent import SimpleAgent as Agent
from backend.core.tools.registry import tool_registry
from backend.modules.weather.routes import router as weather_router

# Configure logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Include module routers
router.include_router(agent_router, prefix="/agent/v1", tags=["agent"])
router.include_router(weather_router, prefix="/weather", tags=["weather"])

# Initialize agent
agent = Agent()

# In-memory task store (would use Redis in production)
tasks = {}

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


class TaskStatus(BaseModel):
    """Task status information."""
    
    task_id: str
    status: str  # pending, running, completed, failed
    progress: int = 0  # 0-100
    result: Optional[Dict[str, Any]] = None
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
        response = await agent.process_query(request.query)
        
        return TaskResponse(**response)
        
    except Exception as e:
        logger.error(f"Error processing task: {e}")
        return TaskResponse(
            status="error",
            error={
                "code": "PROCESSING_ERROR",
                "message": str(e)
            }
        )


@router.post("/agent/task/async", response_model=TaskResponse)
async def submit_async_task(request: TaskRequest):
    """Submit a task to the agent asynchronously with real-time status updates."""
    # Generate task ID
    task_id = str(uuid4())
    
    # Initialize task status
    tasks[task_id] = {
        "status": "pending",
        "progress": 0,
        "result": None,
        "error": None
    }
    
    # Start background task processing
    asyncio.create_task(process_task_async(task_id, request.query))
    
    return TaskResponse(
        status="success",
        data={
            "task_id": task_id,
            "message": "Task submitted successfully"
        }
    )


async def process_task_async(task_id: str, query: str):
    """Process a task asynchronously and update its status."""
    try:
        # Update status to running
        tasks[task_id]["status"] = "running"
        tasks[task_id]["progress"] = 10
        
        # Simulate progress updates
        for i in range(1, 10):
            await asyncio.sleep(0.5)  # Simulate work
            tasks[task_id]["progress"] = 10 + i * 9  # Progress from 10% to 90%
        
        # Process the query
        response = await agent.process_query(query)
        tasks[task_id]["progress"] = 100
        
        # Update status to completed
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["result"] = response
        
    except Exception as e:
        logger.error(f"Error processing task {task_id}: {e}")
        # Update status to failed
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = {
            "code": "PROCESSING_ERROR",
            "message": str(e)
        }


@router.get("/agent/task/{task_id}", response_model=TaskResponse)
async def get_task_status(task_id: str):
    """Get the status of a task."""
    if task_id not in tasks:
        return TaskResponse(
            status="error",
            error={
                "code": "TASK_NOT_FOUND",
                "message": f"Task {task_id} not found"
            }
        )
    
    task_info = tasks[task_id]
    return TaskResponse(
        status="success",
        data=task_info
    )


@router.get("/agent/task/{task_id}/stream")
async def stream_task_status(task_id: str):
    """Stream task status updates in real-time."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    async def event_generator():
        last_progress = -1
        while True:
            # Check if task exists
            if task_id not in tasks:
                break
                
            task_info = tasks[task_id]
            current_progress = task_info["progress"]
            
            # Send update if progress has changed
            if current_progress > last_progress:
                yield f"data: {current_progress}\n\n"
                last_progress = current_progress
                
                # Break if task is completed or failed
                if task_info["status"] in ["completed", "failed"]:
                    break
            
            # Wait before next check
            await asyncio.sleep(0.5)
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/tools", response_model=TaskResponse)
async def list_tools():
    """List all available tools."""
    try:
        tools = tool_registry.list_tools()
        
        return TaskResponse(
            status="success",
            data={
                "tools": [tool.dict() for tool in tools]
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
                "active_tasks": len(tasks)  # Current number of tasks
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