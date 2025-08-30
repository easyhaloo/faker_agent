"""
Test script for the custom LiteLLM chat model with environment variables from .env file.

This script tests the custom LiteLLM chat model implementation using the settings
defined in the backend/.env file.
"""
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.abspath("."))

# Load environment variables from .env file
dotenv_path = Path("backend/.env")
load_dotenv(dotenv_path=dotenv_path)

# Print the loaded environment variables (excluding API keys)
print("Environment variables loaded:")
print(f"LITELLM_MODEL: {os.environ.get('LITELLM_MODEL')}")
print(f"LITELLM_BASE_URL: {os.environ.get('LITELLM_BASE_URL')}")
print("LITELLM_API_KEY: [REDACTED]")

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from backend.core.llm import (
    LiteLLMChatModel,
    get_chat_model,
)

async def test_basic_chat():
    """Test basic chat functionality."""
    print("\n=== Testing Basic Chat ===")
    
    # Create a chat model instance using our environment variables
    chat = get_chat_model()  # This will use the settings from the .env file
    
    # Create a simple message list
    messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content="Hello, what can you tell me about LiteLLM?")
    ]
    
    # Invoke the model
    print("Sending message to LiteLLM chat model...")
    result = await chat._agenerate(messages)
    
    # Print the response
    print("\nResponse:")
    print(result.generations[0].message.content)
    print("\n" + "="*50)

async def main():
    """Run all tests."""
    print("Starting LiteLLM Chat Model Tests with Environment Variables")
    print("="*50)
    
    # Run the basic chat test
    await test_basic_chat()
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    asyncio.run(main())