@echo off
echo Setting up UV environment for Faker Agent...

:: Install UV if not already installed
pip install uv

:: Create and activate virtual environment
echo Creating virtual environment...
uv venv

:: Install dependencies
echo Installing dependencies from pyproject.toml...
uv pip install -e .

echo UV environment setup complete!
echo To activate the environment, run: .venv\Scripts\activate