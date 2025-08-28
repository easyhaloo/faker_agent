"""
Test for API routes with real-time task status updates.
"""
import asyncio
import os
import sys
from uuid import uuid4

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import httpx
from backend.api.routes import tasks


async def test_api_routes():
    """Test API routes functionality."""
    base_url = "http://localhost:8000/api"
    
    # Test submitting an async task
    print("Submitting async task...")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/agent/task/async",
            json={"query": "What is the weather like today?"}
        )
        
        if response.status_code == 200:
            data = response.json()
            task_id = data["data"]["task_id"]
            print(f"Task submitted successfully with ID: {task_id}")
        else:
            print(f"Error submitting task: {response.status_code} - {response.text}")
            return
    
    # Test getting task status
    print("\nGetting task status...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{base_url}/agent/task/{task_id}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Task status: {data['data']['status']}")
            print(f"Task progress: {data['data']['progress']}%")
        else:
            print(f"Error getting task status: {response.status_code} - {response.text}")
    
    # Wait for task to complete
    print("\nWaiting for task to complete...")
    while True:
        if task_id in tasks:
            task_info = tasks[task_id]
            if task_info["status"] in ["completed", "failed"]:
                break
        await asyncio.sleep(1)
    
    # Test getting final task status
    print("\nGetting final task status...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{base_url}/agent/task/{task_id}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Final task status: {data['data']['status']}")
            if data['data']['status'] == 'completed':
                print("Task completed successfully!")
            elif data['data']['status'] == 'failed':
                print(f"Task failed: {data['data']['error']}")
        else:
            print(f"Error getting final task status: {response.status_code} - {response.text}")
    
    # Test listing tools
    print("\nListing tools...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{base_url}/tools")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Available tools: {len(data['data']['tools'])}")
            for tool in data['data']['tools']:
                print(f"- {tool['name']}: {tool['description']}")
        else:
            print(f"Error listing tools: {response.status_code} - {response.text}")
    
    # Test system status
    print("\nGetting system status...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{base_url}/system/status")
        
        if response.status_code == 200:
            data = response.json()
            print(f"System version: {data['data']['version']}")
            print(f"Active tasks: {data['data']['active_tasks']}")
        else:
            print(f"Error getting system status: {response.status_code} - {response.text}")
    
    print("\nAPI routes test completed!")


if __name__ == "__main__":
    asyncio.run(test_api_routes())