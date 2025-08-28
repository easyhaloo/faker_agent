# Faker Agent

一个模块化、可扩展的智能体系统，支持多种协议和工具过滤策略。

## 特性

- **多协议支持**：HTTP、SSE 和 WebSocket
- **工具过滤层**：支持多种策略过滤工具集
- **LangGraph 工作流**：基于 LangGraph 的流程编排
- **LLM-based Assembler**：将用户输入转化为工具链
- **模块化设计**：易于扩展的插件架构
- **流式输出**：支持实时反馈和进度展示
- **LiteLLM 集成**：灵活的 LLM 支持
- **FastAPI 后端**：支持 OpenAPI 文档
- **React 前端**：使用 Zustand 状态管理
- **UV 依赖管理**：现代化的依赖管理

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
│   │   ├── registry/       # Tool registry
│   │   ├── filters/        # Tool filter strategies
│   │   ├── graph/          # LangGraph orchestration
│   │   ├── assembler/      # LLM-based assembler
│   │   ├── protocol/       # Protocol handlers
│   │   └── tools/          # Base tool definitions
│   ├── api/                # API routes
│   └── modules/            # Extension modules
│       └── weather/        # Weather tool example
├── frontend/               # React frontend
│   ├── src/                # Source code
│   │   ├── components/     # UI components
│   │   ├── features/       # Feature modules
│   │   └── services/       # API services
├── docs/                   # Documentation
│   ├── architecture.md     # Architecture documentation
│   ├── api_spec.md         # API specification
│   ├── guide.md            # User guide
│   ├── protocol_guide.md   # Protocol guide
│   └── progress/           # Progress reports
└── tests/                  # Test suite
```

### API Documentation

When running the backend, the OpenAPI documentation is available at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 文档

- [使用指南](docs/guide.md) - 详细使用说明
- [API 规范](docs/api_spec.md) - API 接口文档
- [架构设计](docs/architecture.md) - 系统架构说明
- [协议指南](docs/protocol_guide.md) - 协议使用详解
- [进度报告](docs/progress/) - 开发进度记录

## 架构

Faker Agent 由以下核心组件组成：

1. **Tool Registry**：工具注册与管理中心
2. **Tool Filter & Strategy Layer**：工具过滤策略层
3. **LangGraph Flow Orchestrator**：工作流编排器
4. **LLM-based Assembler**：工具链组装器
5. **Protocol Layer**：统一协议层
6. **API 接口**：FastAPI 路由及端点

## 示例请求

```bash
curl -X POST http://localhost:8000/api/agent/v1/respond \
  -H "Content-Type: application/json" \
  -d '{
    "input": "北京的天气怎么样？",
    "protocol": "http",
    "mode": "sync"
  }'
```

## 贡献

欢迎通过 Issue 或 Pull Request 参与贡献。

## 许可

[MIT 许可证](LICENSE)