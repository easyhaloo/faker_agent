"""
Weather query module for the Faker Agent.
"""
from backend.modules.weather.routes import router as weather_router
from backend.modules.weather.weather_tool import WeatherTool
from backend.modules.weather.weather_assistant_tool import WeatherAssistantTool
from backend.modules.weather.streaming_weather_tool import StreamingWeatherTool
from backend.core.registry.enhanced_registry import enhanced_registry

# These tools are auto-registered in their respective files