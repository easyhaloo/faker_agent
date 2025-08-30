"""
API routes for the Faker Agent.

This module provides the FastAPI routes for interacting with the Faker Agent,
supporting different communication protocols (HTTP, SSE, WebSocket).
"""
import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from backend.core.assembler.llm_assembler import LLMAssembler
from backend.core.contracts.base import Message
from backend.core.contracts.execution import ExecutionPlan
from backend.core.contracts.protocol import ProtocolType
from backend.core.graph.flow_orchestrator import FlowOrchestrator
from backend.core.protocol.filtered_registry import filtered_protocol_registry

# Configure logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/agent/v1",
    tags=["agent"],
)


# Request models
class AgentRequest(BaseModel):
    """Base model for agent requests."""
    
    query: str = Field(..., description="The user query")
    conversation_id: Optional[str] = Field(None, description="The conversation ID for context")
    protocol_type: ProtocolType = Field(ProtocolType.HTTP, description="The protocol type to use")
    system_message: Optional[str] = Field(None, description="Optional system message")
    filter_strategy: Optional[str] = Field(None, description="Optional filter strategy name")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens for the response")
    temperature: Optional[float] = Field(None, description="Temperature for the LLM")


# Response models
class AgentResponse(BaseModel):
    """Base model for agent responses."""
    
    status: str = Field(..., description="The status of the response")
    data: Optional[Dict] = Field(None, description="The response data")
    error: Optional[Dict] = Field(None, description="Error information if status is 'error'")


class AnalysisResponse(BaseModel):
    """Response model for analysis requests."""
    
    status: str = Field(..., description="The status of the response")
    data: Optional[ExecutionPlan] = Field(None, description="The execution plan")
    error: Optional[Dict] = Field(None, description="Error information if status is 'error'")


class StrategyResponse(BaseModel):
    """Response model for strategy requests."""
    
    status: str = Field(..., description="The status of the response")
    data: Optional[Dict[str, List[str]]] = Field(None, description="Available strategies")
    error: Optional[Dict] = Field(None, description="Error information if status is 'error'")


@router.post("/respond", response_model=AgentResponse)
async def respond(request: AgentRequest):
    """
    Respond to a user query using the specified protocol.
    
    This endpoint processes the user query and returns a response using
    the specified protocol (HTTP, SSE, or WebSocket).
    """
    try:
        # Get the protocol handler
        protocol_handler = filtered_protocol_registry.get_protocol(request.protocol_type)
        if not protocol_handler:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported protocol: {request.protocol_type}"
            )
            
        # Create the assembler and generate an execution plan
        assembler = LLMAssembler()
        execution_plan = await assembler.create_execution_plan(request.query)
        
        # Create the orchestrator
        orchestrator = FlowOrchestrator(
            execution_plan=execution_plan,
            system_message=request.system_message,
            filter_strategy=request.filter_strategy
        )
        
        # Execute the plan and get events
        events = await orchestrator.stream(request.query)
        
        # Handle events using the protocol handler
        if request.protocol_type == ProtocolType.HTTP:
            # For HTTP, collect all events and return a single response
            all_events = []
            async for event in events:
                all_events.append(event)
            
            result = await protocol_handler.handle_events(all_events)
            return result
            
        elif request.protocol_type == ProtocolType.SSE:
            # For SSE, stream events
            return await protocol_handler.handle_events(events)
            
        else:
            # This shouldn't happen since we already checked the protocol type
            raise HTTPException(
                status_code=500,
                detail="Unsupported protocol handling implementation"
            )
            
    except Exception as e:
        logger.exception(f"Error processing request: {e}")
        return {
            "status": "error",
            "error": {
                "code": "PROCESSING_ERROR",
                "message": str(e)
            }
        }


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time communication.
    
    This endpoint establishes a WebSocket connection and processes
    user queries in real-time, returning responses as they're generated.
    """
    try:
        await websocket.accept()
        
        # Get the protocol handler
        protocol_handler = filtered_protocol_registry.get_protocol(ProtocolType.WEBSOCKET)
        if not protocol_handler:
            await websocket.close(code=1008, reason="WebSocket protocol not available")
            return
            
        # Process messages
        while True:
            # Wait for a message
            data = await websocket.receive_json()
            
            # Extract request parameters
            query = data.get("query")
            if not query:
                await websocket.send_json({
                    "status": "error",
                    "error": {
                        "code": "INVALID_REQUEST",
                        "message": "Missing 'query' parameter"
                    }
                })
                continue
                
            # Optional parameters
            system_message = data.get("system_message")
            filter_strategy = data.get("filter_strategy")
            
            try:
                # Create the assembler and generate an execution plan
                assembler = LLMAssembler()
                execution_plan = await assembler.create_execution_plan(query)
                
                # Create the orchestrator
                orchestrator = FlowOrchestrator(
                    execution_plan=execution_plan,
                    system_message=system_message,
                    filter_strategy=filter_strategy
                )
                
                # Execute the plan and get events
                events = await orchestrator.stream(query)
                
                # Handle events using the protocol handler
                await protocol_handler.handle_events(events, websocket=websocket)
                
            except Exception as e:
                logger.exception(f"Error processing WebSocket request: {e}")
                await websocket.send_json({
                    "status": "error",
                    "error": {
                        "code": "PROCESSING_ERROR",
                        "message": str(e)
                    }
                })
                
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.exception(f"WebSocket error: {e}")


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(request: AgentRequest):
    """
    Analyze a user query and return an execution plan without executing it.
    
    This endpoint processes the user query and returns an execution plan
    showing what tools would be used to respond.
    """
    try:
        # Create the assembler and generate an execution plan
        assembler = LLMAssembler()
        execution_plan = await assembler.create_execution_plan(request.query)
        
        # Return the execution plan
        return {
            "status": "success",
            "data": execution_plan
        }
        
    except Exception as e:
        logger.exception(f"Error analyzing request: {e}")
        return {
            "status": "error",
            "error": {
                "code": "ANALYSIS_ERROR",
                "message": str(e)
            }
        }


@router.get("/strategies", response_model=StrategyResponse)
async def get_strategies():
    """
    Get available filtering strategies for tools and protocols.
    
    This endpoint returns a list of available filter strategies
    for tools and protocols that can be used with the agent.
    """
    from backend.core.filters.filter_manager import filter_manager
    
    try:
        # Get tool strategies
        tool_strategies = filter_manager.list_tool_strategies()
        
        # Get protocol strategies
        protocol_strategies = filter_manager.list_protocol_strategies()
        
        # Return strategies
        return {
            "status": "success",
            "data": {
                "tool_strategies": tool_strategies,
                "protocol_strategies": protocol_strategies
            }
        }
        
    except Exception as e:
        logger.exception(f"Error getting strategies: {e}")
        return {
            "status": "error",
            "error": {
                "code": "STRATEGY_ERROR",
                "message": str(e)
            }
        }