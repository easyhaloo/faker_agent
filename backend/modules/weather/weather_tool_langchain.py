"""
Weather query tool for the Faker Agent, implemented with LangChain compatibility.
"""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.core.tools.base import BaseTool, ToolParameter

# Configure logger
logger = logging.getLogger(__name__)


class WeatherTool(BaseTool):
    """Tool for querying weather data, compatible with LangChain."""
    
    name = "weather_query"
    description = "Queries weather information for a specified city"
    
    def get_parameters(self) -> List[ToolParameter]:
        """Get tool parameters."""
        return [
            ToolParameter(
                name="city",
                type="string",
                description="The city name to get weather for",
                required=True
            ),
            ToolParameter(
                name="country",
                type="string",
                description="Optional country code to disambiguate city names",
                required=False
            )
        ]
    
    async def run(self, city: str, country: Optional[str] = None) -> Dict[str, Any]:
        """
        Get weather data for the specified city.
        
        Args:
            city: The city name
            country: Optional country code
            
        Returns:
            Weather data for the city
        """
        logger.info(f"Getting weather for {city}{f', {country}' if country else ''}")
        
        try:
            # In a real implementation, we would call an actual weather API
            # For this demo, we'll return mock data
            return self._get_mock_weather(city, country)
            
        except Exception as e:
            logger.error(f"Error getting weather: {e}")
            raise ValueError(f"Failed to get weather data: {str(e)}")
    
    def _get_mock_weather(self, city: str, country: Optional[str] = None) -> Dict[str, Any]:
        """Get mock weather data for demo purposes."""
        # Get current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Mock data for different cities
        weather_data = {
            "beijing": {
                "city": "Beijing",
                "date": current_date,
                "temperature": {
                    "current": "28°C",
                    "min": "25°C",
                    "max": "32°C"
                },
                "condition": "晴",
                "humidity": "45%",
                "wind": {
                    "direction": "东南风",
                    "speed": "3-4级"
                }
            },
            "shanghai": {
                "city": "Shanghai",
                "date": current_date,
                "temperature": {
                    "current": "26°C",
                    "min": "24°C",
                    "max": "29°C"
                },
                "condition": "多云",
                "humidity": "60%",
                "wind": {
                    "direction": "东风",
                    "speed": "2-3级"
                }
            },
            "new york": {
                "city": "New York",
                "date": current_date,
                "temperature": {
                    "current": "22°C",
                    "min": "18°C",
                    "max": "24°C"
                },
                "condition": "Partly Cloudy",
                "humidity": "55%",
                "wind": {
                    "direction": "SW",
                    "speed": "10 mph"
                }
            },
            "london": {
                "city": "London",
                "date": current_date,
                "temperature": {
                    "current": "18°C",
                    "min": "15°C",
                    "max": "20°C"
                },
                "condition": "Light Rain",
                "humidity": "75%",
                "wind": {
                    "direction": "W",
                    "speed": "15 mph"
                }
            }
        }
        
        # Default data for cities not in our mock database
        default_data = {
            "city": city.capitalize(),
            "date": current_date,
            "temperature": {
                "current": "25°C",
                "min": "20°C",
                "max": "30°C"
            },
            "condition": "Sunny",
            "humidity": "50%",
            "wind": {
                "direction": "N/A",
                "speed": "N/A"
            }
        }
        
        # Return data for the requested city or default
        return weather_data.get(city.lower(), default_data)