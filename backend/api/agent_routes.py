"""
Enhanced API routes for the Faker Agent with protocol support.
"""
import asyncio
import json
import time
import uuid
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, validator

from backend.core.services.agent_service import AgentService
from backend.core.assembler.llm_assembler import assembler
from backend.core.filters.filter_manager import filter_manager
from backend.core.graph.event_types import Event, EventType
from backend.core.graph.flow_orchestrator import FlowOrchestrator
from backend.core.protocol.protocol_factory import ProtocolType, protocol_factory
from backend.core.tools.registry import tool_registry
from backend.core.utils.logging import get_logger



# Ensure logger propagates to root logger
logger = get_logger(__name__)
# Create router
router = APIRouter()

# In-memory task store (would use Redis in production)
tasks = {}

# Define request and response models
class TaskRequest(BaseModel):
    """
Request to submit a task to the agent.
    """
    
    query: str
    context: Dict[str, Any] = {}
    stream: bool = False


class TaskResponse(BaseModel):
    """
Response from the agent.
    """
    
    status: str = "success"
    data: Dict[str, Any] = {}
    error: Optional[Dict[str, Any]] = None


class TaskStatus(BaseModel):
    """
Task status information.
    """
    
    task_id: str
    status: str  # pending, running, completed, failed
    progress: int = 0  # 0-100
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """
Error response.
    """
    
    code: str
    message: str


# Define request and response models
class AgentRequest(BaseModel):
    """Request for the agent API."""
    
    input: str = Field(..., description="User input query")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    protocol: str = Field("http", description="Response protocol (http, sse, websocket)")
    mode: str = Field("stream", description="Response mode (sync, stream)")
    filter_strategy: Optional[str] = Field(None, description="Tool filter strategy")
    tool_tags: Optional[List[str]] = Field(None, description="Tool tags to filter by")
    params: Optional[Dict[str, Any]] = Field(None, description="Additional parameters")


class AgentResponse(BaseModel):
    """Response from the agent API."""
    
    status: str = "success"
    data: Dict[str, Any] = {}
    error: Optional[Dict[str, Any]] = None


async def _create_flow_orchestrator(
    filter_strategy: Optional[str] = None,
    tool_tags: Optional[List[str]] = None,
    streaming: Optional[bool] = None
) -> FlowOrchestrator:
    """
    Create a flow orchestrator with the specified filters.
    
    Args:
        filter_strategy: Optional filter strategy name
        tool_tags: Optional tool tags to filter by
        streaming: Optional flag to enable streaming in LLM adapter selection
        
    Returns:
        A flow orchestrator instance
    """
    # Create a flow orchestrator with its default LLM node (no private method usage)
    orchestrator = FlowOrchestrator(
        filter_strategy=filter_strategy,
        tool_tags=tool_tags,
        streaming=bool(streaming) if streaming is not None else False
    )
    
    return orchestrator


