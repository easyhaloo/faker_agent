"""
Prompt templates for the weather assistant module.
"""

# System message for parameter extraction
PARAM_EXTRACTION_SYSTEM_MESSAGE = "You are a weather query parser that extracts parameters from natural language."

# Parameter extraction prompt template
PARAM_EXTRACTION_PROMPT_TEMPLATE = """
Extract weather query parameters from the following user request:

"{query}"

Extract the following parameters:
1. city: The city name the user is asking about
2. country: The country code (if specified)
3. units: 'metric' or 'imperial' based on user preference
4. forecast_days: Number of days for forecast (0-7), 0 means current weather only

Return your answer in this exact JSON format:
{{
    "city": "extracted city name",
    "country": "extracted country code or null",
    "units": "metric or imperial",
    "forecast_days": number from 0-7
}}

If a parameter is not specified, use these defaults:
- city: Must be extracted from the query (no default)
- country: null
- units: "metric"
- forecast_days: 0 for current weather, or appropriate value if forecast is requested

Determine forecast_days based on whether the user is asking about:
- Current weather (0 days)
- Tomorrow/next day (1 day)
- This week/next few days (3-5 days)
- Extended forecast (7 days)
"""

# System message for response generation
RESPONSE_GENERATION_SYSTEM_MESSAGE = "You are a helpful weather assistant that provides clear and concise weather information."

# Weather response generation prompt template
WEATHER_RESPONSE_PROMPT_TEMPLATE = """
Generate a natural language response to the user's weather query:

User query: "{query}"

Weather data: {weather_data}

Guidelines for your response:
1. Be conversational and friendly
2. Focus on answering the specific question asked
3. Include relevant weather details from the provided data
4. For current weather, mention temperature, conditions, and feels like
5. For forecasts, summarize the trends and notable weather events
6. Keep the response concise (2-3 sentences for current weather, 3-5 for forecast)
7. Use natural phrasing like "It's currently sunny and 25°C in Beijing"
8. If forecast data is available, include a brief summary of upcoming weather

Only include information that is present in the weather data.
"""