"""
Flow orchestrator for the LangGraph agent.

This module provides an enhanced flow orchestrator that supports
streaming events and tool filtering.
"""
import asyncio
import traceback
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Union, TypedDict
from typing_extensions import Annotated

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.language_models import BaseChatModel
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

from backend.core.filters.filter_manager import filter_manager
from backend.core.graph.event_types import (
    ErrorEvent,
    Event,
    EventType,
    FinalEvent,
    TokenEvent,
    ToolCallResultEvent,
    ToolCallStartEvent
)
from backend.core.llm import get_chat_model
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
    """
    
    def __init__(
        self,
        llm_model: Optional[BaseChatModel] = None,
        filter_strategy: Optional[str] = None,
        tool_tags: Optional[List[str]] = None
    ):
        """
        Initialize the flow orchestrator.
        
        Args:
            llm_model: BaseChatModel instance for LLM interactions (or None to use default)
            filter_strategy: Optional filter strategy name
            tool_tags: Optional tool tags to pre-filter by
        """
        # Get filtered tools
        self.tools = filter_manager.filter_tools(
            strategy_name=filter_strategy,
            tags=tool_tags
        )
        
        # Convert to LangChain tools if needed
        self.langchain_tools = []
        for tool in self.tools:
            if hasattr(tool, 'to_langchain_tool'):
                self.langchain_tools.append(tool.to_langchain_tool())
        
        # Set up the LLM model
        self.llm_model = llm_model or get_chat_model()
        
        # Set up tool node
        self.tool_node = ToolNode(self.langchain_tools)
        
        # Build the graph
        self.graph = self._build_graph()
        
        logger.info(f"Initialized FlowOrchestrator with {len(self.tools)} tools and {self.llm_model.__class__.__name__}")

    
    def _build_graph(self) -> StateGraph:
        """Build the agent graph using StateGraph."""
        # Create a state graph with proper state and context schemas
        graph = StateGraph(state_schema=AgentState, context_schema=AgentContext)
        
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
    
    async def _call_llm(self, state: AgentState, context: AgentContext) -> Dict[str, List[Any]]:
        """Call the LLM with the current state and context.
        
        Args:
            state: The current agent state containing messages
            context: Runtime context with conversation ID and callbacks
            
        Returns:
            Updated state with LLM response added to messages
        """
        try:
            # Extract messages from state
            messages = state["messages"]
            
            # Convert messages to LangChain format if needed
            langchain_messages = []
            for msg in messages:
                if isinstance(msg, (HumanMessage, AIMessage, ToolMessage)):
                    # Already in LangChain format
                    langchain_messages.append(msg)
                else:
                    # Convert to LangChain format
                    langchain_messages.append(message_formatter.to_langchain_format(msg))
            
            # Call the LLM model
            chat_result = await self.llm_model._agenerate(langchain_messages)
            
            # Get the generated message
            ai_message = chat_result.generations[0].message
            
            # Create result in the format expected by the graph
            result = {"messages": messages + [ai_message]}
            
            # Handle streaming tokens if an event callback is provided
            if context.get("event_callback") and hasattr(ai_message, "content"):
                # Send token events for streaming UI updates
                await context["event_callback"](TokenEvent(token=ai_message.content, is_partial=False))
                
            return result
        except Exception as e:
            logger.error(f"Error in LLM call: {e}")
            # Return an empty result to avoid breaking the flow
            return {"messages": state["messages"]}
    
    async def _execute_tools(self, state: AgentState, context: AgentContext) -> Dict[str, List[Any]]:
        """Execute tools based on LLM output.
        
        Args:
            state: The current agent state containing messages
            context: Runtime context with conversation ID and callbacks
            
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
        
        # Process tool calls and collect results
        results = []
        for tool_call in last_message.tool_calls:
            try:
                # Extract tool information
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_call_id = tool_call["id"]
                
                # Send tool start event if callback is provided
                if context.get("event_callback"):
                    await context["event_callback"](ToolCallStartEvent(
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
                
                # Send tool result event if callback is provided
                if context.get("event_callback"):
                    await context["event_callback"](ToolCallResultEvent(
                        tool_name=tool_name,
                        tool_call_id=tool_call_id,
                        result=result_str
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
                
                # Send error event if callback is provided
                if context.get("event_callback"):
                    await context["event_callback"](ToolCallResultEvent(
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
    
    def _should_continue(self, state: AgentState, context: AgentContext) -> str:
        """Determine if the graph should continue or end based on the state.
        
        Args:
            state: The current agent state containing messages
            context: Runtime context with conversation ID and callbacks
            
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
            if event_callback:
                context["event_callback"] = event_callback
            
            # Invoke the graph with proper state and context
            result = await self.graph.ainvoke(initial_state, context=context)
            
            # Generate final event if callback is provided
            if event_callback and "messages" in result:
                messages = result["messages"]
                final_message = messages[-1] if messages else None
                final_response = final_message.content if hasattr(final_message, "content") else "No response"
                
                # Convert ToolMessage objects to dicts for the event
                tool_actions = []
                for msg in messages:
                    if isinstance(msg, ToolMessage):
                        if hasattr(msg, "dict"):
                            tool_actions.append(msg.dict())
                        elif hasattr(msg, "model_dump"):
                            # For newer Pydantic versions
                            tool_actions.append(msg.model_dump())
                        else:
                            # Fallback to manual conversion
                            tool_actions.append({
                                "content": msg.content,
                                "tool_call_id": msg.tool_call_id,
                                "name": msg.name
                            })
                
                await event_callback(FinalEvent(
                    response=final_response,
                    actions=tool_actions
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
                        if not any(event.type == EventType.FINAL for event in done):
                            # Extract messages and format final response
                            messages = result.get("messages", [])
                            final_message = messages[-1] if messages else None
                            
                            # Handle different types of final messages
                            if hasattr(final_message, "content"):
                                final_response = final_message.content
                            elif isinstance(final_message, dict) and "content" in final_message:
                                final_response = final_message["content"]
                            else:
                                final_response = "No response"
                            
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
                                actions=tool_actions
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