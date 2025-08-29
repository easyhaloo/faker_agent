"""
Test for API routes with real-time task status updates.
"""
import asyncio
import os
import sys
from uuid import uuid4

import pytest
import httpx
from backend.api.routes import tasks


@pytest.mark.asyncio
async def test_api_routes():
    """Test API routes functionality."""
    # Skip this test if the server is not running
    pytest.skip("Skipping API routes test - requires running server")
    
    base_url = "http://localhost:8000/api"
    
    # Test submitting an async task
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/agent/task/async",
            json={"query": "What is the weather like today?"}
        )
        
        assert response.status_code == 200
        data = response.json()
        task_id = data["data"]["task_id"]
    
    # Test getting task status
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{base_url}/agent/task/{task_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data['data']
        assert "progress" in data['data']
    
    # Wait for task to complete
    while True:
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
        assert data['data']['status'] in ['completed', 'failed']
    
    # Test listing tools
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{base_url}/tools")
        
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data['data']
    
    # Test system status
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{base_url}/system/status")
        
        assert response.status_code == 200
        data = response.json()
        assert "version" in data['data']
        assert "active_tasks" in data['data']