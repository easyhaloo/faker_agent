"""
Integration tests for the Faker Agent system.
"""
import asyncio
import os
import sys
from uuid import uuid4

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import httpx
from backend.api.routes import tasks
from backend.core.memory.redis_memory import RedisMemory
from backend.core.tools.calculator import CalculatorTool
from backend.core.tools.web_search import WebSearchTool


async def test_full_system():
    """Test the full system integration."""
    base_url = "http://localhost:8000/api"
    
    print("=== Full System Integration Test ===\n")
    
    # Test 1: Redis Memory
    print("1. Testing Redis Memory...")
    try:
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
        
        print("   ✓ Redis Memory test passed")
    except Exception as e:
        print(f"   ✗ Redis Memory test failed: {e}")
        return
    
    # Test 2: Calculator Tool
    print("\n2. Testing Calculator Tool...")
    try:
        calculator = CalculatorTool()
        
        # Test basic operations
        result = await calculator.run("2 + 3 * 4")
        assert result["result"] == 14
        
        # Test error handling
        result = await calculator.run("10 / 0")
        assert "error" in result
        assert "zero" in result["error"].lower()
        
        print("   ✓ Calculator Tool test passed")
    except Exception as e:
        print(f"   ✗ Calculator Tool test failed: {e}")
        return
    
    # Test 3: Web Search Tool
    print("\n3. Testing Web Search Tool...")
    try:
        searcher = WebSearchTool()
        
        # Test search
        result = await searcher.run("Python programming", max_results=2)
        assert "results" in result
        assert len(result["results"]) <= 2
        
        print("   ✓ Web Search Tool test passed")
    except Exception as e:
        print(f"   ✗ Web Search Tool test failed: {e}")
        return
    
    # Test 4: API Routes
    print("\n4. Testing API Routes...")
    try:
        # Test submitting an async task
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/agent/task/async",
                json={"query": "What is the weather like today?"}
            )
            
            assert response.status_code == 200
            data = response.json()
            task_id = data["data"]["task_id"]
            print(f"   Task submitted with ID: {task_id}")
        
        # Wait for task to complete
        print("   Waiting for task to complete...")
        for _ in range(30):  # Wait up to 30 seconds
            if task_id in tasks:
                task_info = tasks[task_id]
                if task_info["status"] in ["completed", "failed"]:
                    break
            await asyncio.sleep(1)
        
        # Test getting final task status
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/agent/task/{task_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["data"]["status"] in ["completed", "failed"]
        
        # Test listing tools
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/tools")
            assert response.status_code == 200
            data = response.json()
            assert "tools" in data["data"]
        
        # Test system status
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/system/status")
            assert response.status_code == 200
            data = response.json()
            assert "version" in data["data"]
        
        print("   ✓ API Routes test passed")
    except Exception as e:
        print(f"   ✗ API Routes test failed: {e}")
        return
    
    print("\n=== All Integration Tests Passed! ===")


if __name__ == "__main__":
    asyncio.run(test_full_system())