"""
Agent graph implementation using LangGraph.
"""
from typing import Any, Dict, List, Optional, Union

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.language_models import BaseChatModel
from langgraph.graph import END, StateGraph
from typing import TypedDict
from langgraph.prebuilt import ToolNode

from backend.core.llm import get_chat_model
from backend.core.tools.registry import tool_registry
from backend.core.utils.logging import get_logger
from backend.core.utils.message_formatter import message_formatter

# Configure logger
logger = get_logger(__name__)


# Define state schema for the graph
class AgentState(dict):
    """State schema for the agent graph."""
    messages: List[Any]  # Messages in the conversation


# Define context schema for runtime data
class AgentContext(dict):
    """Runtime context for the agent graph."""
    conversation_id: Optional[str] = None  # Optional conversation ID for context


class AgentGraph:
    """Agent graph for orchestrating tool execution using LangGraph."""
    
    def __init__(self, llm_model: Optional[BaseChatModel] = None):
        self.llm_model = llm_model or get_chat_model()
        self.tools = tool_registry.get_all_langchain_tools()
        self.tool_node = ToolNode(self.tools)
        self.graph = self._build_graph()
    
    # Define state structure
    class State(TypedDict):
        messages: list
    
    def _build_graph(self) -> StateGraph:
        """Build the agent graph."""
        # Create a state graph with proper state schema
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
            context: Runtime context with conversation ID
            
        Returns:
            Updated state with LLM response added to messages
        """
        logger.info("Calling LLM with state")
        
        try:
            # Extract messages from state
            messages = state.get("messages", [])
            
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
            
            # Return a dict with the updated messages list
            return {"messages": messages + [ai_message]}
            
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            # Fallback to simple response
            error_msg = f"I received your query, but I'm currently experiencing technical difficulties: {str(e)}"
            error_message = AIMessage(content=error_msg)
            return {"messages": messages + [error_message]}
    
    async def _execute_tools(self, state: AgentState, context: AgentContext) -> Dict[str, List[Any]]:
        """Execute tools based on LLM output.
        
        Args:
            state: The current agent state containing messages
            context: Runtime context with conversation ID
            
        Returns:
            Updated state with tool results added to messages
        """
        # Extract messages from state
        messages = state.get("messages", [])
        
        if not messages:
            return {"messages": messages}
            
        # Get the last message (LLM response)
        last_message = messages[-1]
        
        # Convert to LangChain format if needed
        if not isinstance(last_message, (HumanMessage, AIMessage, ToolMessage)):
            last_message = message_formatter.to_langchain_format(last_message)
        
        # Check if there are any tool calls to execute
        if not isinstance(last_message, AIMessage) or not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
            return {"messages": messages}  # Return original messages if no tool calls
        
        # Execute tool calls and collect results
        results = []
        for tool_call in last_message.tool_calls:
            logger.info("Executing tool: %s with args: %s", 
                       tool_call["name"], tool_call["args"])
            
            # Extract tool information
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            # Find the matching tool
            matching_tool = None
            for tool in self.tools:
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
            
            # Create ToolMessage object for the graph
            tool_message_obj = ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"],
                name=tool_call["name"]
            )
            results.append(tool_message_obj)
        
        # Return updated state with tool results added to messages
        return {"messages": messages + results}
    
    def _should_continue(self, state: AgentState, context: AgentContext) -> str:
        """Determine if we should continue or end based on the state.
        
        Args:
            state: The current agent state containing messages
            context: Runtime context with conversation ID
            
        Returns:
            'continue' if there are tool calls to execute, 'end' otherwise
        """
        # Extract messages from state
        messages = state.get("messages", [])
        
        if not messages:
            return "end"
            
        # Get the last message
        last_message = messages[-1]
        
        # Convert to LangChain format if needed
        if not isinstance(last_message, (HumanMessage, AIMessage, ToolMessage)):
            last_message = message_formatter.to_langchain_format(last_message)
        
        # Check if there are tool calls to execute
        if isinstance(last_message, AIMessage) and hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "continue"
        else:
            return "end"
    
    async def invoke(self, input_message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Invoke the agent graph with an input message.
        
        Args:
            input_message: The user's input message
            conversation_id: Optional conversation ID for context
            
        Returns:
            The result of the agent's processing
        """
        # Create human message from input
        if isinstance(input_message, str):
            human_message = HumanMessage(content=input_message)
        else:
            # Already a dict format, convert to LangChain format
            human_message = message_formatter.to_langchain_format(input_message)
        
        # Create initial state
        initial_state = {"messages": [human_message]}
        
        # Create context
        context = {}
        if conversation_id:
            context["conversation_id"] = conversation_id
        
        # Invoke the graph with state and context
        result = await self.graph.ainvoke(initial_state, context=context)
        
        return result