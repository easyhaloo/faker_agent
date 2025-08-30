"""
Integration tests for the Protocol API integration.

This test script verifies that the API layer correctly integrates with
the Protocol layer for different communication methods.
"""
import asyncio
import json
import logging
import os
import sys
from typing import Dict, List, Optional, AsyncGenerator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketDisconnect
from httpx import AsyncClient

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.core.contracts.protocol import ProtocolType
from backend.core.graph.event_types import Event, EventType
from backend.core.protocol.filtered_registry import filtered_protocol_registry
from backend.interface.api.routes_agent import router as agent_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Create FastAPI app for testing
app = FastAPI()
app.include_router(agent_router)


# Mock orchestrator stream for testing
async def mock_stream(query: str) -> AsyncGenerator[Event, None]:
    """Mock event stream for testing."""
    # Tool call start event
    yield Event(
        type=EventType.TOOL_CALL_START,
        tool_name="test_tool",
        tool_args={"arg1": "value1"},
        tool_call_id="123",
        timestamp=1.0
    )
    
    # Tool call result event
    yield Event(
        type=EventType.TOOL_CALL_RESULT,
        tool_call_id="123",
        result={"data": "test result"},
        error=None,
        timestamp=2.0
    )
    
    # Final response event
    yield Event(
        type=EventType.FINAL,
        response=f"Response to: {query}",
        timestamp=3.0
    )


# Mock LLMAssembler and FlowOrchestrator
@pytest.fixture(autouse=True)
def mock_orchestrator(monkeypatch):
    """Mock the LLMAssembler and FlowOrchestrator for testing."""
    # Mock LLMAssembler
    class MockAssembler:
        async def create_execution_plan(self, query):
            from backend.core.contracts.execution import ExecutionPlan, ToolChain
            return ExecutionPlan(
                plan="Test plan",
                tool_chain=ToolChain(nodes=[]),
                raw_response="Test raw response"
            )
    
    # Mock FlowOrchestrator
    class MockOrchestrator:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
            
        async def invoke(self, query, **kwargs):
            return {
                "messages": [
                    {"role": "user", "content": query},
                    {"role": "assistant", "content": f"Response to: {query}"}
                ]
            }
            
        async def stream(self, query):
            return mock_stream(query)
    
    # Apply mocks
    monkeypatch.setattr(
        "backend.interface.api.routes_agent.LLMAssembler",
        MockAssembler
    )
    monkeypatch.setattr(
        "backend.interface.api.routes_agent.FlowOrchestrator",
        MockOrchestrator
    )


# Test HTTP protocol
@pytest.mark.asyncio
async def test_http_protocol():
    """Test the HTTP protocol endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/agent/v1/respond",
            json={
                "query": "Test query",
                "protocol_type": "http"
            }
        )
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "Response to: Test query" in data["data"]["response"]
        assert len(data["data"]["tool_calls"]) == 1


# Test SSE protocol
@pytest.mark.asyncio
async def test_sse_protocol():
    """Test the SSE protocol endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/agent/v1/respond",
            json={
                "query": "Test query",
                "protocol_type": "sse"
            },
            headers={"Accept": "text/event-stream"}
        )
        
        # Check response
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream"
        
        # Parse SSE events
        events = []
        for line in response.text.split("\n\n"):
            if line.startswith("data: "):
                event_json = line[6:]  # Remove "data: "
                if event_json:
                    events.append(json.loads(event_json))
        
        # Check events
        assert len(events) == 3
        assert events[0]["type"] == "tool_call_start"
        assert events[1]["type"] == "tool_call_result"
        assert events[2]["type"] == "final"
        assert events[2]["response"] == "Response to: Test query"


# Test WebSocket protocol
def test_websocket_protocol():
    """Test the WebSocket endpoint."""
    with TestClient(app) as client:
        with client.websocket_connect("/api/agent/v1/ws") as websocket:
            # Send query
            websocket.send_json({
                "query": "Test query"
            })
            
            # Collect responses
            events = []
            for _ in range(3):  # Expect 3 events
                events.append(websocket.receive_json())
            
            # Check events
            assert len(events) == 3
            assert events[0]["type"] == "tool_call_start"
            assert events[1]["type"] == "tool_call_result"
            assert events[2]["type"] == "final"
            assert events[2]["response"] == "Response to: Test query"


# Test analysis endpoint
@pytest.mark.asyncio
async def test_analyze_endpoint():
    """Test the analysis endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/agent/v1/analyze",
            json={
                "query": "Test query"
            }
        )
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["plan"] == "Test plan"


# Test strategies endpoint
@pytest.mark.asyncio
async def test_strategies_endpoint():
    """Test the strategies endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/agent/v1/strategies")
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "tool_strategies" in data["data"]
        assert "protocol_strategies" in data["data"]


# Test error handling
@pytest.mark.asyncio
async def test_error_handling():
    """Test API error handling."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Test with unsupported protocol
        response = await client.post(
            "/api/agent/v1/respond",
            json={
                "query": "Test query",
                "protocol_type": "unsupported"
            }
        )
        
        # Check response
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Unsupported protocol" in data["detail"]


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])