# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Faker Agent is a modular, extensible intelligent agent platform with FastAPI backend and React frontend. The system uses LiteLLM for flexible LLM integration and UV for Python dependency management.

## Common Development Commands

### Environment Setup
```bash
# Setup backend (Windows)
setup_uv.bat

# Setup backend (Unix/Linux/Mac) 
pip install uv
uv venv
uv pip install -e .

# Create environment file
cp backend/.env.example backend/.env
# Edit backend/.env to add your API keys (LITELLM_API_KEY, WEATHER_API_KEY)

# Setup frontend
cd frontend
npm install
```

### Development Servers
```bash
# Start backend (from project root)
cd backend
uvicorn main:app --reload
# Backend runs at http://localhost:8000

# Start frontend (from project root)
cd frontend
npm run dev
# Frontend runs at http://localhost:5173
```

### Code Quality
```bash
# Format Python code
uv run black backend/

# Sort imports
uv run isort backend/

# Type checking
uv run mypy backend/

# Format and build frontend
cd frontend
npm run build
```

### Testing
```bash
# Run Python tests (when added)
uv run pytest

# No tests currently exist - this is an area for development
```

## Architecture Overview

### Core Components

The system implements a modular agent architecture with four main components:

1. **Planner** (`backend/core/planner/`) - Breaks down user queries into executable plans
2. **Executor** (`backend/core/executor/`) - Executes plans by calling tools and services
3. **Memory** (`backend/core/memory/`) - Maintains conversation context and history
4. **Registry** (`backend/core/registry/`) - Manages available tools and plugins

### Request Flow

1. User query received via `/api/agent/task` endpoint
2. Agent stores query in memory and creates execution plan
3. Executor runs plan steps, calling registered tools as needed
4. Final response returned with actions taken
5. Response stored in memory for context

### Module System

Extensions are added as modules in `backend/modules/`. Each module can:
- Register tools in the global registry
- Provide API endpoints via FastAPI routers
- Define custom data models and logic

Example: Weather module provides weather lookup functionality through both direct API and agent tool integration.

### Frontend Architecture

React frontend uses:
- **Zustand** for state management
- **TailwindCSS** for styling
- **Axios** for API communication
- **Vite** for build tooling

Features are organized in `frontend/src/features/` with reusable components in `frontend/src/components/`.

## Key Configuration

### Backend Settings (`backend/config/settings.py`)
- LiteLLM model configuration (default: gpt-3.5-turbo)
- CORS origins for frontend integration
- API prefixes and endpoints
- Environment-based configuration via `.env`

### Development vs Production
- Development: CORS allows localhost:5173
- API documentation available at `/docs` and `/redoc`
- Debug logging enabled by default

## Important Files

- `backend/main.py` - FastAPI application entry point
- `backend/core/agent.py` - Main agent orchestration logic  
- `backend/config/settings.py` - Configuration management
- `frontend/src/App.jsx` - React application entry point
- `pyproject.toml` - Python project configuration and dependencies
- `docs/architecture.md` - Detailed Chinese architecture documentation
- `docs/api_spec.md` - Comprehensive API specification

## Development Patterns

### Adding New Tools
1. Create tool class inheriting from base classes in `backend/core/`
2. Register tool in `backend/core/registry/base_registry.py`
3. Add API routes if direct access needed
4. Update frontend services if UI integration required

### Error Handling
- All API responses use consistent format with `status`, `data`, and `error` fields
- Backend uses structured logging with appropriate log levels
- Frontend should handle both success and error response formats

### Memory Management  
- Conversation context automatically maintained by memory module
- Each query gets unique task_id and optional conversation_id
- Memory currently uses simple in-memory storage (can be extended to Redis/DB)

## API Integration

Backend provides RESTful API at `/api` prefix:
- `/api/agent/task` - Submit queries to the agent
- `/api/tools` - List available tools
- `/api/weather/{city}` - Direct weather lookup
- `/api/system/status` - System health check

Full API specification available in `docs/api_spec.md`.

## Extension Points

The system is designed for extensibility:
- Add new modules in `backend/modules/`
- Extend core components by inheriting from base classes
- Register new tools via the registry system
- Add frontend features in `src/features/`

Focus areas for future development include WebSocket support for streaming, persistent memory backends, and comprehensive test coverage.
