"""
Enhanced API routes for the Faker Agent with protocol support.
"""
import asyncio
import uuid
from typing import Any, Dict, List, Optional

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.core.agent import Agent
from backend.core.assembler.llm_assembler import assembler
from backend.core.filters.filter_manager import filter_manager
from backend.core.graph.event_types import Event, EventType
from backend.core.graph.flow_orchestrator import FlowOrchestrator
from backend.core.protocol.protocol_factory import ProtocolType, protocol_factory
from backend.core.utils.logging import get_logger



# Ensure logger propagates to root logger
logger = get_logger(__name__)
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
        # 简化处理，直接调用agent的graph._call_llm方法
        # 该方法已经在agent_graph.py中完成了必要的消息格式转换
        try:
            result = await agent.graph._call_llm(state)
            return result
        except Exception as e:
            logger.error(f"Error in llm_node_adapter: {e}")
            return {
                "messages": [AIMessage(content=f"处理您的请求时发生错误: {e}")]
            }
    
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
        # Test log message to verify logging is working
        print("TEST PRINT: Agent respond function called")
        logger.critical("TEST CRITICAL LOG: Agent respond function called")
        logger.error("TEST ERROR LOG: Agent respond function called")
        logger.warning("TEST WARNING LOG: Agent respond function called")
        logger.info("TEST INFO LOG: Agent respond function called")
        logger.debug("TEST DEBUG LOG: Agent respond function called")
        
        # Log request parameters
        logger.info(f"Agent respond request received - Protocol: {request.protocol}, Mode: {request.mode}, Input: {request.input[:100]}...")
        logger.info(f"Request details - Conversation ID: {request.conversation_id}, Filter Strategy: {request.filter_strategy}, Tool Tags: {request.tool_tags}")
        if request.params:
            logger.info(f"Additional parameters: {request.params}")
        
        # Check if this is a WebSocket request
        if request.protocol.lower() == ProtocolType.WEBSOCKET:
            logger.warning(f"Invalid protocol request: {request.protocol} for HTTP endpoint")
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
            logger.error(f"Unknown protocol requested: {request.protocol}")
            return {
                "status": "error",
                "error": {
                    "code": "INVALID_PROTOCOL",
                    "message": f"Unknown protocol: {request.protocol}"
                }
            }
            
        # Create a flow orchestrator
        logger.info(f"Creating flow orchestrator with filter strategy: {request.filter_strategy}, tool tags: {request.tool_tags}")
        orchestrator = await _create_flow_orchestrator(
            filter_strategy=request.filter_strategy,
            tool_tags=request.tool_tags
        )
        
        # Generate a conversation ID if not provided
        conversation_id = request.conversation_id or str(uuid.uuid4())
        logger.info(f"Using conversation ID: {conversation_id}")
        
        # Check the mode
        if request.mode.lower() == "sync":
            # Synchronous mode
            logger.info("Processing request in synchronous mode")
            events = []
            
            # Define event callback
            async def event_callback(event: Event):
                events.append(event)
            
            # 使用消息格式化工具创建标准格式的消息
            from backend.core.utils.message_formatter import message_formatter
            
            # 调用编排器处理消息
            logger.info(f"Invoking orchestrator with input: {request.input[:100]}...")
            await orchestrator.invoke(
                request.input,
                conversation_id=conversation_id,
                event_callback=event_callback
            )
            
            # Return the response using the protocol handler
            logger.info(f"Processing {len(events)} events with protocol handler")
            return await protocol_handler.handle_events(events)
            
        else:
            # Streaming mode
            logger.info("Processing request in streaming mode")
            if request.protocol.lower() == ProtocolType.HTTP:
                # HTTP doesn't support streaming
                logger.warning("HTTP protocol requested with streaming mode - not supported")
                return {
                    "status": "error",
                    "error": {
                        "code": "INVALID_MODE",
                        "message": "HTTP protocol does not support streaming mode"
                    }
                }
                
            # Create event stream
            logger.info("Creating event stream for streaming response")
            event_stream = orchestrator.stream_invoke(
                request.input,
                conversation_id=conversation_id
            )
            
            # Return the streaming response
            logger.info("Streaming response to client")
            return await protocol_handler.handle_events(event_stream)
            
    except Exception as e:
        logger.error(f"Error processing agent request: {e}")
        logger.error(f"Request that caused error: {request.dict() if request else 'No request data'}")
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
                tool_tags=request.tool_tags
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