@router.post("/respond", response_model=None)
async def agent_respond(request_data: Dict[str, Any] = Body(...)):
    """
    Send a query to the agent with protocol support.
    
    This endpoint automatically routes to the appropriate protocol handler
    based on the 'protocol' parameter.
    """
    try:
        # Create agent request
        agent_request = AgentRequest(**request_data)
    except Exception as e:
        logger.error(f"Error parsing request: {e}")
        return {
            "status": "error",
            "error": {
                "code": "INVALID_REQUEST",
                "message": f"Invalid request format: {str(e)}"
            }
        }
    try:
        # Log request parameters
        logger.info("Agent respond function called with POST request")
        logger.info(f"Input: {agent_request.input[:100]}..., Protocol: {agent_request.protocol}, Mode: {agent_request.mode}")
        logger.info(f"Conversation ID: {agent_request.conversation_id}, Filter Strategy: {agent_request.filter_strategy}, Tool Tags: {agent_request.tool_tags}")
        
        # Add additional parameters log if they exist
        if agent_request.params:
            logger.info(f"Additional parameters: {agent_request.params}")
        
        # Check for WebSocket protocol (redirect to WebSocket endpoint)
        if agent_request.protocol.lower() == ProtocolType.WEBSOCKET:
            logger.warning("WebSocket protocol requested - redirecting to WebSocket endpoint")
            return {
                "status": "error",
                "error": {
                    "code": "INVALID_PROTOCOL",
                    "message": "WebSocket requests should use the /agent/ws endpoint"
                }
            }
            
        # Get the protocol handler
        protocol_handler = protocol_factory.get_protocol(agent_request.protocol)
        if not protocol_handler:
            logger.error(f"Unknown protocol requested: {agent_request.protocol}")
            return {
                "status": "error",
                "error": {
                    "code": "INVALID_PROTOCOL",
                    "message": f"Unsupported protocol: {agent_request.protocol}. Use 'http', 'sse', or 'websocket'."
                }
            }
            
        # Create flow orchestrator based on request parameters
        streaming_mode = agent_request.mode.lower() != "sync"
        logger.info(f"Creating flow orchestrator: strategy={agent_request.filter_strategy}, tags={agent_request.tool_tags}, streaming={streaming_mode}")
        orchestrator = await _create_flow_orchestrator(
            filter_strategy=agent_request.filter_strategy,
            tool_tags=agent_request.tool_tags,
            streaming=streaming_mode
        )
        
        # Generate a conversation ID if not provided
        conversation_id = agent_request.conversation_id or str(uuid.uuid4())
        logger.info(f"Using conversation ID: {conversation_id}")
        
        # Check if streaming mode is requested with HTTP protocol (not supported)
        if agent_request.mode.lower() != "sync" and agent_request.protocol.lower() == ProtocolType.HTTP:
            logger.warning("HTTP protocol does not support streaming mode")
            return {
                "status": "error",
                "error": {
                    "code": "INVALID_MODE",
                    "message": "HTTP protocol does not support streaming mode. Use 'sync' mode or 'sse'/'websocket' protocol."
                }
            }
            
        # Handle request based on mode
        logger.info(f"Processing in {agent_request.mode} mode with {agent_request.protocol} protocol")
        logger.info(f"Conversation ID: {conversation_id}")
        
        if agent_request.mode.lower() == "sync":
            # Synchronous mode - collect all events
            events = []
            async def event_callback(event: Event):
                events.append(event)
                
            # Invoke orchestrator
            await orchestrator.invoke(
                agent_request.input,
                conversation_id=conversation_id,
                event_callback=event_callback
            )
            
            logger.info(f"Processed {len(events)} events")
            return await protocol_handler.handle_events(events)
        else:
            # Streaming mode - create event stream
            event_stream = orchestrator.stream_invoke(
                agent_request.input,
                conversation_id=conversation_id
            )
            
            # For SSE protocol and weather queries, direct handling with centralized utilities
            if agent_request.protocol.lower() == ProtocolType.SSE:
                # Import here to avoid circular imports
                from backend.core.utils.weather_utils import is_weather_query, get_sse_weather_event
                
                if is_weather_query(agent_request.input):
                    logger.info("Weather query detected in POST endpoint - using centralized weather utils")
                    
                    # Create a streaming response with the appropriate headers
                    async def direct_weather_response():
                        # Get weather event from centralized utility
                        weather_event_data = await get_sse_weather_event(agent_request.input)
                        yield weather_event_data
                    
                    return StreamingResponse(
                        direct_weather_response(),
                        media_type="text/event-stream",
                        headers={
                            "Cache-Control": "no-cache",
                            "Connection": "keep-alive",
                            "Content-Type": "text/event-stream",
                            "X-Accel-Buffering": "no"
                        }
                    )
            
            # For all other cases, use the protocol handler
            logger.info(f"Streaming response using {agent_request.protocol} protocol")
            return await protocol_handler.handle_events(event_stream)
            
    except Exception as e:
        logger.error(f"Error processing agent request: {e}", exc_info=True)
        return {
            "status": "error",
            "error": {
                "code": "PROCESSING_ERROR",
                "message": str(e)
            }
        }


