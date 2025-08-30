"""
Weather tool for querying weather information.
"""
import logging
import os
from typing import Dict, Any

import aiohttp

from backend.core.tools.base import BaseTool, ToolParameter
from backend.config.settings import settings

# Configure logger
logger = logging.getLogger(__name__)


class WeatherTool(BaseTool):
    """A weather tool that provides weather information for a given city."""
    
    name = "weather"
    description = "Provides current weather information for a specified city"
    tags = ["weather", "data", "forecast"]
    priority = 5
    
    def get_parameters(self):
        return [
            {
                "name": "city",
                "type": "string",
                "description": "Name of the city to get weather information for",
                "required": True
            }
        ]
    
    async def run(self, city: str) -> Dict[str, Any]:
        """
        Get current weather information for a specified city.
        
        Args:
            city: Name of the city to get weather for
            
        Returns:
            Dictionary with weather information or error
        """
        try:
            # Construct the API URL
            api_key = settings.WEATHER_API_KEY
            if not api_key:
                logger.warning("WEATHER_API_KEY is not set in environment variables")
                # Return mock data for demonstration if API key is not available
                return self._get_mock_weather_data(city)
            
            url = f"{settings.WEATHER_API_URL}/weather"
            params = {
                "q": city,
                "appid": api_key,
                "units": "metric"  # Use metric units (Celsius)
            }
            
            # Make API request
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        error_data = await response.text()
                        logger.error(f"Weather API error: {error_data}")
                        return {
                            "error": f"Failed to get weather data: {response.status}",
                            "city": city
                        }
                    
                    data = await response.json()
                    
                    # Extract relevant information
                    return {
                        "city": city,
                        "temperature": data.get("main", {}).get("temp"),
                        "feels_like": data.get("main", {}).get("feels_like"),
                        "humidity": data.get("main", {}).get("humidity"),
                        "pressure": data.get("main", {}).get("pressure"),
                        "condition": data.get("weather", [{}])[0].get("main"),
                        "description": data.get("weather", [{}])[0].get("description"),
                        "wind_speed": data.get("wind", {}).get("speed"),
                        "country": data.get("sys", {}).get("country")
                    }
                    
        except Exception as e:
            logger.error(f"Error getting weather data: {e}")
            # Return mock data on error for demonstration
            return self._get_mock_weather_data(city)
    
    def _get_mock_weather_data(self, city: str) -> Dict[str, Any]:
        """Generate mock weather data for demonstration purposes."""
        import random
        
        conditions = ["Clear", "Clouds", "Rain", "Snow", "Mist", "Thunderstorm"]
        descriptions = {
            "Clear": "clear sky",
            "Clouds": "scattered clouds",
            "Rain": "light rain",
            "Snow": "light snow",
            "Mist": "mist",
            "Thunderstorm": "thunderstorm"
        }
        
        condition = random.choice(conditions)
        
        return {
            "city": city,
            "temperature": round(random.uniform(15, 30), 1),
            "feels_like": round(random.uniform(15, 30), 1),
            "humidity": random.randint(30, 90),
            "pressure": random.randint(1000, 1030),
            "condition": condition,
            "description": descriptions[condition],
            "wind_speed": round(random.uniform(1, 10), 1),
            "country": "Demo",
            "note": "This is mock data for demonstration purposes"
        }