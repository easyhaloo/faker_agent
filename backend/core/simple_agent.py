"""
Simple agent implementation without LangGraph dependency.
"""
import logging
from typing import Any, Dict

# Configure logger
logger = logging.getLogger(__name__)


class SimpleAgent:
    """Simple agent class without LangGraph dependency."""
    
    def __init__(self):
        logger.info("Initialized SimpleAgent")
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a user query with a simple response.
        
        Args:
            query: The user's query
            
        Returns:
            The final result from the agent
        """
        logger.info(f"Processing query: {query}")
        
        try:
            # Simple response for now
            response = f"I received your query: '{query}'. This is a simple agent response."
            
            return {
                "status": "success",
                "data": {
                    "query": query,
                    "result": response,
                    "actions": []
                }
            }
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "status": "error",
                "error": str(e)
            }