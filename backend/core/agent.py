"""
Main agent implementation using LangGraph.
"""
from typing import Any, Dict

from backend.core.graph.agent_graph import AgentGraph
from backend.core.utils.logging import get_logger
from backend.core.utils.message_formatter import message_formatter
from backend.core.utils.weather_utils import is_weather_query, get_weather_response

# Configure logger
logger = get_logger(__name__)


class Agent:
    """Main agent class using LangGraph for orchestration."""
    
    def __init__(self):
        self.graph = AgentGraph()
        logger.info("Initialized Agent with LangGraph")
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a user query through the agent graph.
        
        Args:
            query: The user's query
            
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
        
        # Check if this is a weather query using centralized detection
        if is_weather_query(query):
            # Get weather response using centralized utility
            return await get_weather_response(query)
            
        # 调用LangGraph进行处理
        try:
            # 使用正确的消息格式调用图结构
            logger.info(f"query -> {query}")
            result = await self.graph.invoke(query)
            
            # 从结果中提取最后一条消息
            if isinstance(result, dict) and "messages" in result:
                messages = result["messages"]
                final_message = messages[-1] if messages else None
                final_content = final_message["content"] if isinstance(final_message, dict) and "content" in final_message else "No response"
                
                # 提取工具调用结果
                tool_messages = []
                for msg in messages:
                    if isinstance(msg, dict) and msg.get("role") == "tool":
                        tool_messages.append(msg)
                    
                return {
                    "status": "success",
                    "data": {
                        "query": query,
                        "result": final_content,
                        "actions": tool_messages
                    }
                }
            
            # 如果结果没有预期的格式，返回通用响应
            return {
                "status": "success",
                "data": {
                    "query": query,
                    "result": "I processed your query but couldn't generate a detailed response.",
                    "actions": []
                }
            }
            
        except Exception as e:
            logger.error(f"Error in graph processing: {e}")
            # 返回错误响应
            return {
                "status": "error",
                "data": {
                    "query": query,
                    "result": "I can only process weather queries at this time. Please try asking about the weather.",
                    "actions": []
                },
                "error": {
                    "code": "PROCESSING_ERROR",
                    "message": str(e)
                }
            }