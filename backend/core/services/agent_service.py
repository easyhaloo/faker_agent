"""
Agent service for processing user queries using LangGraph.
"""
from typing import Any, Dict, List, Optional
from uuid import UUID

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from backend.core.graph.agent_graph import AgentGraph
from backend.core.tools.registry import tool_registry
from backend.core.utils.logging import get_logger
from backend.core.utils.message_formatter import message_formatter

# Configure logger
logger = get_logger(__name__)


class AgentService:
    """Service for processing user queries using LangGraph."""
    
    def __init__(self):
        """Initialize the agent service with LangGraph."""
        self.graph = AgentGraph()
        
        # Use elegant logging for initialization
        from backend.core.utils.logging import log_initialization
        log_initialization("AgentService", "with LangGraph integration")
    
    async def process_query(
        self, 
        query: str, 
        conversation_id: Optional[UUID] = None,
        context_messages: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Process a user query through the agent graph.
        
        Args:
            query: The user's query
            conversation_id: Optional conversation ID for context
            context_messages: Optional list of context messages
            
        Returns:
            The final result from the agent
        """
        logger.info(f"Processing query: {query}")
        
        # Fix for encoding issues with Chinese characters
        try:
            # Ensure the query is properly decoded
            if isinstance(query, bytes):
                query = query.decode('utf-8')
        except:
            # If decoding fails, use a placeholder
            query = str(query)
        
        # Prepare the input for the graph
        input_data = {
            "query": query,
            "context_messages": context_messages or []
        }
        
        # 调用LangGraph进行处理
        try:
            # 使用正确的消息格式调用图结构
            logger.info(f"query -> {query}")
            result = await self.graph.invoke(query, conversation_id)
            
            # 从结果中提取最后一条消息
            if isinstance(result, dict) and "messages" in result:
                messages = result["messages"]
                final_message = messages[-1] if messages else None
                final_content = final_message.content if hasattr(final_message, 'content') else "No response"
                
                # 提取工具调用结果
                tool_messages = []
                for msg in messages:
                    if hasattr(msg, 'role') and msg.role == "tool":
                        tool_messages.append({
                            "role": msg.role,
                            "content": msg.content,
                            "name": getattr(msg, 'name', None),
                            "tool_call_id": getattr(msg, 'tool_call_id', None)
                        })
                    elif isinstance(msg, ToolMessage):
                        tool_messages.append({
                            "role": "tool",
                            "content": msg.content,
                            "name": getattr(msg, 'name', None),
                            "tool_call_id": getattr(msg, 'tool_call_id', None)
                        })
                    
                return {
                    "status": "success",
                    "data": {
                        "query": query,
                        "result": final_content,
                        "actions": tool_messages,
                        "messages": messages
                    }
                }
            
            # 如果结果没有预期的格式，返回通用响应
            return {
                "status": "success",
                "data": {
                    "query": query,
                    "result": "I processed your query but couldn't generate a detailed response.",
                    "actions": [],
                    "messages": []
                }
            }
            
        except Exception as e:
            logger.error(f"Error in graph processing: {e}")
            # 返回错误响应
            return {
                "status": "error",
                "data": {
                    "query": query,
                    "result": "I encountered an error while processing your query.",
                    "actions": [],
                    "messages": []
                },
                "error": {
                    "code": "PROCESSING_ERROR",
                    "message": str(e)
                }
            }
    
    async def process_query_with_context(
        self, 
        query: str, 
        context_messages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Process a user query with context messages.
        
        Args:
            query: The user's query
            context_messages: List of context messages
            
        Returns:
            The final result from the agent
        """
        logger.info(f"Processing query with context: {query}")
        
        # Convert context messages to LangChain format
        langchain_messages = []
        for msg in context_messages:
            langchain_messages.append(message_formatter.to_langchain_format(msg))
        
        # Add the current query as a human message
        langchain_messages.append(HumanMessage(content=query))
        
        # Create a temporary graph with context
        temp_graph = AgentGraph()
        
        # Create initial state with context
        initial_state = {"messages": langchain_messages}
        
        try:
            # Invoke the graph with state and context
            result = await temp_graph.graph.ainvoke(initial_state)
            
            # Extract the final response
            if isinstance(result, dict) and "messages" in result:
                messages = result["messages"]
                final_message = messages[-1] if messages else None
                final_content = final_message.content if hasattr(final_message, 'content') else "No response"
                
                # Extract tool call results
                tool_messages = []
                for msg in messages:
                    if hasattr(msg, 'role') and msg.role == "tool":
                        tool_messages.append({
                            "role": msg.role,
                            "content": msg.content,
                            "name": getattr(msg, 'name', None),
                            "tool_call_id": getattr(msg, 'tool_call_id', None)
                        })
                    elif isinstance(msg, ToolMessage):
                        tool_messages.append({
                            "role": "tool",
                            "content": msg.content,
                            "name": getattr(msg, 'name', None),
                            "tool_call_id": getattr(msg, 'tool_call_id', None)
                        })
                
                return {
                    "status": "success",
                    "data": {
                        "query": query,
                        "result": final_content,
                        "actions": tool_messages,
                        "context_messages": context_messages,
                        "messages": messages
                    }
                }
            
            return {
                "status": "success",
                "data": {
                    "query": query,
                    "result": "I processed your query but couldn't generate a detailed response.",
                    "actions": [],
                    "context_messages": context_messages,
                    "messages": []
                }
            }
            
        except Exception as e:
            logger.error(f"Error in graph processing with context: {e}")
            return {
                "status": "error",
                "data": {
                    "query": query,
                    "result": "I encountered an error while processing your query with context.",
                    "actions": [],
                    "context_messages": context_messages,
                    "messages": []
                },
                "error": {
                    "code": "CONTEXT_PROCESSING_ERROR",
                    "message": str(e)
                }
            }