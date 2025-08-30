"""
Test script for the custom LiteLLM chat model with manually set environment variables.

This script tests the custom LiteLLM chat model implementation using manually set
environment variables instead of relying on the .env file.
"""
import asyncio
import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.abspath("."))

# Set environment variables manually
os.environ["LITELLM_API_KEY"] = "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"
os.environ["LITELLM_MODEL"] = "openai/gpt-5-chat"
os.environ["LITELLM_BASE_URL"] = "https://models.github.ai/inference"

# Print the set environment variables (excluding full API key)
print("Environment variables set:")
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
    chat = get_chat_model()  # This will use the settings from the environment variables
    
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
    print("Starting LiteLLM Chat Model Tests with Manual Environment Variables")
    print("="*50)
    
    # Run the basic chat test
    await test_basic_chat()
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    asyncio.run(main())