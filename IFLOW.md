# Faker Agent 项目概述

Faker Agent 是一个模块化、可扩展的智能体系统，支持多种协议和工具过滤策略。它使用 FastAPI 作为后端框架，React 作为前端框架，并集成了 LiteLLM 和 LangGraph 来处理 LLM 相关功能。

## 项目结构

```
faker_agent/
├── backend/                # FastAPI 后端
│   ├── core/               # 核心模块
│   │   ├── registry/       # 工具注册中心
│   │   ├── filters/        # 工具过滤策略
│   │   ├── graph/          # LangGraph 编排器
│   │   ├── assembler/      # LLM-based 组装器
│   │   ├── protocol/       # 协议处理器
│   │   ├── services/       # 服务层
│   │   └── tools/          # 基础工具定义
│   ├── api/                # API 路由
│   └── modules/            # 扩展模块
│       └── weather/        # 天气工具示例
├── frontend/               # React 前端
│   ├── src/                # 源代码
│   │   ├── components/     # UI 组件
│   │   ├── features/       # 功能模块
│   │   └── services/       # API 服务
├── docs/                   # 文档
│   ├── architecture/       # 架构文档
│   ├── backend/            # 后端文档
│   ├── frontend/           # 前端文档
│   ├── design/             # 设计文档
│   ├── standards/          # 标准文档
│   └── progress/           # 进度报告
└── tests/                  # 测试套件
```

## 构建和运行

### 后端设置

1. 安装 UV 并设置环境：

```bash
# 在 Windows 上
setup_uv.bat

# 在 Unix/Linux/Mac 上
pip install uv
uv venv
uv pip install -e .
```

2. 从示例创建 `.env` 文件：

```bash
cp backend/.env.example backend/.env
```

3. 编辑 `.env` 文件以添加您的 API 密钥。

4. 启动后端：

```bash
cd backend
uvicorn main:app --reload
```

后端 API 将在 http://localhost:8000 可用。

### 前端设置

1. 安装前端依赖：

```bash
cd frontend
npm install
```

2. 启动开发服务器：

```bash
npm run dev
```

前端将在 http://localhost:5173 可用。

### 一键启动脚本

为了简化开发流程，我们提供了一键启动脚本，可以同时启动后端和前端服务：

#### 对于 Unix/Linux/macOS 用户

```bash
./start_dev.sh
```

此脚本将：
- 启动后端服务器 (http://localhost:8000)
- 启动前端开发服务器 (http://localhost:5173)
- 显示两个服务地址
- 在您按 Ctrl+C 时处理优雅关闭

#### 对于 Windows 用户

```cmd
start_dev.bat
```

此脚本将：
- 打开单独的命令窗口用于后端和前端服务
- 启动后端服务器 (http://localhost:8000)
- 启动前端开发服务器 (http://localhost:5173)
- 在每个窗口中显示服务地址

这两个脚本都需要先完成单独的设置步骤（UV 安装、npm install、.env 配置）。

## 开发约定

### 后端开发

- 使用 FastAPI 作为主要的 Web 框架
- 使用 Pydantic 进行数据验证
- 使用 LiteLLM 集成各种 LLM 模型
- 使用 LangGraph 进行工作流编排
- 遵循模块化设计，便于扩展新工具和功能

### 前端开发

- 使用 React 作为主要的前端框架
- 使用 Zustand 进行状态管理
- 使用 Tailwind CSS 进行样式设计
- 使用 Vite 作为构建工具

### API 文档

运行后端时，OpenAPI 文档在以下位置可用：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 核心组件

1. **Tool Registry**：工具注册与管理中心
2. **Tool Filter & Strategy Layer**：工具过滤策略层
3. **LangGraph Flow Orchestrator**：工作流编排器
4. **LLM-based Assembler**：工具链组装器
5. **Protocol Layer**：统一协议层
6. **API 接口**：FastAPI 路由及端点