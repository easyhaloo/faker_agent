# LiteLLM Integration with LangChain

This document describes how the Faker Agent backend integrates LiteLLM with LangChain to provide a flexible and modular AI chat experience.

## Overview

We've implemented a custom LangChain chat model that uses LiteLLM as its backend. This integration allows us to:

1. Use LiteLLM's model management capabilities with LangChain's agent framework
2. Support multiple LLM providers through a single interface
3. Extend the system with custom behaviors specific to our application

## Architecture

The integration consists of the following components:

```
backend/core/llm/
├── __init__.py              # Package exports
├── litellm_chat_model.py    # Custom LangChain chat model using LiteLLM
├── chat_model_factory.py    # Factory functions for creating chat models
└── agent_utils.py           # Utilities for working with LangChain agents
```

### LiteLLMChatModel

The `LiteLLMChatModel` class implements LangChain's `BaseChatModel` interface and uses LiteLLM for its backend. This class:

- Converts LangChain messages to LiteLLM format
- Handles synchronous and asynchronous generation
- Converts LiteLLM responses back to LangChain format
- Supports tool calling and streaming

### Chat Model Factory

The `chat_model_factory.py` module provides factory functions for creating different configurations of the LiteLLM chat model:

- `get_chat_model()` - Creates a general-purpose chat model
- `get_planner_model()` - Creates a model optimized for planning tasks
- `get_executor_model()` - Creates a model optimized for executing tasks
- `get_assembler_model()` - Creates a model optimized for assembling tools

### Agent Utilities

The `agent_utils.py` module provides utilities for working with LangChain agents:

- `create_agent_executor()` - Creates a LangChain agent executor with the specified tools and LLM
- `convert_to_langchain_tools()` - Converts internal tool format to LangChain tools

## Configuration

The LiteLLM integration is configured through environment variables and settings:

- `LITELLM_API_KEY` - API key for the LLM provider
- `LITELLM_MODEL` - Model to use (default: "gpt-3.5-turbo")
- `LITELLM_BASE_URL` - Custom endpoint URL for the LLM provider
- `LITELLM_TEMPERATURE` - Temperature for generation (default: 0.7)
- `LITELLM_MAX_TOKENS` - Maximum tokens to generate (default: 800)

These settings can be found in `backend/config/settings.py`.

## Usage Examples

### Basic Chat

```python
from backend.core.llm import get_chat_model
from langchain_core.messages import HumanMessage, SystemMessage

# Get a chat model instance
chat = get_chat_model()

# Create a message list
messages = [
    SystemMessage(content="You are a helpful assistant."),
    HumanMessage(content="What's the weather like today?")
]

# Generate a response
result = await chat._agenerate(messages)
response = result.generations[0].message.content

print(response)
```

### Creating an Agent

```python
from backend.core.llm import create_agent_executor
from backend.core.tools.registry import tool_registry

# Get tools from the registry
tools = tool_registry.get_all_langchain_tools()

# Create an agent executor
agent_executor = create_agent_executor(
    tools=tools,
    verbose=True
)

# Run the agent
result = await agent_executor.ainvoke({"input": "What's the weather like in Beijing?"})
print(result["output"])
```

## Integration with Flow Orchestrator

The LiteLLM chat model is integrated with the Flow Orchestrator to provide a seamless experience:

```python
from backend.core.llm import get_chat_model
from backend.core.graph.flow_orchestrator import FlowOrchestrator

# Create a chat model
chat_model = get_chat_model()

# Create a flow orchestrator with the chat model
orchestrator = FlowOrchestrator(llm_model=chat_model)

# Invoke the orchestrator
result = await orchestrator.invoke("What's the weather like today?")
```

## Testing

The LiteLLM integration includes tests that verify its functionality:

- `test_litellm_chat.py` - Tests basic chat functionality
- Unit tests for the LiteLLM chat model and its integration with LangChain

## Future Improvements

- Add support for streaming responses
- Implement caching for improved performance
- Add support for more LLM providers
- Extend tool handling capabilities