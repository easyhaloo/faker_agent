"""
Weather query module for the Faker Agent.
"""
from backend.modules.weather.routes import router as weather_router
from backend.modules.weather.weather_tool_langchain import WeatherTool
from backend.core.tools.registry import tool_registry

# Register the weather tool
weather_tool = WeatherTool()
tool_registry.register_tool(weather_tool)