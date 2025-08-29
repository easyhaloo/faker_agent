"""
API routes for the weather module.
"""
import logging
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException, Query

# Removed unused import
from backend.modules.weather.weather_tool import WeatherTool

# Configure logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.get("/{city}")
async def get_weather(
    city: str,
    country: Optional[str] = None
):
    """
    Get weather for a specific city.
    
    Args:
        city: The city name
        country: Optional country code
        
    Returns:
        Weather data for the city
    """
    try:
        # Get weather tool from registry
        weather_tool = WeatherTool()
        weather_data = await weather_tool.run(city=city, country=country)
        
        return {
            "status": "success",
            "data": weather_data
        }
        
    except Exception as e:
        logger.error(f"Error getting weather: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get weather data: {str(e)}"
        )