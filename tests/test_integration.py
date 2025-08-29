"""
Integration tests for the Faker Agent system.
"""
import asyncio
import os
import sys
from uuid import uuid4

import pytest
import httpx
from backend.api.routes import tasks
from backend.core.memory.redis_memory import RedisMemory
from backend.core.tools.calculator import CalculatorTool
from backend.core.tools.web_search import WebSearchTool


@pytest.mark.asyncio
async def test_full_system():
    """Test the full system integration."""
    # Skip this test if the server is not running
    pytest.skip("Skipping integration test - requires running server and Redis")
    
    base_url = "http://localhost:8000/api"
    
    # Test 1: Redis Memory
    memory = RedisMemory(host="localhost", port=6379, db=0)
    
    # Add messages to a conversation
    conv_id = f"test_conv_{uuid4().hex[:8]}"
    await memory.add_message(conv_id, "user", "Hello, this is a test message!")
    await memory.add_message(conv_id, "assistant", "Hi there! I'm responding to your test.")
    
    # Retrieve messages
    messages = await memory.get_messages(conv_id)
    assert len(messages) == 2
    assert messages[0].role == "user"
    assert messages[1].role == "assistant"
    
    # Test metadata
    await memory.set_metadata(conv_id, "test_key", "test_value")
    value = await memory.get_metadata(conv_id, "test_key")
    assert value == "test_value"
    
    # Test 2: Calculator Tool
    calculator = CalculatorTool()
    
    # Test basic operations
    result = await calculator.run("2 + 3 * 4")
    assert result["result"] == 14
    
    # Test error handling
    result = await calculator.run("10 / 0")
    assert "error" in result
    assert "zero" in result["error"].lower()
    
    # Test 3: Web Search Tool
    searcher = WebSearchTool()
    
    # Test search
    result = await searcher.run("Python programming", max_results=2)
    assert "results" in result
    assert len(result["results"]) <= 2