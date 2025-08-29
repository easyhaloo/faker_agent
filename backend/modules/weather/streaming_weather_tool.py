"""
Streaming Weather Tool for the Faker Agent.

This module implements a streaming version of the weather tool
that can emit incremental results for a more interactive experience.
"""
import asyncio
import logging
import random
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, Optional

from backend.core.tools.base import BaseTool
from backend.core.tools.registry import tool_registry

# Configure logger
logger = logging.getLogger(__name__)


class StreamingWeatherTool(BaseTool):
    """
    Tool for querying weather data with streaming results.
    
    This tool emits partial results as it "fetches" the weather data,
    demonstrating how to implement a streaming tool in the agent system.
    """
    
    name = "streaming_weather"
    description = "Queries weather information with streaming updates"
    tags = ["weather", "data", "streaming"]
    priority = 15
    
    def get_parameters(self):
        return [
            {
                "name": "city",
                "type": "string",
                "description": "The city name to get weather for",
                "required": True
            },
            {
                "name": "country",
                "type": "string",
                "description": "Optional country code to disambiguate city names",
                "required": False
            },
            {
                "name": "detailed",
                "type": "boolean",
                "description": "Whether to return detailed weather information",
                "required": False,
                "default": False
            }
        ]
    
    async def run(
        self, 
        city: str, 
        country: Optional[str] = None, 
        detailed: bool = False,
        stream_callback = None
    ) -> Dict[str, Any]:
        """
        Get weather data for the specified city with streaming updates.
        
        Args:
            city: The city name
            country: Optional country code
            detailed: Whether to return detailed weather information
            stream_callback: Optional callback for streaming updates
            
        Returns:
            Weather data for the city
        """
        logger.info(f"Getting weather for {city}{f', {country}' if country else ''}")
        
        try:
            # Stream results if a callback is provided
            if stream_callback:
                async for update in self._stream_weather(city, country, detailed):
                    await stream_callback(update)
            
            # Return the final result
            return self._get_mock_weather(city, country, detailed)
            
        except Exception as e:
            logger.error(f"Error getting weather: {e}")
            raise ValueError(f"Failed to get weather data: {str(e)}")
    
    async def _stream_weather(
        self, 
        city: str, 
        country: Optional[str] = None,
        detailed: bool = False
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream weather data updates.
        
        Args:
            city: The city name
            country: Optional country code
            detailed: Whether to return detailed weather information
            
        Yields:
            Partial weather data updates
        """
        # Simulate steps in fetching weather data
        
        # Step 1: Initial connection
        yield {
            "status": "connecting",
            "message": f"Connecting to weather service for {city}...",
            "progress": 10
        }
        await asyncio.sleep(0.5)
        
        # Step 2: Location lookup
        yield {
            "status": "processing",
            "message": f"Looking up coordinates for {city}...",
            "progress": 30,
            "location": {
                "city": city.capitalize(),
                "country": country or "Unknown"
            }
        }
        await asyncio.sleep(0.7)
        
        # Step 3: Current conditions
        current = {
            "temperature": {
                "current": f"{random.randint(15, 35)}°C",
                "feels_like": f"{random.randint(15, 35)}°C"
            },
            "condition": random.choice(["Sunny", "Cloudy", "Partly Cloudy", "Rainy", "Clear"]),
            "humidity": f"{random.randint(30, 90)}%"
        }
        
        yield {
            "status": "processing",
            "message": f"Retrieved current conditions for {city}...",
            "progress": 60,
            "location": {
                "city": city.capitalize(),
                "country": country or "Unknown"
            },
            "current": current
        }
        await asyncio.sleep(0.5)
        
        # Step 4: Forecast (if detailed)
        if detailed:
            yield {
                "status": "processing",
                "message": f"Retrieving forecast for {city}...",
                "progress": 80,
                "location": {
                    "city": city.capitalize(),
                    "country": country or "Unknown"
                },
                "current": current
            }
            await asyncio.sleep(0.8)
        
        # Step 5: Complete data
        final_data = self._get_mock_weather(city, country, detailed)
        yield {
            "status": "completed",
            "message": f"Weather data retrieved for {city}",
            "progress": 100,
            "data": final_data
        }
    
    def _get_mock_weather(
        self, 
        city: str, 
        country: Optional[str] = None,
        detailed: bool = False
    ) -> Dict[str, Any]:
        """
        Get mock weather data for demo purposes.
        
        Args:
            city: The city name
            country: Optional country code
            detailed: Whether to return detailed weather information
            
        Returns:
            Mock weather data
        """
        # Get current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Basic data available for all cities
        weather_data = {
            "location": {
                "city": city.capitalize(),
                "country": country or "Unknown",
                "date": current_date
            },
            "current": {
                "temperature": {
                    "current": f"{random.randint(15, 35)}°C",
                    "min": f"{random.randint(10, 20)}°C",
                    "max": f"{random.randint(25, 40)}°C",
                    "feels_like": f"{random.randint(15, 35)}°C"
                },
                "condition": random.choice(["Sunny", "Cloudy", "Partly Cloudy", "Rainy", "Clear"]),
                "humidity": f"{random.randint(30, 90)}%",
                "wind": {
                    "direction": random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"]),
                    "speed": f"{random.randint(0, 30)} km/h"
                }
            }
        }
        
        # Add detailed forecast if requested
        if detailed:
            forecast = []
            for i in range(5):
                forecast.append({
                    "date": (datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + 
                            # Add days to the current date
                            datetime.timedelta(days=i+1)).strftime("%Y-%m-%d"),
                    "condition": random.choice(["Sunny", "Cloudy", "Partly Cloudy", "Rainy", "Clear"]),
                    "temperature": {
                        "min": f"{random.randint(10, 20)}°C",
                        "max": f"{random.randint(25, 40)}°C"
                    },
                    "humidity": f"{random.randint(30, 90)}%",
                    "precipitation": {
                        "probability": f"{random.randint(0, 100)}%",
                        "amount": f"{random.randint(0, 30)} mm" if random.random() > 0.5 else "0 mm"
                    }
                })
            
            weather_data["forecast"] = forecast
        
        return weather_data


# Register the streaming weather tool
tool_registry.register_tool(StreamingWeatherTool())