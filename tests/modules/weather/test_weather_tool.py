"""
Tests for the weather tools.
"""
import pytest

from backend.modules.weather.streaming_weather_tool import StreamingWeatherTool
from backend.modules.weather.weather_assistant_tool import WeatherAssistantTool
from backend.modules.weather.weather_tool import WeatherTool


@pytest.fixture
def weather_tool():
    """Create a weather tool."""
    return WeatherTool()


@pytest.fixture
def weather_assistant_tool():
    """Create a weather assistant tool."""
    return WeatherAssistantTool()


@pytest.fixture
def streaming_weather_tool():
    """Create a streaming weather tool."""
    return StreamingWeatherTool()


def test_weather_tool_initialization(weather_tool):
    """Test that the weather tool is initialized correctly."""
    # Check tool metadata
    assert weather_tool.name == "weather_query"
    assert "Queries weather information" in weather_tool.description
    assert "weather" in weather_tool.tags
    assert "data" in weather_tool.tags
    assert weather_tool.priority > 0


def test_weather_assistant_tool_initialization(weather_assistant_tool):
    """Test that the weather assistant tool is initialized correctly."""
    # Check tool metadata
    assert weather_assistant_tool.name == "weather_assistant"
    assert "natural language" in weather_assistant_tool.description.lower()
    assert "weather" in weather_assistant_tool.tags
    assert "assistant" in weather_assistant_tool.tags
    assert "natural_language" in weather_assistant_tool.tags
    assert weather_assistant_tool.priority > 0


def test_streaming_weather_tool_initialization(streaming_weather_tool):
    """Test that the streaming weather tool is initialized correctly."""
    # Check tool metadata
    assert streaming_weather_tool.name == "streaming_weather"
    assert "streaming" in streaming_weather_tool.description.lower()
    assert "weather" in streaming_weather_tool.tags
    assert "data" in streaming_weather_tool.tags
    assert "streaming" in streaming_weather_tool.tags
    assert streaming_weather_tool.priority > 0


@pytest.mark.asyncio
async def test_weather_tool_run(weather_tool):
    """Test that the weather tool can be run."""
    # Run the tool
    result = await weather_tool.run(city="Beijing")
    
    # Check that we got a result
    assert result is not None
    assert "city" in result
    assert result["city"] == "Beijing"
    assert "temperature" in result
    assert "condition" in result


@pytest.mark.asyncio
async def test_streaming_weather_tool_run(streaming_weather_tool):
    """Test that the streaming weather tool can be run."""
    # Run the tool
    result = await streaming_weather_tool.run(city="Beijing")
    
    # Check that we got a result
    assert result is not None
    assert "location" in result
    assert result["location"]["city"] == "Beijing"
    assert "current" in result
    assert "temperature" in result["current"]