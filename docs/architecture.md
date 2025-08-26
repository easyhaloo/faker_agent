# 智能体架构文档

## 整体架构

本项目为通用智能体平台，采用前后端分离架构：
- **前端**：React 应用，提供用户交互界面
- **后端**：FastAPI 服务，包含智能体核心逻辑
- **大模型集成**：通过 LiteLLM 框架实现，支持多模型接入
- **环境管理**：基于 UV 工具实现 Python 包管理

## 目录结构

```
faker_agent/
├── backend/                # 后端代码（Python FastAPI）
│   ├── core/               # 核心智能体逻辑
│   │   ├── planner/        # 任务规划模块
│   │   ├── executor/       # 执行模块
│   │   ├── memory/         # 记忆模块
│   │   └── registry/       # 插件/工具注册中心
│   ├── api/                # API 路由定义
│   ├── modules/            # 功能模块，如天气查询模块
│   ├── config/             # 配置文件
│   └── main.py             # 应用入口
│
├── frontend/               # 前端代码（React）
│   ├── src/
│   │   ├── features/       # 功能模块
│   │   ├── components/     # UI 组件
│   │   ├── services/       # API 服务调用
│   │   └── App.jsx         # 应用入口
│   ├── public/             # 静态资源
│   └── package.json        # 依赖配置
│
└── docs/                   # 项目文档
    ├── architecture.md     # 架构文档
    ├── api_spec.md         # API 交互规范
    └── progress/           # 进度记录
```

## 核心模块

### 后端

1. **Planner 模块**
   - 职责：将用户自然语言任务分解为步骤流
   - 实现：基于 LiteLLM 调用大模型，生成任务执行计划

2. **Executor 模块**
   - 职责：执行任务步骤，调用工具和服务
   - 实现：支持 API 调用、本地函数执行、插件调用

3. **Memory 模块**
   - 职责：维护对话历史和上下文
   - 实现：支持短期内存和长期存储

4. **Registry 模块**
   - 职责：管理和调用各种工具/插件
   - 实现：提供统一的注册和发现机制

### 前端

1. **Features 模块**
   - 任务面板：展示和管理任务
   - 对话界面：与智能体交互
   - 插件管理：查看和配置可用插件

2. **Components 模块**
   - 基础 UI 组件集合
   - 遵循 TailwindCSS + shadcn/ui 规范

3. **Services 模块**
   - API 调用封装
   - WebSocket 连接管理（用于实时更新）

## 技术栈详情

### 后端技术栈

- **主框架**：FastAPI
- **大模型接入**：LiteLLM
- **依赖管理**：UV
- **数据存储**：SQLite（开发阶段）/ Redis（可选）

### 前端技术栈

- **主框架**：React
- **构建工具**：Vite
- **状态管理**：Zustand
- **UI 框架**：TailwindCSS + shadcn/ui
- **HTTP 客户端**：Axios

## 部署架构

开发阶段，前后端可独立运行：
- 后端：FastAPI 服务，默认端口 8000
- 前端：Vite 开发服务器，默认端口 5173

生产环境下的推荐部署方式：
- 后端部署为独立服务
- 前端静态文件由 Nginx/CDN 提供服务
- 可选容器化部署（Docker）