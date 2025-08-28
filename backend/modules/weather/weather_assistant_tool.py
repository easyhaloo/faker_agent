"""
Weather assistant tool that can be used by the agent.
"""
import logging
from typing import Any, Dict

from backend.core.registry.base_registry import BaseTool, registry
from backend.modules.weather.weather_assistant import weather_assistant

# Configure logger
logger = logging.getLogger(__name__)


class WeatherAssistantTool(BaseTool):
    """Tool that provides natural language weather information."""
    
    name = "weather_assistant"
    description = "Get weather information by asking questions in natural language"
    tags = ["weather", "assistant", "natural_language"]
    priority = 20
    parameters = [
        {
            "name": "query",
            "type": "string",
            "description": "Natural language question about weather, e.g., 'What's the weather like in Beijing?'",
            "required": True
        }
    ]
    
    async def run(self, query: str) -> Dict[str, Any]:
        """
        Process a natural language query about weather.
        
        Args:
            query: The natural language weather query
            
        Returns:
            Weather information with a natural language response
        """
        logger.info(f"Weather assistant processing query: {query}")
        
        try:
            # Process the query with the weather assistant
            result = await weather_assistant.process_query(query)
            return result
            
        except Exception as e:
            logger.error(f"Error in weather assistant tool: {e}")
            raise ValueError(f"Failed to process weather query: {str(e)}")


# Register the weather assistant tool
registry.register_tool(WeatherAssistantTool)