@router.websocket("/ws")
async def agent_websocket(websocket: WebSocket):
    """WebSocket endpoint for the agent."""
    try:
        # Accept the connection
        await websocket.accept()
        logger.info("WebSocket connection established")
        
        # Get the protocol handler
        protocol_handler = protocol_factory.get_protocol(ProtocolType.WEBSOCKET)
        
        while True:
            # Wait for a message
            data = await websocket.receive_json()
            logger.info(f"WebSocket message received: {data}")
            
            # Parse the request
            try:
                request = AgentRequest(**data)
                logger.info(f"WebSocket request parsed - Protocol: {request.protocol}, Mode: {request.mode}, Input: {request.input[:100]}...")
                logger.info(f"WebSocket request details - Conversation ID: {request.conversation_id}, Filter Strategy: {request.filter_strategy}, Tool Tags: {request.tool_tags}")
                if request.params:
                    logger.info(f"WebSocket additional parameters: {request.params}")
            except Exception as e:
                logger.error(f"Invalid WebSocket request: {e}")
                logger.error(f"Raw WebSocket data that caused error: {data}")
                await websocket.send_json({
                    "status": "error",
                    "error": {
                        "code": "INVALID_REQUEST",
                        "message": str(e)
                    }
                })
                continue
                
            # Create a flow orchestrator
            logger.info(f"Creating WebSocket flow orchestrator with filter strategy: {request.filter_strategy}, tool tags: {request.tool_tags}")
            orchestrator = await _create_flow_orchestrator(
                filter_strategy=request.filter_strategy,
                tool_tags=request.tool_tags,
                streaming=True
            )
            
            # Generate a conversation ID if not provided
            conversation_id = request.conversation_id or str(uuid.uuid4())
            logger.info(f"WebSocket using conversation ID: {conversation_id}")
            
            # Create event stream
            logger.info(f"Creating WebSocket event stream for input: {request.input[:100]}...")
            event_stream = orchestrator.stream_invoke(
                request.input,
                conversation_id=conversation_id
            )
            
            # Stream events to the client
            logger.info("Streaming WebSocket events to client")
            await protocol_handler.handle_events(event_stream, websocket=websocket)
            
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_json({
                "status": "error",
                "error": {
                    "code": "WEBSOCKET_ERROR",
                    "message": str(e)
                }
            })
        except:
            pass


@router.post("/analyze", response_model=AgentResponse)
async def analyze_query(request: AgentRequest):
    """
    Analyze a query and return an execution plan.
    
    This endpoint uses the LLM Assembler to create a plan for the query
    without actually executing it.
    """
    try:
        # Log request parameters
        logger.info(f"Analyze query request received - Protocol: {request.protocol}, Mode: {request.mode}, Input: {request.input[:100]}...")
        logger.info(f"Analyze request details - Conversation ID: {request.conversation_id}, Filter Strategy: {request.filter_strategy}, Tool Tags: {request.tool_tags}")
        if request.params:
            logger.info(f"Analyze additional parameters: {request.params}")
        
        # Create an execution plan
        logger.info(f"Creating execution plan for query: {request.input[:100]}...")
        execution_plan = await assembler.create_execution_plan(request.input)
        
        logger.info(f"Execution plan created successfully for query: {request.input[:100]}...")
        return {
            "status": "success",
            "data": {
                "query": request.input,
                "plan": execution_plan.dict()
            }
        }
        
    except Exception as e:
        logger.error(f"Error analyzing query: {e}")
        logger.error(f"Analyze request that caused error: {request.dict() if request else 'No request data'}")
        return {
            "status": "error",
            "error": {
                "code": "ANALYSIS_ERROR",
                "message": str(e)
            }
        }


