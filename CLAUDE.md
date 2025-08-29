# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Faker Agent is a modular, extensible intelligent agent platform with FastAPI backend and React frontend. The system uses LiteLLM for flexible LLM integration and UV for Python dependency management.

The architecture follows a clear separation between frontend (React) and backend (Python), with the core intelligence residing in the backend and the frontend providing the user interface for interaction and visualization.

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
# Run Python tests
uv run pytest

# Run specific test files
uv run pytest tests/core/filters/test_tool_filter_strategy.py -v
```

## Architecture Overview

### Core Components

The system implements a modular agent architecture with the following main components:

1. **Agent** (`backend/core/agent.py`) - Main intelligent agent that orchestrates tool execution using LangGraph
2. **Tools** (`backend/core/tools/`) - LangChain-compatible tool framework with unified registry and management
3. **Graph** (`backend/core/graph/`) - LangGraph-based workflow orchestration for complex state transitions
4. **Memory** (`backend/core/memory/`) - Short-term/long-term memory management (supporting Redis/vector databases)
5. **Registry** (`backend/core/tools/registry.py`) - Centralized tool and plugin registry with LangChain compatibility

Note: The previous Planner and Executor modules have been removed and replaced with LangGraph-based orchestration.

### Request Flow

1. User query received via API endpoints
2. Agent uses LangGraph to orchestrate tool execution workflow
3. Tools are dynamically selected and executed based on LLM decisions
4. Results are collected and processed by the Agent
5. Final response is generated and returned to the user
6. Conversation context is maintained in memory for continuity

### Module System

Extensions are added as modules in `backend/modules/`. Each module can:
- Register tools in the global registry
- Provide API endpoints via FastAPI routers
- Define custom data models and logic
- Implement specialized functionality (e.g., weather lookup, web search)

Example: Weather module provides weather lookup functionality through both direct API and agent tool integration.

### Frontend Architecture

React frontend uses:
- **Zustand** for state management
- **TailwindCSS** for styling
- **Axios** for API communication
- **Vite** for build tooling

Features are organized in `frontend/src/features/` with reusable components in `frontend/src/components/`.

Key frontend features include:
- Task panel for managing agent tasks
- Plugin management interface
- Log monitoring dashboard
- Real-time task status visualization

## Key Configuration

### Backend Settings (`backend/config/settings.py`)
- LiteLLM model configuration (default: gpt-3.5-turbo)
- LiteLLM custom endpoint URL support via `LITELLM_BASE_URL`
- CORS origins for frontend integration
- API prefixes and endpoints
- Environment-based configuration via `.env`

### Development vs Production
- Development: CORS allows localhost:5173
- API documentation available at `/docs` and `/redoc`
- Debug logging enabled by default

## Important Files

- `backend/main.py` - FastAPI application entry point
- `backend/core/agent.py` - Main agent orchestration logic using LangGraph
- `backend/core/tools/` - LangChain-compatible tool framework
- `backend/core/graph/` - LangGraph-based workflow orchestration
- `backend/config/settings.py` - Configuration management
- `frontend/src/App.jsx` - React application entry point
- `pyproject.toml` - Python project configuration and dependencies
- `docs/progress/` - Progress documentation for each iteration
- `docs/roadmap.md` - Long-term development roadmap

## Development Patterns

### Adding New Tools

The tool framework is designed with LangChain compatibility and follows these principles:
1. Standardized Interface: All tools inherit from `BaseTool` base class
2. Parameter Definition: Use `ToolParameter` to define tool parameters clearly
3. Metadata Management: Each tool includes complete metadata for registration and discovery
4. Adapter Pattern: `LangChainToolAdapter` converts proprietary tools to LangChain tools
5. Dynamic Registration: Support runtime dynamic tool registration and discovery
6. Async Support: Native asynchronous execution support for better performance

Steps to add new tools:
1. Create tool class inheriting from `BaseTool` in `backend/core/tools/`
2. Define tool parameters using the `get_parameters()` method
3. Implement the async `run()` method with tool logic
4. Register tool instance in `backend/core/tools/registry.py`
5. Add API routes if direct access is needed
6. Update frontend services if UI integration is required

### Error Handling
- All API responses use consistent format with `status`, `data`, and `error` fields
- Backend uses structured logging with appropriate log levels
- Frontend should handle both success and error response formats
- Tools should gracefully handle exceptions and return meaningful error messages

### Memory Management  
- Conversation context automatically maintained by memory module
- Each query gets unique task_id and optional conversation_id
- Memory supports multiple backends (in-memory, Redis, vector databases)
- Long-term memory capabilities for knowledge retention

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

Focus areas for future development:
- WebSocket support for real-time streaming
- Persistent memory backends (Redis, PostgreSQL, etc.)
- Vector database integration for semantic search
- Comprehensive test coverage
- Advanced plugin system with lifecycle management
- Multi-agent collaboration capabilities

## Development Workflow (Progressive Iteration)

1. **Initialization**
   - Define backend core interfaces (Agent/Tools/Graph/Registry)
   - Set up frontend React application framework
   - Establish API contracts between frontend and backend

2. **Iteration Cycle**
   - Write **Capability Declarations** (new feature requirements)
   - Write **Problem Statements** (bugs to fix)
   - Claude Code generates or modifies code based on declarations
   - Perform integration testing to ensure functionality
   - Update `docs/progress/YYYY-MM-DD.md` with changes
   - Update documentation with usage instructions

## Tool Module Design Philosophy

Tools modules use a LangChain-compatible design with the following characteristics:

1. **Standardized Interface**: All tools inherit from `BaseTool` base class for uniform interface
2. **Parameter Definition**: Clear parameter definitions using `ToolParameter`
3. **Metadata Management**: Complete metadata for each tool to facilitate registration and discovery
4. **Adapter Pattern**: `LangChainToolAdapter` bridges proprietary tools with LangChain
5. **Dynamic Registration**: Runtime registration and discovery of tools
6. **Async Support**: Native async execution support for improved concurrency

Tool execution flow:
1. User query received by Agent
2. Agent uses LangGraph to orchestrate workflow
3. Graph invokes LLM to generate tool calling plan
4. Executor invokes appropriate tools based on plan
5. Tool execution results returned to Agent
6. Agent integrates results to generate final response