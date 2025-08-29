"""
Agent graph implementation using LangGraph.
"""
import logging
from typing import Any, Dict, List

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.graph import END, MessageGraph
from langgraph.prebuilt import ToolNode

from backend.core.tools.registry import tool_registry

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
        # In a real implementation, this would call an actual LLM
        # For now, we'll simulate a response
        logger.info("Calling LLM with state: %s", state)
        
        # Simple simulation - in reality, this would be an LLM call
        # We'll just return a predefined response for demonstration
        response = AIMessage(content="Calling weather tool", tool_calls=[
            {
                "name": "weather_query",
                "args": {"city": "Beijing"},
                "id": "tool_call_1"
            }
        ])
        
        return {"messages": [response]}
    
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
            tool_message = await self.tool_node.ainvoke([ToolMessage(
                content="",  # Content is not used for tool invocation
                tool_call_id=tool_call["id"],
                name=tool_call["name"],
                args=tool_call["args"]
            )])
            result = tool_message[0].content if isinstance(tool_message, list) else tool_message.content
            
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