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
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Set, Union, TypedDict
from typing_extensions import Annotated

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.language_models import BaseChatModel
from langgraph.graph import END, StateGraph
from typing import Optional as OptionalType
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
from backend.core.infrastructure.llm.chat_model import get_chat_model
from backend.core.utils.logging import get_logger
from backend.core.utils.message_formatter import message_formatter

# Configure logger
logger = get_logger(__name__)

# Define state schema for the graph
class AgentState(TypedDict):
    """State schema for the agent graph."""
    messages: List[Any]  # Messages in the conversation

# Define context schema for runtime data
class AgentContext(TypedDict):
    """Runtime context for the agent graph."""
    conversation_id: Optional[str]  # Optional conversation ID for context
    event_callback: Optional[Callable[[Event], Any]]  # Event callback for streaming


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
        llm_model: Optional[BaseChatModel] = None,
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
            llm_model: BaseChatModel instance for LLM interactions (or None to use default)
            filter_strategy: Optional filter strategy name
            tool_tags: Optional tool tags to pre-filter by
            execution_plan: Optional execution plan to use
            system_message: Optional system message for the LLM
            streaming: Whether to enable streaming mode
        """
        # Configure streaming as early as possible to avoid attribute access before assignment
        self.streaming = streaming
        
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
        
        # Store system message
        self.system_message = system_message or "You are a helpful assistant that can use tools to accomplish tasks."
        
        # Set up the LLM model if provided
        self.llm_model = llm_model or get_chat_model()
        
        # Use provided LLM node or create default
        self.llm_node = llm_node or self._create_default_llm_node()
        
        # Build the graph
        self.graph = self._build_graph()
        
        logger.info(f"Initialized FlowOrchestrator with {len(self.tools)} tools, streaming={self.streaming}")
    
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
        graph.add_node("llm", self.llm_node)
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
    
    # Note: Previously this class defined an internal _call_llm that relied on private
    # LLM APIs and a context parameter. The graph now uses self.llm_node created
    # via the factory adapter, which avoids private API usage and matches the
    # expected node signature for LangGraph.
        
    async def _execute_tools(self, state: AgentState) -> Dict[str, List[Any]]:
        """Execute tools based on LLM output.
        
        Args:
            state: The current agent state containing messages
            
        Returns:
            Updated state with tool results added to messages
        """
        messages = state["messages"]
        if not messages:
            return {"messages": messages}
            
        # Get the last message (LLM response)
        last_message = messages[-1]
        
        # Convert dictionary message to LangChain format if needed
        if isinstance(last_message, dict) and "role" in last_message and last_message["role"] == "assistant":
            last_message = message_formatter.to_langchain_format(last_message)
        
        # Check if there are any tool calls to execute
        if not isinstance(last_message, AIMessage) or not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
            return {"messages": messages}
        
        # Access optional event callback from state
        event_callback = state.get("event_callback") if isinstance(state, dict) else None
        
        # Process tool calls and collect results
        results = []
        for tool_call in last_message.tool_calls:
            try:
                # Extract tool information
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_call_id = tool_call["id"]
                
                # Capture start time for performance monitoring
                start_time = time.time()
                
                # Generate tool start event
                if event_callback:
                    await event_callback(ToolCallStartEvent(
                        tool_name=tool_name,
                        tool_args=tool_args,
                        tool_call_id=tool_call_id
                    ))
                
                # Find the matching tool
                matching_tool = None
                for tool in self.langchain_tools:
                    if tool.name == tool_name:
                        matching_tool = tool
                        break
                
                # Execute the tool
                if matching_tool:
                    try:
                        result = await matching_tool.ainvoke(tool_args)
                    except Exception as e:
                        result = f"Error executing tool: {str(e)}"
                else:
                    result = f"Tool not found: {tool_name}"
                
                # Convert result to string for consistency
                result_str = str(result)
                
                # Calculate execution time
                execution_time = time.time() - start_time
                
                # Generate tool result event
                if event_callback:
                    await event_callback(ToolCallResultEvent(
                        tool_name=tool_name,
                        tool_call_id=tool_call_id,
                        result=result_str,
                        metadata={"execution_time": execution_time}
                    ))
                
                # Create ToolMessage object for the graph
                tool_message_obj = ToolMessage(
                    content=result_str,
                    tool_call_id=tool_call_id,
                    name=tool_name
                )
                results.append(tool_message_obj)
                
            except Exception as e:
                error_msg = f"Error executing tool '{tool_name}': {e}"
                logger.error(error_msg)
                
                # Generate error event
                if event_callback:
                    await event_callback(ToolCallResultEvent(
                        tool_name=tool_call["name"],
                        tool_call_id=tool_call["id"],
                        result=None,
                        error=str(e)
                    ))
                
                # Create error ToolMessage for the graph
                error_message_obj = ToolMessage(
                    content=f"Error: {str(e)}",
                    tool_call_id=tool_call["id"],
                    name=tool_call["name"]
                )
                results.append(error_message_obj)
        
        # Return updated state with tool results added to messages
        return {"messages": messages + results}
        
    def _should_continue(self, state: AgentState) -> str:
        """Determine if the graph should continue or end based on the state.
        
        Args:
            state: The current agent state containing messages
            
        Returns:
            'continue' if there are tool calls to execute, 'end' otherwise
        """
        messages = state["messages"]
        if not messages:
            return "end"
            
        # Get the last message
        last_message = messages[-1]
        
        # Convert dictionary message to LangChain format if needed
        if isinstance(last_message, dict) and "role" in last_message and last_message["role"] == "assistant":
            last_message = message_formatter.to_langchain_format(last_message)
        
        # Check if there are tool calls to execute
        if isinstance(last_message, AIMessage) and hasattr(last_message, 'tool_calls') and last_message.tool_calls:
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
            # Create the human message in standard format
            human_dict = message_formatter.to_dict_format({"role": "user", "content": input_message})
            
            # Create initial state for the graph
            initial_state = {"messages": [human_dict]}
            
            # Create context with conversation ID and event callback
            context = {}
            if conversation_id:
                context["conversation_id"] = conversation_id
                initial_state["conversation_id"] = conversation_id
            if event_callback:
                context["event_callback"] = event_callback
                initial_state["event_callback"] = event_callback
            
            # Invoke the graph
            result = await self.graph.ainvoke(initial_state)
            
            # Generate final event if callback is provided
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
                        elif hasattr(msg, "model_dump"):
                            # For newer Pydantic versions
                            actions.append(msg.model_dump())
                        elif isinstance(msg, dict):
                            actions.append(msg)
                        else:
                            # Fallback to manual conversion
                            actions.append({
                                "content": msg.content,
                                "tool_call_id": msg.tool_call_id,
                                "name": msg.name
                            })
                
                await event_callback(FinalEvent(
                    response=final_response,
                    actions=actions
                ))
            
            # Add metadata to result for the caller
            result_with_metadata = dict(result)
            if conversation_id:
                result_with_metadata["conversation_id"] = conversation_id
            
            return result_with_metadata
            
        except Exception as e:
            logger.error(f"Error in flow orchestrator: {e}")
            stack_trace = traceback.format_exc()
            
            # Generate error event if callback is provided
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
        
        # Define the event callback that adds events to the queue
        async def event_callback(event: Event):
            await event_queue.put(event)
        
        # Start the execution in a background task with proper context
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
                        # Check if we need to send a final event
                        if not any(task != execution_task and isinstance(task.result(), Event) and task.result().type == EventType.FINAL for task in done):
                            # Extract messages and format final response
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
                                # Import here to avoid circular imports
                                from backend.core.utils.weather_utils import is_weather_query
                                
                                # Provide a more helpful default response for weather queries
                                messages_str = str(messages)
                                if is_weather_query(messages_str):
                                    final_response = "请稍等，我来为您查询天气信息。"
                                else:
                                    final_response = "请稍等，我正在处理您的请求。"
                            
                            # Handle tool message conversion safely
                            actions = []
                            for msg in messages:
                                if isinstance(msg, ToolMessage):
                                    if hasattr(msg, "dict") and callable(getattr(msg, "dict")):
                                        actions.append(msg.dict())
                                    elif hasattr(msg, "model_dump"):
                                        actions.append(msg.model_dump())
                                    elif isinstance(msg, dict):
                                        actions.append(msg)
                            
                            # Handle different types of final messages
                            if hasattr(final_message, "content"):
                                final_response = final_message.content
                            elif isinstance(final_message, dict) and "content" in final_message:
                                final_response = final_message["content"]
                            else:
                                # Import here to avoid circular imports
                                from backend.core.utils.weather_utils import is_weather_query
                                
                                # Provide a more helpful default response for weather queries
                                messages_str = str(messages)
                                if is_weather_query(messages_str):
                                    final_response = "请稍等，我来为您查询天气信息。"
                                else:
                                    final_response = "请稍等，我正在处理您的请求。"
                            
                            # Format tool actions safely
                            tool_actions = []
                            for msg in messages:
                                if isinstance(msg, ToolMessage):
                                    if hasattr(msg, "dict"):
                                        tool_actions.append(msg.dict())
                                    elif hasattr(msg, "model_dump"):
                                        tool_actions.append(msg.model_dump())
                                    else:
                                        # Manual conversion
                                        tool_actions.append({
                                            "content": msg.content,
                                            "tool_call_id": msg.tool_call_id,
                                            "name": msg.name
                                        })
                            
                            # Yield the final event
                            yield FinalEvent(
                                response=final_response,
                                actions=actions
                            )
                    except Exception as e:
                        # Yield an error event on exception
                        error_msg = f"Error in stream_invoke: {str(e)}"
                        logger.error(error_msg)
                        yield ErrorEvent(
                            error=error_msg,
                            stack_trace=traceback.format_exc()
                        )
                    
                    # Break the loop when execution is complete
                    break
                
                # Process and yield events from the queue
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