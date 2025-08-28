"""
Main agent implementation using LangGraph.
"""
import logging
from typing import Any, Dict

from backend.core.graph.agent_graph import AgentGraph

# Configure logger
logger = logging.getLogger(__name__)


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
        
        try:
            # Invoke the graph
            result = await self.graph.invoke(query)
            
            # Extract the final message
            messages = result["messages"]
            final_message = messages[-1] if messages else None
            
            return {
                "status": "success",
                "data": {
                    "query": query,
                    "result": final_message.content if final_message else "No response",
                    "actions": [msg.dict() for msg in messages]
                }
            }
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "status": "error",
                "error": str(e)
            }