@echo off
echo Running Faker Agent tests...

REM Activate the virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM Install test dependencies if needed
pip install pytest pytest-asyncio httpx

REM Run the tests
pytest tests -v

echo Tests completed!