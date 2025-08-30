"""
Test script for direct LiteLLM API usage with an available model.

This script bypasses the LangChain integration and tests the LiteLLM API directly
using a known available model.
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
os.environ["LITELLM_LOG"] = "DEBUG"  # Enable debug logging
litellm._turn_on_debug()
# Let's try different models
MODELS_TO_TRY = [
    "openai/openai/gpt-4.1"
]

print("LiteLLM configured directly")
print(f"API Base: https://models.github.ai/inference")
print("API Key: [REDACTED]")
print(f"Models to try: {MODELS_TO_TRY}")

async def test_direct_litellm():
    """Test LiteLLM API directly with multiple models."""
    
    # Set up messages in litellm format
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, give me a short greeting in 10 words or less."}
    ]
    
    for model in MODELS_TO_TRY:
        print(f"\n=== Testing Direct LiteLLM API with model: {model} ===")
        
        # Call LiteLLM directly
        print(f"Calling LiteLLM API with model {model}...")
        try:
            response = await litellm.acompletion(
                model=model,
                messages=messages,
                base_url="https://models.github.ai/inference/v1",
                max_tokens=50  # Limit token usage
            )
            
            # Print the response
            print("\nResponse:")
            content = response.choices[0].message.content
            print(content)
            
        except Exception as e:
            print(f"\nError with model {model}: {e}")
            
        print("\n" + "="*50)

async def main():
    """Run all tests."""
    print("Starting Direct LiteLLM Tests with Available Models")
    print("="*50)
    
    # Run the direct litellm test
    await test_direct_litellm()
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    asyncio.run(main())