"""
Weather assistant module that provides prompt-guided weather information.

This module implements a weather assistant that can interpret natural language
queries about weather and use the WeatherTool to retrieve information.
"""
import logging
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import litellm
from litellm import completion

from backend.config.settings import settings
from backend.core.prompts.weather_prompts import (
    PARAM_EXTRACTION_SYSTEM_MESSAGE,
    PARAM_EXTRACTION_PROMPT_TEMPLATE,
    RESPONSE_GENERATION_SYSTEM_MESSAGE,
    WEATHER_RESPONSE_PROMPT_TEMPLATE
)
from backend.modules.weather.weather_tool import WeatherTool

# Configure logger
logger = logging.getLogger(__name__)


class WeatherAssistant:
    """
    Weather assistant that can interpret natural language queries and 
    provide weather information using the WeatherTool.
    """
    
    def __init__(self):
        """Initialize the weather assistant."""
        self.weather_tool = WeatherTool()
        self.model = settings.LITELLM_MODEL
        self.temperature = settings.LITELLM_TEMPERATURE
        self.max_tokens = settings.LITELLM_MAX_TOKENS
        
        # Set API key from settings
        if settings.LITELLM_API_KEY:
            litellm.api_key = settings.LITELLM_API_KEY
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a natural language query about weather.
        
        Args:
            query: The natural language query from the user
            
        Returns:
            Response with weather information and a formatted message
        """
        try:
            # 1. Parse the query to extract parameters
            params = await self._extract_parameters(query)
            
            # 2. Call the weather tool with the extracted parameters
            weather_data = await self.weather_tool.run(**params)
            
            # 3. Generate a natural language response
            response_text = await self._generate_response(query, weather_data)
            
            return {
                "status": "success",
                "data": {
                    "query": query,
                    "weather": weather_data,
                    "response": response_text,
                    "extracted_params": params
                }
            }
            
        except Exception as e:
            logger.error(f"Error in weather assistant: {e}")
            return {
                "status": "error",
                "error": {
                    "message": str(e)
                }
            }
    
    async def _extract_parameters(self, query: str) -> Dict[str, Any]:
        """
        Extract parameters from a natural language query.
        
        Uses an LLM to parse the query and extract parameters like:
        - city
        - country
        - units (metric/imperial)
        - forecast_days
        
        Args:
            query: The natural language query
            
        Returns:
            Dictionary of parameters to pass to the weather tool
        """
        # Default parameters
        params = {
            "city": "Beijing",  # Default city
            "country": None,
            "units": "metric",
            "forecast_days": 0
        }
        
        # Create a prompt for parameter extraction
        extraction_prompt = PARAM_EXTRACTION_PROMPT_TEMPLATE.format(query=query)
        
        try:
            # Call the LLM for parameter extraction
            response = await completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": PARAM_EXTRACTION_SYSTEM_MESSAGE},
                    {"role": "user", "content": extraction_prompt}
                ],
                temperature=0.0,  # Use low temperature for deterministic results
                max_tokens=300
            )
            
            # Extract the JSON response
            output = response.choices[0].message.content.strip()
            
            # Use regex to extract the JSON part
            import json
            import re
            
            # Find JSON object in the response
            json_match = re.search(r'{.*}', output, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                extracted_params = json.loads(json_str)
                
                # Update the default parameters with extracted values
                for key, value in extracted_params.items():
                    if key in params and value is not None:
                        params[key] = value
                
                # Ensure city is provided
                if not params["city"]:
                    raise ValueError("Could not extract city from the query")
                    
                # Ensure forecast_days is within range
                params["forecast_days"] = max(0, min(7, params.get("forecast_days", 0)))
                
                return params
            else:
                logger.warning(f"Could not extract JSON from LLM response: {output}")
                # Fall back to regex-based extraction for city
                city_match = re.search(r'(?:in|at|for)\s+([A-Za-z\s]+)(?:\?|$|\.)', query)
                if city_match:
                    params["city"] = city_match.group(1).strip()
                    
                # Check for forecast keywords
                if any(word in query.lower() for word in ["forecast", "tomorrow", "week", "days", "future"]):
                    params["forecast_days"] = 5  # Default forecast length
                
                return params
                
        except Exception as e:
            logger.error(f"Error extracting parameters: {e}")
            # Fall back to a simple regex-based extraction
            city_match = re.search(r'(?:in|at|for)\s+([A-Za-z\s]+)(?:\?|$|\.)', query)
            if city_match:
                params["city"] = city_match.group(1).strip()
            
            # Use default values for other parameters
            return params
    
    async def _generate_response(self, query: str, weather_data: Dict[str, Any]) -> str:
        """
        Generate a natural language response based on the weather data.
        
        Args:
            query: The original user query
            weather_data: The weather data from the weather tool
            
        Returns:
            Natural language response about the weather
        """
        # Create a prompt for response generation
        response_prompt = WEATHER_RESPONSE_PROMPT_TEMPLATE.format(
            query=query,
            weather_data=weather_data
        )
        
        try:
            # Call the LLM for response generation
            response = await completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": RESPONSE_GENERATION_SYSTEM_MESSAGE},
                    {"role": "user", "content": response_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            
            # Fall back to a template-based response if LLM fails
            try:
                location = weather_data.get("location", {})
                current = weather_data.get("current", {})
                forecast = weather_data.get("forecast", [])
                
                city = location.get("city", "the requested location")
                current_temp = current.get("temperature", {}).get("current", "N/A")
                condition = current.get("condition", "N/A")
                
                # Basic response template
                response = f"It's currently {condition} and {current_temp} in {city}."
                
                # Add forecast if available
                if forecast and len(forecast) > 0:
                    tomorrow = forecast[0]
                    response += f" Tomorrow will be {tomorrow.get('condition', 'N/A')} with temperatures around {tomorrow.get('temperature', {}).get('max', 'N/A')}."
                
                return response
                
            except Exception as inner_e:
                logger.error(f"Error in fallback response generation: {inner_e}")
                return "I'm sorry, I couldn't generate a proper response about the weather data."


# Create a global assistant instance
weather_assistant = WeatherAssistant()