"""
Test script for direct LiteLLM API usage with explicit configuration.

This script bypasses the LangChain integration and tests the LiteLLM API directly.
"""
import asyncio
import os
import sys
from pprint import pprint

# Add the project root to the Python path
sys.path.append(os.path.abspath("."))

# Import LiteLLM directly
import litellm
from langchain_core.messages import HumanMessage, SystemMessage

# Configure LiteLLM directly
litellm.api_key = "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"
litellm.set_verbose = True  # Enable verbose logging

print("LiteLLM configured directly")
print(f"Model: openai/gpt-5-chat")
print(f"API Base: https://models.github.ai/inference")
print("API Key: [REDACTED]")

async def test_direct_litellm():
    """Test LiteLLM API directly."""
    print("\n=== Testing Direct LiteLLM API ===")
    
    # Set up messages in litellm format
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, what can you tell me about LiteLLM?"}
    ]
    
    # Call LiteLLM directly
    print("Calling LiteLLM API directly...")
    try:
        response = await litellm.acompletion(
            model="openai/gpt-5-chat",
            messages=messages,
            api_base="https://models.github.ai/inference"
        )
        
        # Print the response
        print("\nResponse:")
        content = response.choices[0].message.content
        print(content)
        
    except Exception as e:
        print(f"\nError: {e}")
        
    print("\n" + "="*50)

async def main():
    """Run all tests."""
    print("Starting Direct LiteLLM Tests")
    print("="*50)
    
    # Run the direct litellm test
    await test_direct_litellm()
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    asyncio.run(main())