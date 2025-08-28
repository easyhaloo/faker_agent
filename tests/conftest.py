"""
Pytest configuration file.
"""
import asyncio
import os
import sys
from pathlib import Path

import pytest

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))


# Create an event loop for async tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Set up test environment variables
@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    # Set test-specific environment variables
    os.environ["TESTING"] = "1"
    os.environ["LITELLM_API_KEY"] = "test_key"
    os.environ["WEATHER_API_KEY"] = "test_key"
    
    yield
    
    # Clean up
    os.environ.pop("TESTING", None)