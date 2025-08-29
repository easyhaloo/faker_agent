"""
Enhanced API routes for the Faker Agent with protocol support.
"""
import asyncio
import logging
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.core.agent import Agent
from backend.core.assembler.llm_assembler import assembler
from backend.core.filters.filter_manager import filter_manager
from backend.core.graph.event_types import Event, EventType
from backend.core.graph.flow_orchestrator import FlowOrchestrator
from backend.core.protocol.protocol_factory import ProtocolType, protocol_factory

# Configure logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


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
    tool_tags: Optional[List[str]] = None
) -> FlowOrchestrator:
    """
    Create a flow orchestrator with the specified filters.
    
    Args:
        filter_strategy: Optional filter strategy name
        tool_tags: Optional tool tags to filter by
        
    Returns:
        A flow orchestrator instance
    """
    # Use the regular Agent's LLM node for simplicity
    agent = Agent()
    
    # Create an adapter for the LLM node to handle different state formats
    async def llm_node_adapter(state):
        # If state is a dict (flow_orchestrator format), extract messages
        if isinstance(state, dict):
            messages = state.get("messages", [])
        # If state is a list (agent_graph format), use as-is
        elif isinstance(state, list):
            messages = state
        else:
            messages = []
        
        # Call the original LLM node with the extracted messages
        return await agent.graph._call_llm(messages)
    
    # Create a flow orchestrator
    orchestrator = FlowOrchestrator(
        llm_node=llm_node_adapter,
        filter_strategy=filter_strategy,
        tool_tags=tool_tags
    )
    
    return orchestrator


@router.post("/respond", response_model=AgentResponse)
async def agent_respond(request: AgentRequest):
    """
    Send a query to the agent with protocol support.
    
    This endpoint automatically routes to the appropriate protocol handler
    based on the 'protocol' parameter.
    """
    try:
        # Check if this is a WebSocket request
        if request.protocol.lower() == ProtocolType.WEBSOCKET:
            return {
                "status": "error",
                "error": {
                    "code": "INVALID_PROTOCOL",
                    "message": "WebSocket requests should use the /agent/ws endpoint"
                }
            }
            
        # Get the protocol handler
        protocol_handler = protocol_factory.get_protocol(request.protocol)
        if not protocol_handler:
            return {
                "status": "error",
                "error": {
                    "code": "INVALID_PROTOCOL",
                    "message": f"Unknown protocol: {request.protocol}"
                }
            }
            
        # Create a flow orchestrator
        orchestrator = await _create_flow_orchestrator(
            filter_strategy=request.filter_strategy,
            tool_tags=request.tool_tags
        )
        
        # Generate a conversation ID if not provided
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Check the mode
        if request.mode.lower() == "sync":
            # Synchronous mode
            events = []
            
            # Define event callback
            async def event_callback(event: Event):
                events.append(event)
            
            # Invoke the orchestrator
            await orchestrator.invoke(
                request.input,
                conversation_id=conversation_id,
                event_callback=event_callback
            )
            
            # Return the response using the protocol handler
            return await protocol_handler.handle_events(events)
            
        else:
            # Streaming mode
            if request.protocol.lower() == ProtocolType.HTTP:
                # HTTP doesn't support streaming
                return {
                    "status": "error",
                    "error": {
                        "code": "INVALID_MODE",
                        "message": "HTTP protocol does not support streaming mode"
                    }
                }
                
            # Create event stream
            event_stream = orchestrator.stream_invoke(
                request.input,
                conversation_id=conversation_id
            )
            
            # Return the streaming response
            return await protocol_handler.handle_events(event_stream)
            
    except Exception as e:
        logger.error(f"Error processing agent request: {e}")
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
            
            # Parse the request
            try:
                request = AgentRequest(**data)
            except Exception as e:
                logger.error(f"Invalid WebSocket request: {e}")
                await websocket.send_json({
                    "status": "error",
                    "error": {
                        "code": "INVALID_REQUEST",
                        "message": str(e)
                    }
                })
                continue
                
            # Create a flow orchestrator
            orchestrator = await _create_flow_orchestrator(
                filter_strategy=request.filter_strategy,
                tool_tags=request.tool_tags
            )
            
            # Generate a conversation ID if not provided
            conversation_id = request.conversation_id or str(uuid.uuid4())
            
            # Create event stream
            event_stream = orchestrator.stream_invoke(
                request.input,
                conversation_id=conversation_id
            )
            
            # Stream events to the client
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
        # Create an execution plan
        execution_plan = await assembler.create_execution_plan(request.input)
        
        return {
            "status": "success",
            "data": {
                "query": request.input,
                "plan": execution_plan.dict()
            }
        }
        
    except Exception as e:
        logger.error(f"Error analyzing query: {e}")
        return {
            "status": "error",
            "error": {
                "code": "ANALYSIS_ERROR",
                "message": str(e)
            }
        }


@router.get("/strategies", response_model=AgentResponse)
async def list_strategies():
    """
    List available filter strategies.
    """
    try:
        # Get strategies from the filter manager
        strategies = list(filter_manager.strategies.keys())
        
        return {
            "status": "success",
            "data": {
                "strategies": strategies
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