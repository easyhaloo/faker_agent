"""
Flow orchestrator for the LangGraph agent.

This module provides an enhanced flow orchestrator that supports
streaming events and tool filtering. It implements the core orchestration
logic for the Faker Agent system, managing the execution flow of tools
and LLM interactions through a graph-based workflow.
"""
import asyncio
import logging
import time
import traceback
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Set, Union

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import END, StateGraph
from typing import TypedDict, Optional as OptionalType
from langgraph.prebuilt import ToolNode

from backend.config.settings import settings
from backend.core.contracts.base import Message as FakerMessage
from backend.core.contracts.tools import ToolSpec
from backend.core.contracts.execution import ExecutionPlan

# Import registry directly to avoid circular imports
from backend.core.tools.registry import tool_registry
from backend.core.infrastructure.llm.factory import llm_factory
from backend.core.graph.event_types import (
    ErrorEvent,
    Event,
    EventType,
    FinalEvent,
    TokenEvent,
    ToolCallResultEvent,
    ToolCallStartEvent
)

# Configure logger
logger = logging.getLogger(__name__)


class FlowOrchestrator:
    """
    Enhanced flow orchestrator for the LangGraph agent.
    
    This class provides an orchestrator that supports:
    1. Tool filtering before flow creation
    2. Streaming events during execution
    3. Unified event format for protocol layer
    4. Multiple execution strategies
    5. Integration with LLM-based planning
    """
    
    # Define state structure
    class State(TypedDict):
        messages: list
        conversation_id: OptionalType[str]
        event_callback: OptionalType[Callable[[Event], None]]
    
    def __init__(
        self,
        llm_node: Optional[Callable] = None,
        filter_strategy: Optional[str] = None,
        tool_tags: Optional[List[str]] = None,
        execution_plan: Optional[ExecutionPlan] = None,
        system_message: Optional[str] = None,
        streaming: bool = False
    ):
        """
        Initialize the flow orchestrator.
        
        Args:
            llm_node: Callable that handles LLM interactions (optional, created if not provided)
            filter_strategy: Optional filter strategy name
            tool_tags: Optional tool tags to pre-filter by
            execution_plan: Optional execution plan to use
            system_message: Optional system message for the LLM
            streaming: Whether to enable streaming mode
        """
        # Get filtered tools or tools from execution plan
        if execution_plan:
            # Get tools from execution plan
            tool_names = set()
            for node in execution_plan.tool_chain.nodes:
                tool_names.add(node.tool_invocation.tool_name)
                
            self.tools = []
            for name in tool_names:
                tool = tool_registry.get_tool(name)
                if tool:
                    self.tools.append(tool)
                else:
                    logger.warning(f"Tool not found: {name}")
                    
            logger.info(f"Using {len(self.tools)} tools from execution plan")
            self.execution_plan = execution_plan
        else:
            # Import filter_manager here to avoid circular imports
            from backend.core.filters.filter_manager import filter_manager
            
            # Get filtered tools
            self.tools = filter_manager.filter_tools(
                strategy_name=filter_strategy,
                tags=tool_tags
            )
            self.execution_plan = None
            logger.info(f"Using {len(self.tools)} tools from filter strategy")
        
        # Convert to LangChain tools
        self.langchain_tools = []
        for tool in self.tools:
            if hasattr(tool, 'to_langchain_tool'):
                self.langchain_tools.append(tool.to_langchain_tool())
        
        # Create tool node
        self.tool_node = ToolNode(self.langchain_tools)
        
        # Use provided LLM node or create default
        self.llm_node = llm_node or self._create_default_llm_node()
        
        # Store system message
        self.system_message = system_message or "You are a helpful assistant that can use tools to accomplish tasks."
        
        # Configure streaming
        self.streaming = streaming
        
        # Build the graph
        self.graph = self._build_graph()
        
        logger.info(f"Initialized FlowOrchestrator with {len(self.tools)} tools, streaming={streaming}")
    
    def _create_default_llm_node(self) -> Callable:
        """Create a default LLM node using the LLM factory."""
        # Get the appropriate LLM adapter based on streaming setting
        if self.streaming:
            llm_adapter = llm_factory.get_streaming_adapter()
        else:
            llm_adapter = llm_factory.get_default_adapter()
            
        # Return a callable that uses the adapter
        async def default_llm_node(state: Dict[str, Any]) -> Dict[str, Any]:
            # Process messages from state
            messages = state.get("messages", [])
            
            # Add system message if not present
            if not any(msg.get("role") == "system" for msg in messages):
                system_msg = {"role": "system", "content": self.system_message}
                messages = [system_msg] + messages
                
            # Convert to FakerMessage format
            faker_messages = []
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                faker_messages.append(FakerMessage(role=role, content=content))
                
            # Get response from LLM
            response = await llm_adapter.chat(faker_messages)
            
            # Convert back to LangGraph format
            response_dict = {"role": "assistant", "content": response.content}
            
            # Update messages in state
            return {"messages": messages + [response_dict]}
            
        return default_llm_node
    
    def _build_graph(self) -> StateGraph:
        """Build the agent graph."""
        if self.execution_plan:
            # Build graph based on execution plan
            return self._build_graph_from_plan()
        else:
            # Build default graph
            return self._build_default_graph()
    
    def _build_default_graph(self) -> StateGraph:
        """Build the default agent graph."""
        graph = StateGraph(self.State)
        
        # Add nodes
        graph.add_node("llm", self._call_llm)
        graph.add_node("action", self._execute_tools)
        
        # Add edges
        graph.add_edge("action", "llm")
        
        # Set conditional edges from LLM to either action or end
        graph.add_conditional_edges(
            "llm",
            self._should_continue,
            {
                "continue": "action",
                "end": END
            }
        )
        
        # Set entry point
        graph.set_entry_point("llm")
        
        return graph.compile()
        
    def _build_graph_from_plan(self) -> StateGraph:
        """Build a graph based on the execution plan."""
        # For now, we'll use the default graph
        # In a more advanced implementation, we would build a custom graph
        # based on the execution plan's tool chain
        return self._build_default_graph()
    
    async def _call_llm(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Call the LLM with the current state."""
        try:
            # Convert messages to dict format for LangGraph compatibility
            if isinstance(state, dict) and "messages" in state:
                # Convert message objects to dicts if needed
                converted_messages = []
                for msg in state["messages"]:
                    if hasattr(msg, 'dict') and callable(getattr(msg, 'dict')):
                        # If it's a message object with a dict method, use it
                        converted_messages.append(msg.dict())
                    elif hasattr(msg, '__dict__'):
                        # If it's an object with __dict__, convert manually
                        msg_dict = {
                            "content": getattr(msg, 'content', ''),
                            "role": getattr(msg, 'role', 'user')  # Default to user if no role
                        }
                        # Add any additional attributes
                        for key, value in msg.__dict__.items():
                            if key not in msg_dict:
                                msg_dict[key] = value
                        converted_messages.append(msg_dict)
                    elif isinstance(msg, dict):
                        # If it's already a dict, keep as is
                        converted_messages.append(msg)
                    else:
                        # Convert to dict with basic properties
                        converted_messages.append({
                            "content": str(msg),
                            "role": "user"
                        })
                # Create a new state with converted messages
                converted_state = state.copy()
                converted_state["messages"] = converted_messages
                result = await self.llm_node(converted_state)
            else:
                result = await self.llm_node(state)
            return result
        except Exception as e:
            logger.error(f"Error in LLM call: {e}")
            # Return an empty result to avoid breaking the flow
            return {"messages": state.get("messages", []) if isinstance(state, dict) else []}
    
    async def _execute_tools(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tools based on LLM output."""
        messages = state["messages"]
        last_message = messages[-1]
        
        if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
            return {"messages": messages}
        
        results = []
        for tool_call in last_message.tool_calls:
            try:
                # Capture start time for performance monitoring
                start_time = time.time()
                
                # Generate tool start event
                if "event_callback" in state and state["event_callback"]:
                    await state["event_callback"](ToolCallStartEvent(
                        tool_name=tool_call["name"],
                        tool_args=tool_call["args"],
                        tool_call_id=tool_call["id"]
                    ))
                
                # Execute the tool
                tool_message = await self.tool_node.ainvoke([ToolMessage(
                    content="",  # Content is not used for tool invocation
                    tool_call_id=tool_call["id"],
                    name=tool_call["name"],
                    args=tool_call["args"]
                )])
                result = tool_message[0].content if isinstance(tool_message, list) else tool_message.content
                
                # Calculate execution time
                execution_time = time.time() - start_time
                
                # Generate tool result event
                if "event_callback" in state and state["event_callback"]:
                    await state["event_callback"](ToolCallResultEvent(
                        tool_name=tool_call["name"],
                        tool_call_id=tool_call["id"],
                        result=result,
                        metadata={"execution_time": execution_time}
                    ))
                
                # Create tool message
                tool_message = ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call["id"],
                    name=tool_call["name"]
                )
                results.append(tool_message)
                
            except Exception as e:
                logger.error(f"Error executing tool '{tool_call['name']}': {e}")
                
                # Generate error event
                if "event_callback" in state and state["event_callback"]:
                    await state["event_callback"](ToolCallResultEvent(
                        tool_name=tool_call["name"],
                        tool_call_id=tool_call["id"],
                        result=None,
                        error=str(e)
                    ))
                
                # Create error tool message
                error_message = ToolMessage(
                    content=f"Error: {str(e)}",
                    tool_call_id=tool_call["id"],
                    name=tool_call["name"]
                )
                results.append(error_message)
        
        # Add the results to the messages
        return {"messages": messages + results}
    
    def _should_continue(self, state: Dict[str, Any]) -> str:
        """Determine if we should continue or end."""
        messages = state["messages"]
        last_message = messages[-1]
        
        # If the last message is an AIMessage with tool calls, continue
        if isinstance(last_message, AIMessage) and last_message.tool_calls:
            return "continue"
        else:
            return "end"
    
    async def invoke(
        self,
        input_message: str,
        conversation_id: Optional[str] = None,
        event_callback: Optional[Callable[[Event], None]] = None
    ) -> Dict[str, Any]:
        """
        Invoke the agent graph with an input message.
        
        Args:
            input_message: The user's input message
            conversation_id: Optional conversation ID for context
            event_callback: Optional callback for events
            
        Returns:
            The final result from the agent
        """
        try:
            # Convert input to HumanMessage
            human_message = HumanMessage(content=input_message)
            
            # Create initial state
            state = {"messages": [human_message]}
            
            # Add conversation ID and event callback to state if provided
            if conversation_id:
                state["conversation_id"] = conversation_id
                
            if event_callback:
                state["event_callback"] = event_callback
            
            # Invoke the graph with complete state
            result = await self.graph.ainvoke(state)
            
            # Generate final event
            if event_callback:
                messages = result["messages"]
                final_message = messages[-1] if messages else None
                
                # Handle dict or object with content attribute
                if final_message:
                    if isinstance(final_message, dict) and "content" in final_message:
                        final_response = final_message["content"]
                    elif hasattr(final_message, "content"):
                        final_response = final_message.content
                    else:
                        final_response = str(final_message)
                else:
                    final_response = "No response"
                
                # Handle tool message conversion safely
                actions = []
                for msg in messages:
                    if isinstance(msg, ToolMessage):
                        if hasattr(msg, "dict") and callable(getattr(msg, "dict")):
                            actions.append(msg.dict())
                        elif isinstance(msg, dict):
                            actions.append(msg)
                
                await event_callback(FinalEvent(
                    response=final_response,
                    actions=actions
                ))
            
            return result
            
        except Exception as e:
            logger.error(f"Error in flow orchestrator: {e}")
            stack_trace = traceback.format_exc()
            
            # Generate error event
            if event_callback:
                await event_callback(ErrorEvent(
                    error=str(e),
                    stack_trace=stack_trace
                ))
            
            return {
                "error": str(e),
                "stack_trace": stack_trace
            }
    
    async def stream_invoke(
        self,
        input_message: str,
        conversation_id: Optional[str] = None
    ) -> AsyncGenerator[Event, None]:
        """
        Stream the agent execution as a series of events.
        
        Args:
            input_message: The user's input message
            conversation_id: Optional conversation ID for context
            
        Yields:
            Event objects representing the execution flow
        """
        # Create an async queue for events
        event_queue = asyncio.Queue()
        
        # Define the event callback
        async def event_callback(event: Event):
            await event_queue.put(event)
        
        # Start the execution in a background task
        execution_task = asyncio.create_task(
            self.invoke(input_message, conversation_id, event_callback)
        )
        
        try:
            # Yield events as they are generated
            while True:
                # Wait for the next event or execution completion
                done, pending = await asyncio.wait(
                    [
                        asyncio.create_task(event_queue.get()),
                        execution_task
                    ],
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                # Check if the execution is complete
                if execution_task in done:
                    # Get the result or exception
                    try:
                        result = execution_task.result()
                        # Add a final event if not already added
                        if not any(event.type == EventType.FINAL for event in done):
                            messages = result.get("messages", [])
                            final_message = messages[-1] if messages else None
                            
                            # Handle dict or object with content attribute
                            if final_message:
                                if isinstance(final_message, dict) and "content" in final_message:
                                    final_response = final_message["content"]
                                elif hasattr(final_message, "content"):
                                    final_response = final_message.content
                                else:
                                    final_response = str(final_message)
                            else:
                                final_response = "No response"
                            
                            # Handle tool message conversion safely
                            actions = []
                            for msg in messages:
                                if isinstance(msg, ToolMessage):
                                    if hasattr(msg, "dict") and callable(getattr(msg, "dict")):
                                        actions.append(msg.dict())
                                    elif isinstance(msg, dict):
                                        actions.append(msg)
                            
                            yield FinalEvent(
                                response=final_response,
                                actions=actions
                            )
                    except Exception as e:
                        # Add an error event
                        yield ErrorEvent(
                            error=str(e),
                            stack_trace=traceback.format_exc()
                        )
                    
                    # Break the loop when execution is complete
                    break
                
                # Get the event from the queue
                for task in done:
                    if task != execution_task:
                        event = task.result()
                        yield event
            
        finally:
            # Clean up the execution task if it's still running
            if not execution_task.done():
                execution_task.cancel()
                try:
                    await execution_task
                except asyncio.CancelledError:
                    pass