# Faker Agent 开发指南

## 1. 项目概述

Faker Agent 是一个模块化、可扩展的智能体平台，具有以下特性：

* **前后端分离架构**：前端使用 React，后端使用 Python (FastAPI)
* **多协议支持**：支持 HTTP、SSE 和 WebSocket 三种通信协议
* **工具系统**：基于 LangChain 兼容的工具框架，支持工具注册和发现
* **工作流编排**：使用 LangGraph 进行智能体工作流编排
* **流式响应**：支持工具执行可视化和实时响应
* **模块化设计**：插件化架构，便于扩展和定制

## 2. 技术栈

### 前端 (Web)
* **框架**：React
* **状态管理**：Zustand
* **UI 框架**：TailwindCSS + shadcn/ui
* **构建工具**：Vite
* **通信**：支持 HTTP、SSE 和 WebSocket

### 后端 (Python)
* **框架**：FastAPI
* **核心模块**：
  * Graph：基于 LangGraph 的工作流编排
  * Tools：工具框架（LangChain 兼容）
  * Registry：工具注册中心
  * Protocols：多协议支持层
* **异步支持**：使用 asyncio 和 FastAPI 的异步特性

## 3. 项目结构

```
project-root/
├── backend/               # 后端代码
│   ├── core/              # 核心模块
│   │   ├── tools/         # 工具框架
│   │   ├── graph/         # 工作流编排
│   │   ├── protocols/     # 协议实现
│   │   └── agent.py       # 主智能体类
│   ├── api/               # API 路由
│   ├── modules/           # 扩展模块
│   └── main.py            # 入口文件
│
├── frontend/              # 前端代码
│   ├── src/
│   │   ├── components/    # UI 组件
│   │   │   ├── chat/      # 聊天相关组件
│   │   │   └── ui/        # 通用 UI 组件
│   │   ├── services/      # API 服务
│   │   ├── store/         # 状态管理
│   │   └── App.jsx        # 入口组件
│   └── ...
│
├── docs/                  # 文档中心
│   ├── architecture/      # 架构文档
│   ├── backend/           # 后端文档
│   ├── frontend/          # 前端文档
│   ├── design/            # 设计文档
│   ├── standards/         # 规范文档
│   ├── progress/          # 进度文档
│   └── README.md          # 文档说明
│
└── CLAUDE.md              # Claude Code 指导文档
```

## 4. 开发流程

### 4.1 渐进式迭代

1. **需求分析**：明确本次迭代的目标和范围
2. **能力声明**：描述需要新增的功能和能力
3. **问题声明**：描述需要修复的问题和改进点
4. **开发实现**：根据声明进行代码开发
5. **测试验证**：确保功能正常工作
6. **文档更新**：更新相关文档
7. **提交代码**：提交变更并记录进度

### 4.2 文档驱动开发

* 每个重要功能应先编写设计文档
* 代码变更应伴随文档更新
* 使用进度文档记录迭代内容

## 5. 文档规范

### 5.1 文档目录

文档按照以下结构组织：

```
docs/
├── architecture/       # 架构文档
├── backend/            # 后端文档
├── frontend/           # 前端文档
├── design/             # 设计文档
├── standards/          # 规范文档
├── progress/           # 进度文档
└── README.md           # 文档说明
```

### 5.2 文档类型

* **架构文档**：系统整体架构、模块划分、技术选型
* **后端/前端文档**：具体模块的技术实现和使用方法
* **设计文档**：UI设计、用户体验、工作流程
* **规范文档**：代码风格、提交规范、文档规范
* **进度文档**：记录迭代进度和功能更新

### 5.3 进度文档模板

进度文档使用以下模板，按日期命名为 `YYYY-MM-DD.md`：

```markdown
# 进度报告 – YYYY-MM-DD

## 新能力声明
- [模块] 功能描述
- [模块] 功能描述

## 已完成工作
- 详细说明实现内容
- 代码变更说明
- 新增文件/模块

## 问题声明
- [模块] 问题描述
- [模块] 问题描述

## 下一步计划
- [模块] 计划任务
- [模块] 计划任务
```

## 6. 代码规范

### 6.1 通用规范

* 每个文件专注于单一职责
* 使用有意义的描述性名称
* 代码应自解释，注释解释"为什么"而非"做什么"
* 所有公共 API 应有文档注释

### 6.2 后端代码规范 (Python)

* 遵循 PEP 8 规范
* 使用 Black 和 isort 格式化代码
* 使用类型注解
* 命名约定：
  * 模块名：小写下划线，如 `tool_registry.py`
  * 类名：驼峰命名，如 `ToolRegistry`
  * 函数/方法名：小写下划线，如 `register_tool`
  * 常量名：大写下划线，如 `MAX_RETRY_COUNT`

### 6.3 前端代码规范 (JavaScript/TypeScript)

* 使用 ESLint 和 Prettier
* 首选 TypeScript 而非 JavaScript
* 使用函数组件和 Hooks
* 命名约定：
  * 组件文件：PascalCase，如 `Button.tsx`
  * 服务/工具文件：camelCase，如 `apiClient.ts`
  * 组件名：PascalCase，如 `ToolPanel`
  * 函数名/变量名：camelCase，如 `fetchData`

## 7. 工具和服务集成

### 7.1 多协议支持

Faker Agent 支持三种通信协议：

* **HTTP (同步模式)**：简单查询，无需实时反馈
* **SSE (流式模式)**：实时显示执行过程
* **WebSocket (流式模式)**：双向实时通信

每种协议支持不同的使用场景，前端可根据需要选择适当的协议。

### 7.2 工具系统

工具系统基于 LangChain 兼容设计：

* 所有工具继承自 `BaseTool` 基类
* 通过 `ToolParameter` 定义参数
* 工具支持标签和元数据
* 支持动态注册和发现

### 7.3 工作流编排

使用 LangGraph 进行工作流编排：

* 支持复杂的状态转换和循环逻辑
* 可视化执行流程
* 支持工具调用和结果处理

## 8. 开发示例

### 8.1 能力声明示例

> 根据 `能力声明：前端支持多协议通信`，请在 `frontend/src/services/agentService.js` 中实现 HTTP/SSE/WebSocket 协议支持，并更新相关组件。

### 8.2 问题声明示例

> 根据 `问题声明：WebSocket 连接在某些网络环境下不稳定`，请在 `frontend/src/services/connectionManager.js` 中增强重连逻辑和错误处理。

## 9. 命名和位置约定

### 9.1 文档命名和位置

* **架构文档**：`docs/architecture/[topic].md`
* **模块文档**：`docs/[backend|frontend]/[module].md`
* **规范文档**：`docs/standards/[topic].md`
* **进度文档**：`docs/progress/YYYY-MM-DD.md`

### 9.2 代码文件命名和位置

* **后端模块**：`backend/core/[module]/[file].py`
* **API 路由**：`backend/api/[resource].py`
* **前端组件**：`frontend/src/components/[type]/[Component].jsx`
* **前端服务**：`frontend/src/services/[service].js`

## 10. 总结

Faker Agent 是一个强大的模块化智能体平台，通过多协议支持和工具系统提供灵活的扩展能力。开发时应遵循文档驱动和渐进式迭代的方法，确保代码质量和文档完整性。通过统一的规范和约定，保持项目的一致性和可维护性。