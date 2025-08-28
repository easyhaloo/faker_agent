# Faker Agent 系统架构

本文档描述了 Faker Agent 系统的整体架构、核心模块和技术栈。

## 1. 系统概述

Faker Agent 是一个模块化、可扩展的智能体系统，采用前后端分离架构。系统能够根据用户指令执行各种任务，支持多种通信协议，并提供友好的用户界面。

### 1.1 核心特性

- **前后端分离**：前端使用 React，后端使用 Python (FastAPI)
- **多协议支持**：HTTP、SSE、WebSocket
- **工具系统**：基于 LangChain 兼容的工具框架
- **工作流编排**：基于 LangGraph 的智能体工作流
- **可视化执行**：实时显示工具调用过程
- **模块化设计**：支持插件式扩展

## 2. 系统架构图

```
+-------------------+      +---------------------+
|                   |      |                     |
|   Frontend (Web)  +<---->+   Backend (Python)  |
|                   |      |                     |
+--------+----------+      +---------+-----------+
         ^                           ^
         |                           |
         v                           v
+--------+----------+      +---------+-----------+
|                   |      |                     |
|  UI Components    |      |   Core Modules      |
|  - Chat Panel     |      |   - Agent           |
|  - Tool Panel     |      |   - Graph           |
|  - Settings       |      |   - Tools           |
|                   |      |   - Registry        |
+--------+----------+      +---------+-----------+
         ^                           ^
         |                           |
         v                           v
+--------+----------+      +---------+-----------+
|                   |      |                     |
|  Services         |      |   API Endpoints     |
|  - Agent Service  |      |   - /respond        |
|  - API Client     |      |   - /analyze        |
|  - WS Manager     |      |   - /tools          |
|                   |      |                     |
+-------------------+      +---------------------+
```

## 3. 核心模块

### 3.1 前端模块

#### 3.1.1 UI 组件

- **EnhancedChatPanel**：聊天界面，支持多协议和工具可视化
- **ProtocolSelector**：协议和模式选择组件
- **ToolTagSelector**：工具标签过滤组件
- **StreamingResponse**：流式响应和工具执行可视化组件

#### 3.1.2 服务层

- **AgentService**：与后端智能体通信，支持多种协议
- **WebSocketManager**：WebSocket 连接管理，支持自动重连
- **ApiClient**：基于 Axios 的 API 客户端

#### 3.1.3 状态管理

- **AgentStore**：基于 Zustand 的状态管理，包含：
  - 消息历史
  - 协议设置
  - 工具标签
  - 任务状态

### 3.2 后端模块

#### 3.2.1 核心组件

- **Agent**：主智能体，协调工具调用和响应生成
- **Graph**：基于 LangGraph 的工作流编排
- **Registry**：工具注册中心，管理可用工具
- **ToolFilter**：工具过滤层，基于策略过滤工具

#### 3.2.2 协议层

- **BaseProtocol**：协议基类
- **HTTPProtocol**：HTTP 协议实现
- **SSEProtocol**：SSE 协议实现
- **WebSocketProtocol**：WebSocket 协议实现

#### 3.2.3 工具系统

- **BaseTool**：工具基类
- **ToolParameter**：工具参数定义
- **LangChainToolAdapter**：LangChain 工具适配器

## 4. 通信流程

### 4.1 HTTP 同步模式

```
用户 -> 前端 -> HTTP请求 -> 后端处理 -> HTTP响应 -> 前端展示 -> 用户
```

### 4.2 SSE 流式模式

```
用户 -> 前端 -> HTTP请求 -> 后端处理开始 
                         -> SSE事件1(工具调用) -> 前端实时展示
                         -> SSE事件2(工具结果) -> 前端实时展示
                         -> ... 
                         -> SSE事件N(最终响应) -> 前端展示完整结果 -> 用户
```

### 4.3 WebSocket 流式模式

```
用户 -> 前端 -> WebSocket连接 -> 发送查询 -> 后端处理开始
                                        -> WS消息1(工具调用) -> 前端实时展示
                                        -> WS消息2(工具结果) -> 前端实时展示
                                        -> ...
                                        -> WS消息N(最终响应) -> 前端展示完整结果 -> 用户
```

## 5. 技术栈

### 5.1 前端技术栈

- **框架**：React
- **状态管理**：Zustand
- **UI 框架**：TailwindCSS + shadcn/ui
- **HTTP 客户端**：Axios
- **构建工具**：Vite

### 5.2 后端技术栈

- **框架**：FastAPI
- **LLM 工具链**：LangChain, LangGraph
- **异步支持**：asyncio
- **WebSocket**：websockets
- **SSE**：sse-starlette

## 6. 文件结构

```
project-root/
├── backend/ (Python)          # 智能体核心 + API 服务
│   ├── core/                  # 核心智能体逻辑
│   │   ├── tools/             # 工具框架
│   │   ├── graph/             # 工作流编排
│   │   ├── protocols/         # 协议实现
│   │   └── agent.py           # 主智能体类
│   ├── api/                   # FastAPI 路由
│   ├── modules/               # 后端扩展模块（可插拔）
│   └── main.py                # FastAPI 入口
│
├── frontend/ (React)          # Web 前端
│   ├── src/
│   │   ├── components/        # UI 组件
│   │   │   ├── chat/          # 聊天相关组件
│   │   │   ├── ui/            # 通用 UI 组件
│   │   │   └── ...
│   │   ├── services/          # API 服务
│   │   ├── store/             # 状态管理
│   │   └── App.jsx            # 入口组件
│   └── ...
│
├── docs/                      # 文档目录
└── ...
```

## 7. 未来扩展

系统设计支持以下扩展方向：

- **记忆模块**：支持会话历史和上下文管理
- **多模态支持**：图像、音频等多模态输入处理
- **工具市场**：允许用户自定义和分享工具
- **自动化测试**：端到端测试框架
- **监控系统**：性能和错误监控