@router.get("/sse_respond")
async def agent_sse_respond(
    input: str = Query(..., description="User input query"),
    conversation_id: Optional[str] = Query(None, description="Conversation ID for context"),
    filter_strategy: Optional[str] = Query(None, description="Tool filter strategy"),
    tool_tags: Optional[str] = Query(None, description="Comma-separated tool tags to filter by")
):
    """GET endpoint for SSE streaming responses."""
    try:
        # Log request parameters
        logger.info(f"SSE respond request received - Input: {input[:100]}...")
        logger.info(f"SSE request details - Conversation ID: {conversation_id}, Filter Strategy: {filter_strategy}, Tool Tags: {tool_tags}")
        
        # Parse tool tags if provided
        parsed_tool_tags = tool_tags.split(",") if tool_tags else None
        
        # Create a flow orchestrator
        logger.info(f"Creating SSE flow orchestrator with filter strategy: {filter_strategy}, tool tags: {parsed_tool_tags}")
        orchestrator = await _create_flow_orchestrator(
            filter_strategy=filter_strategy,
            tool_tags=parsed_tool_tags,
            streaming=True
        )
        
        # Generate a conversation ID if not provided
        conv_id = conversation_id or str(uuid.uuid4())
        logger.info(f"Using conversation ID: {conv_id}")
        
        # Get the protocol handler
        protocol_handler = protocol_factory.get_protocol(ProtocolType.SSE)
        if not protocol_handler:
            logger.error("SSE protocol handler not found")
            return {
                "status": "error",
                "error": {
                    "code": "INVALID_PROTOCOL",
                    "message": "SSE protocol handler not found"
                }
            }
        
        # Create event stream
        logger.info("Creating SSE event stream for streaming response")
        event_stream = orchestrator.stream_invoke(
            input,
            conversation_id=conv_id
        )
        
        # Check if this is a weather query using centralized utility
        from backend.core.utils.weather_utils import is_weather_query, get_sse_weather_event
        
        weather_query = is_weather_query(input)
        
        # For weather queries, direct handling with centralized utilities
        if weather_query:
            logger.info("Weather query detected - using centralized weather utils")
            
            # Create a streaming response with the appropriate headers
            async def direct_weather_response():
                # Get weather event from centralized utility
                weather_event_data = await get_sse_weather_event(input)
                yield weather_event_data
            
            return StreamingResponse(
                direct_weather_response(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "text/event-stream",
                    "X-Accel-Buffering": "no"
                }
            )
        
        # Return the regular streaming response for non-weather queries
        logger.info("Streaming SSE response to client")
        return await protocol_handler.handle_events(event_stream, is_weather_query=weather_query)
        
    except Exception as e:
        logger.error(f"Error processing SSE request: {e}")
        return {
            "status": "error",
            "error": {
                "code": "PROCESSING_ERROR",
                "message": str(e)
            }
        }




@router.get("/strategies", response_model=AgentResponse)
async def list_strategies():
    """
    List available filter strategies.
    """
    try:
        logger.info("List strategies request received")
        
        # Get strategies from the filter manager
        tool_strategies = filter_manager.list_tool_strategies()
        protocol_strategies = filter_manager.list_protocol_strategies()
        logger.info(f"Retrieved {len(tool_strategies)} tool strategies and {len(protocol_strategies)} protocol strategies")
        
        return {
            "status": "success",
            "data": {
                "tool_strategies": tool_strategies,
                "protocol_strategies": protocol_strategies
            }
        }
        
    except Exception as e:
        logger.error(f"Error listing strategies: {e}")
        return {
            "status": "error",
            "error": {
                "code": "STRATEGY_ERROR",
                "message": str(e)
            }
        }


@router.post("/task", response_model=TaskResponse)
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


@router.post("/task/async", response_model=TaskResponse)
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


@router.get("/task/{task_id}", response_model=TaskResponse)
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


@router.get("/task/{task_id}/stream")
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