"""
Flow orchestrator for the LangGraph agent.

This module provides an enhanced flow orchestrator that supports
streaming events and tool filtering.
"""
import asyncio
import logging
import traceback
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.graph import END, MessageGraph
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

# Configure logger
logger = logging.getLogger(__name__)


class FlowOrchestrator:
    """
    Enhanced flow orchestrator for the LangGraph agent.
    
    This class provides an orchestrator that supports:
    1. Tool filtering before flow creation
    2. Streaming events during execution
    3. Unified event format for protocol layer
    """
    
    # Class variable to store additional fields for current execution
    _current_additional_fields = {}
    
    def __init__(
        self,
        llm_node: Callable,
        filter_strategy: Optional[str] = None,
        tool_tags: Optional[List[str]] = None
    ):
        """
        Initialize the flow orchestrator.
        
        Args:
            llm_node: Callable that handles LLM interactions
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
        
        self.tool_node = ToolNode(self.langchain_tools)
        self.llm_node = llm_node
        self.graph = self._build_graph()
        
        logger.info(f"Initialized FlowOrchestrator with {len(self.tools)} tools")
    
    def _build_graph(self) -> MessageGraph:
        """Build the agent graph."""
        graph = MessageGraph()
        
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
                # Generate tool start event
                if "event_callback" in FlowOrchestrator._current_additional_fields:
                    await FlowOrchestrator._current_additional_fields["event_callback"](ToolCallStartEvent(
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
                
                # Generate tool result event
                if "event_callback" in FlowOrchestrator._current_additional_fields:
                    await FlowOrchestrator._current_additional_fields["event_callback"](ToolCallResultEvent(
                        tool_name=tool_call["name"],
                        tool_call_id=tool_call["id"],
                        result=result
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
                if "event_callback" in FlowOrchestrator._current_additional_fields:
                    await FlowOrchestrator._current_additional_fields["event_callback"](ToolCallResultEvent(
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
            
            # Store additional fields in class variable
            FlowOrchestrator._current_additional_fields = {}
            
            # Add conversation ID if provided
            if conversation_id:
                FlowOrchestrator._current_additional_fields["conversation_id"] = conversation_id
                
            # Add event callback if provided
            if event_callback:
                FlowOrchestrator._current_additional_fields["event_callback"] = event_callback
            
            # Invoke the graph with only the messages
            result = await self.graph.ainvoke(state)
            
            # Add the additional fields back to the result for use in callbacks
            result.update(FlowOrchestrator._current_additional_fields)
            
            # Clear the class variable
            FlowOrchestrator._current_additional_fields = {}
            
            # Generate final event
            if event_callback:
                messages = result["messages"]
                final_message = messages[-1] if messages else None
                final_response = final_message.content if final_message else "No response"
                
                await event_callback(FinalEvent(
                    response=final_response,
                    actions=[msg.dict() for msg in messages if isinstance(msg, ToolMessage)]
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
                            final_response = final_message.content if final_message else "No response"
                            
                            yield FinalEvent(
                                response=final_response,
                                actions=[msg.dict() for msg in messages if isinstance(msg, ToolMessage)]
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