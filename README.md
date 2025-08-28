# Faker Agent

A modular, extensible intelligent agent platform with FastAPI backend and React frontend.

## Features

- Modular architecture with plug-and-play components
- LiteLLM integration for flexible LLM support
- FastAPI backend with OpenAPI documentation
- React frontend with Zustand state management
- UV-based dependency management

## Quick Start

### Backend Setup

1. Install UV and set up the environment:

```bash
# On Windows
setup_uv.bat

# On Unix/Linux/Mac
pip install uv
uv venv
uv pip install -e .
```

2. Create a `.env` file from the example:

```bash
cp backend/.env.example backend/.env
```

3. Edit `.env` to add your API keys.

4. Start the backend:

```bash
cd backend
uvicorn main:app --reload
```

The API will be available at http://localhost:8000.

### Frontend Setup

1. Install frontend dependencies:

```bash
cd frontend
npm install
```

2. Start the development server:

```bash
npm run dev
```

The frontend will be available at http://localhost:5173.

## One-Click Startup Scripts

To simplify the development workflow, we provide one-click startup scripts that launch both the backend and frontend services simultaneously:

### For Unix/Linux/macOS Users

```bash
./start_dev.sh
```

This script will:
- Start the backend server (http://localhost:8000)
- Start the frontend development server (http://localhost:5173)
- Display both service addresses
- Handle graceful shutdown when you press Ctrl+C

### For Windows Users

```cmd
start_dev.bat
```

This script will:
- Open separate command windows for backend and frontend services
- Start the backend server (http://localhost:8000)
- Start the frontend development server (http://localhost:5173)
- Display service addresses in each window

Both scripts require the individual setup steps (UV installation, npm install, .env configuration) to be completed first.

## Development

### Project Structure

```
faker_agent/
├── backend/                # FastAPI backend
│   ├── core/               # Core modules
│   ├── api/                # API routes
│   └── modules/            # Extension modules
├── frontend/               # React frontend
│   ├── src/                # Source code
│   │   ├── components/     # UI components
│   │   ├── features/       # Feature modules
│   │   └── services/       # API services
├── docs/                   # Documentation
```

### API Documentation

When running the backend, the OpenAPI documentation is available at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## License

MIT