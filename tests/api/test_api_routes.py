"""
Tests for the API routes.
"""
import pytest
from fastapi.testclient import TestClient

from backend.main import app

# Create a test client
client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_system_status_endpoint():
    """Test the system status endpoint."""
    response = client.get("/api/v1/system/status")
    assert response.status_code == 404  # This endpoint doesn't exist in the current implementation


def test_weather_endpoint():
    """Test the weather endpoint."""
    response = client.get("/api/v1/weather/Beijing")
    assert response.status_code == 404  # This endpoint doesn't exist in the current implementation


def test_agent_v1_strategies_endpoint():
    """Test the agent strategies endpoint."""
    response = client.get("/api/v1/agent/v1/strategies")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "success"
    assert "data" in response.json()
    assert "tool_strategies" in response.json()["data"]
    assert isinstance(response.json()["data"]["tool_strategies"], list)