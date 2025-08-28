#!/bin/bash
echo "Running Faker Agent tests..."

# Activate the virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# Install test dependencies if needed
pip install pytest pytest-asyncio httpx

# Run the tests
pytest tests -v

echo "Tests completed!"