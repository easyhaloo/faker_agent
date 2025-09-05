"""
Tests for the weather tools.
"""
import pytest

from backend.core.tools.weather import WeatherTool


@pytest.fixture
def weather_tool():
    """Create a weather tool."""
    return WeatherTool()


def test_weather_tool_initialization(weather_tool):
    """Test that the weather tool is initialized correctly."""
    # Check tool metadata
    assert weather_tool.name == "weather"
    assert "weather" in weather_tool.description.lower()
    assert "weather" in weather_tool.tags
    assert weather_tool.priority > 0


@pytest.mark.asyncio
async def test_weather_tool_run(weather_tool):
    """Test that the weather tool can be run."""
    # Run the tool
    result = await weather_tool.run(city="Beijing")
    
    # Check that we got a result
    assert result is not None
    assert "city" in result
    assert result["city"] == "Beijing"
    assert "temp_c" in result or "temperature" in result