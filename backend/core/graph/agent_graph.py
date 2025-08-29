"""
Agent graph implementation using LangGraph.
"""
import logging
from typing import Any, Dict, List

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.graph import END, MessageGraph
from langgraph.prebuilt import ToolNode

from backend.core.tools.registry import tool_registry
from backend.core.assembler.llm_assembler import assembler

# Configure logger
logger = logging.getLogger(__name__)


class AgentGraph:
    """Agent graph for orchestrating tool execution using LangGraph."""
    
    def __init__(self):
        self.tools = tool_registry.get_all_langchain_tools()
        self.tool_node = ToolNode(self.tools)
        self.graph = self._build_graph()
    
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
    
    async def _call_llm(self, state: List[Any]) -> Dict[str, Any]:
        """Call the LLM with the current state."""
        logger.info("Calling LLM with state: %s", state)
        
        # Use the LLM assembler to get a response
        # Handle different state formats
        if isinstance(state, dict):
            messages = state.get("messages", [])
        elif isinstance(state, list):
            messages = state
        else:
            messages = []
        
        # Get the last message content
        if messages:
            last_message = messages[-1]
            query = last_message.content if hasattr(last_message, 'content') else str(last_message)
        else:
            query = "Hello"
        
        try:
            # Use the assembler to get a response
            response = await assembler.get_response(query, messages)
            
            # If the response contains tool calls, convert them to the proper format
            if hasattr(response, 'tool_calls') and response.tool_calls:
                ai_message_dict = {
                    "content": response.content,
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "name": tool_call.name if hasattr(tool_call, 'name') else tool_call["name"],
                            "args": tool_call.arguments if hasattr(tool_call, 'arguments') else tool_call["args"],
                            "id": f"tool_call_{i}"
                        }
                        for i, tool_call in enumerate(response.tool_calls)
                    ]
                }
            else:
                # Simple text response
                ai_message_dict = {
                    "content": response.content if hasattr(response, 'content') else str(response),
                    "role": "assistant"
                }
            
            return {"messages": [ai_message_dict]}
            
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            # Fallback to simple response
            response_text = f"我收到了您的查询。由于技术问题，我目前无法完全处理它。错误: {str(e)}"
            return {"messages": [{"content": response_text, "role": "assistant"}]}
    
    async def _execute_tools(self, state: List[Any]) -> Dict[str, Any]:
        """Execute tools based on LLM output."""
        messages = state["messages"]
        last_message = messages[-1]
        
        if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
            return {"messages": []}
        
        results = []
        for tool_call in last_message.tool_calls:
            logger.info("Executing tool: %s with args: %s", 
                       tool_call["name"], tool_call["args"])
            
            # Execute the tool
            tool_message = await self.tool_node.ainvoke(ToolMessage(
                content="",  # Content is not used for tool invocation
                tool_call_id=tool_call["id"],
                name=tool_call["name"],
                args=tool_call["args"]
            ))
            result = tool_message.content if hasattr(tool_message, 'content') else str(tool_message)
            
            # Create tool message
            tool_message = ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"],
                name=tool_call["name"]
            )
            results.append(tool_message)
        
        return {"messages": results}
    
    def _should_continue(self, state: List[Any]) -> str:
        """Determine if we should continue or end."""
        messages = state["messages"]
        last_message = messages[-1]
        
        # If the last message is an AIMessage with tool calls, continue
        if isinstance(last_message, AIMessage) and last_message.tool_calls:
            return "continue"
        else:
            return "end"
    
    async def invoke(self, input_message: str) -> Dict[str, Any]:
        """Invoke the agent graph with an input message."""
        # Convert input to HumanMessage
        human_message = HumanMessage(content=input_message)
        
        # Invoke the graph
        result = await self.graph.ainvoke({"messages": [human_message]})
        
        return result