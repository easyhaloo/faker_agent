# Weather Module

This module provides weather-related tools and services for the Faker Agent platform.

## Tools

### 1. WeatherTool

- **Name**: `weather_query`
- **Description**: Basic weather information lookup by city
- **Tags**: `weather`, `data`
- **Priority**: 10

### 2. WeatherAssistantTool

- **Name**: `weather_assistant`
- **Description**: Natural language weather information
- **Tags**: `weather`, `assistant`, `natural_language`
- **Priority**: 20

### 3. StreamingWeatherTool

- **Name**: `streaming_weather`
- **Description**: Weather information with streaming updates
- **Tags**: `weather`, `data`, `streaming`
- **Priority**: 15

## Components

### 1. Weather Tool (`weather_tool.py`)

A structured tool for querying weather data with specific parameters.

**Features:**
- Get current weather conditions
- Get weather forecasts (up to 7 days)
- Support for both metric and imperial units
- Location search by city and country
- Detailed weather data including temperature, conditions, humidity, wind, etc.

**Example usage as a tool:**
```python
weather_data = await weather_tool.run(
    city="Beijing", 
    country="CN",
    units="metric",
    forecast_days=3
)
```

### 2. Weather Assistant (`weather_assistant.py`, `weather_assistant_tool.py`)

A natural language interface for weather queries using LLMs.

**Features:**
- Natural language query understanding
- Parameter extraction from text
- Human-friendly weather responses
- Seamless integration with the structured weather tool
- Available as both a service and a tool

**Example usage:**
```python
# As a service
response = await weather_assistant.process_query(
    "What's the weather like in Beijing tomorrow?"
)

# As a tool
response = await weather_assistant_tool.run(
    query="What's the weather like in Beijing tomorrow?"
)
```

### 3. Weather API Routes (`routes.py`)

FastAPI routes for accessing weather data.

**Endpoints:**
- `GET /weather/{city}` - Get current weather
- `GET /weather/forecast/{city}` - Get weather forecast
- `GET /weather/locations/search` - Search for locations
- `POST /weather/assistant/query` - Query the weather assistant

## Usage Examples

### With the New Protocol Layer

```json
// HTTP Request (Synchronous)
{
  "input": "What's the weather like in Beijing?",
  "protocol": "http",
  "mode": "sync",
  "tool_tags": ["weather"]
}

// SSE Request (Streaming)
{
  "input": "Show me detailed weather forecast for New York",
  "protocol": "sse",
  "mode": "stream",
  "tool_tags": ["weather", "streaming"]
}

// WebSocket Request
{
  "input": "What's the weather forecast for London?",
  "tool_tags": ["weather"]
}
```

### Direct API Calls

```python
# Get current weather
response = requests.get("http://localhost:8000/api/weather/Beijing?units=metric")

# Get forecast
response = requests.get("http://localhost:8000/api/weather/forecast/Beijing?days=5")

# Use the assistant
response = requests.post(
    "http://localhost:8000/api/weather/assistant/query",
    json={"query": "What's the weather like in Beijing tomorrow?"}
)
```

### Using Tools in the Agent

```python
# Using the weather tool
result = await registry.execute_tool(
    "weather_query",
    city="Beijing",
    forecast_days=3
)

# Using the weather assistant tool
result = await registry.execute_tool(
    "weather_assistant",
    query="What's the weather like in Beijing tomorrow?"
)
```

## Configuration

The weather module uses the following configuration settings:

```python
# in backend/config/settings.py
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
WEATHER_API_URL = os.getenv("WEATHER_API_URL", "https://api.openweathermap.org/data/2.5")
```

For production use, set the `WEATHER_API_KEY` environment variable with a valid API key.