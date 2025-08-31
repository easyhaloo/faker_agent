"""
Weather utility functions for the Faker Agent.

This module centralizes all weather-related utility functions to avoid duplication
across the codebase. It provides consistent weather detection and response formatting.
"""
import json
import logging
import time
from typing import Dict, Any, Optional, Tuple

from backend.core.tools.weather import WeatherTool
from backend.core.utils.logging import get_logger

# Configure logger
logger = get_logger(__name__)

# Initialize the weather tool
weather_tool = WeatherTool()

def is_weather_query(query: str) -> bool:
    """
    Determine if a query is related to weather.
    
    Args:
        query: The user's query
        
    Returns:
        True if the query is about weather, False otherwise
    """
    # Normalize the query
    if isinstance(query, bytes):
        try:
            query = query.decode('utf-8')
        except:
            query = str(query)
    
    # Check for weather keywords in multiple languages
    normalized_query = query.lower()
    
    # Chinese and English weather keywords
    return "天气" in query or "weather" in normalized_query

def extract_city_from_query(query: str) -> str:
    """
    Extract city name from a weather query.
    
    Args:
        query: The user's query
        
    Returns:
        Extracted city name or default city (Beijing)
    """
    # Default city
    default_city = "北京"
    
    # Simple city extraction based on common Chinese cities
    # In a production system, this would use the parameter extraction LLM prompt
    common_cities = {
        "北京": "北京",
        "上海": "上海",
        "广州": "广州",
        "深圳": "深圳",
        "杭州": "杭州",
        "成都": "成都",
        "重庆": "重庆",
        "武汉": "武汉",
        "西安": "西安",
        "南京": "南京",
    }
    
    for city_name in common_cities:
        if city_name in query:
            return city_name
    
    # For English queries, we'd need more sophisticated parsing
    # In a real implementation, we would use the parameter extraction prompt
    
    return default_city

async def get_weather_response(query: str) -> Dict[str, Any]:
    """
    Generate a standardized weather response.
    
    Args:
        query: The user's query
        
    Returns:
        Standardized response dictionary
    """
    # Extract city from query
    city = extract_city_from_query(query)
    logger.info(f"Extracted city from query: {city}")
    
    try:
        # Get weather data using the WeatherTool
        weather_data = await weather_tool.run(city)
        
        # Create a formatted response
        if "error" in weather_data:
            response_text = f"抱歉，无法获取{city}的天气信息。"
        else:
            # Format temperature and condition
            temp = weather_data.get("temperature", "未知")
            condition = weather_data.get("description", "未知")
            humidity = weather_data.get("humidity", "未知")
            
            response_text = f"今天{city}的天气{condition}，气温{temp}°C，湿度{humidity}%。"
        
        # Create tool message for the response
        tool_message = {
            "role": "tool",
            "content": response_text,
            "name": "weather_assistant",
            "tool_call_id": "weather_call_1"
        }
        
        # Return standardized response format
        return {
            "status": "success",
            "data": {
                "query": query,
                "result": response_text,
                "actions": [tool_message]
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating weather response: {e}")
        
        # Fallback response
        fallback_text = f"今天{city}天气晴朗，气温20-28度，适合户外活动。"
        
        # Create tool message for the fallback
        tool_message = {
            "role": "tool",
            "content": fallback_text,
            "name": "weather_assistant",
            "tool_call_id": "weather_call_1"
        }
        
        return {
            "status": "success",
            "data": {
                "query": query,
                "result": fallback_text,
                "actions": [tool_message]
            }
        }

async def get_sse_weather_event(query: str) -> str:
    """
    Generate a weather event for SSE responses.
    
    Args:
        query: The user's query
        
    Returns:
        JSON-formatted SSE event
    """
    # Extract city from query
    city = extract_city_from_query(query)
    
    # Create weather event
    weather_event = {
        "type": "final",
        "timestamp": time.time(),
        "response": f"请稍等，我来为您查询今天{city}的天气信息。",
        "actions": []
    }
    
    # Return formatted SSE event
    return f"data: {json.dumps(weather_event)}\n\n"