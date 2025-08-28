# 通用智能体开发蓝图（前后端分离版）

## 1. 项目目标

构建一个 **通用智能体（类似 Manus.ai）**，特性：

* 前后端分离：**前端 Web (React)**，**后端 Python**
* 核心智能体位于后端，由前端调用
* 模块化 + 插件化，方便扩展
* 渐进式迭代：通过 **能力声明 / 问题声明** 驱动开发

---

## 2. 技术栈

### 前端（Web）

* **框架**：React (可选 Next.js)
* **状态管理**：Redux Toolkit / Zustand
* **UI 框架**：TailwindCSS + shadcn/ui
* **构建工具**：Vite / Next.js 内置工具
* **职责**：

  * 提供用户交互界面
  * 可视化任务管理、插件管理、日志面板
  * 调用后端 API

### 后端（Python）

* **框架**：FastAPI（推荐，支持异步 + OpenAPI）
* **核心模块**：

  * Planner（任务分解） - 已移除，使用 LangGraph 替代
  * Executor（动作执行，工具调用） - 已移除，使用 LangGraph 替代
  * Memory（短期/长期记忆，支持 Redis/向量数据库） - 待实现
  * Registry（工具与插件注册中心） - 已重构为 LangChain 兼容版本
  * Graph（基于 LangGraph 的工作流编排） - 新增
* **职责**：

  * 提供智能体服务与 API
  * 处理前端请求
  * 统一管理插件、工具与执行逻辑

---

## 3. 项目架构

```text
project-root/
├── backend/ (Python)          # 智能体核心 + API 服务
│   ├── core/                  # 核心智能体逻辑
│   │   ├── tools/             # 工具框架（LangChain 兼容）
│   │   ├── graph/             # 基于 LangGraph 的工作流编排
│   │   └── agent.py           # 主智能体类
│   ├── api/                   # FastAPI 路由
│   ├── modules/               # 后端扩展模块（可插拔）
│   └── main.py                # FastAPI 入口
│
├── frontend/ (React)          # Web 前端
│   ├── features/              # 功能模块（任务面板、插件管理、日志）
│   ├── components/            # 原子化 UI 组件
│   ├── services/              # API 调用层
│   └── App.jsx                # React 入口
│
├── docs/                      # 开发文档
│   ├── progress/              # 每次迭代的进度记录
│   └── roadmap.md             # 长期计划
└── ...
```

---

## 4. 模块说明（抽象级别）

### 后端（Python）

* **Tools**（工具框架）

  * 基于 LangChain 的工具接口设计
  * 提供统一的工具注册与管理机制
  * 支持工具参数定义与返回值结构化
  * 可动态转换为 LangChain 工具适配器

* **Graph**（工作流编排）

  * 基于 LangGraph 的智能体工作流设计
  * 支持复杂的状态转换和循环逻辑
  * 可视化智能体执行流程
  * 更好的可控性和调试能力

* **Agent**（主智能体）

  * 使用 LangGraph 编排工具执行流程
  * 接收用户查询并生成响应
  * 管理工具调用和结果处理

* **Registry**（工具注册中心）

  * 统一管理所有可用工具
  * 提供工具发现和获取接口
  * 支持 LangChain 工具适配器

### 前端（Web）

* **Features**

  * 功能区块（任务面板、日志监控、插件管理）
* **Components**

  * 原子 UI 组件（按钮、表单、对话框）
* **Services**

  * 调用后端 API（任务提交、结果查询）

---

## 5. 开发流程（渐进式迭代）

1. **初始化**

   * 定义后端核心接口（Agent/Tools/Graph/Registry）
   * 搭建前端 React 应用框架
   * 建立前后端 API 契约

2. **迭代循环**

   * 写入 **能力声明**（新功能需求）
   * 写入 **问题声明**（需要修复的 Bug）
   * Claude Code 依据声明生成或修改代码
   * 进行集成测试确保功能正常
   * 更新 `docs/progress/日期.md`
   * 更新使用文档，注明如何启动和访问

---

## 6. 进度文档模板

```markdown
# 进度报告 – YYYY-MM-DD

## 新能力声明
- [Backend] Memory 模块支持 Redis 存储
- [Frontend] 新增任务进度面板 (TaskPanel)

## 问题声明
- [Backend] Executor 执行未捕获异常
- [Frontend] API 服务调用缺少错误提示

## 下一步计划
- [Backend] 定义插件接口 (Registry)
- [Frontend] 集成 WebSocket 用于实时任务状态
```

---

## 7. Claude Code 使用示例

* **新增能力**

  > "根据 `能力声明：Memory 模块支持 Redis 存储`，请在 `backend/core/memory/redis_memory.py` 生成实现，并更新 Registry 以支持注册。"

* **修复问题**

  > "根据 `问题声明：Executor 执行未捕获异常`，请修改 `backend/core/executor/base_executor.py`，增加 try/except 与日志记录。"

---

## 8. 工具模块设计理念

工具模块采用 LangChain 兼容设计，具有以下特点：

1. **标准化接口**：所有工具继承自 `BaseTool` 基类，确保统一的接口规范
2. **参数定义**：通过 `ToolParameter` 明确定义工具参数类型和描述
3. **元数据管理**：每个工具包含完整的元数据信息，便于注册和发现
4. **适配器模式**：通过 `LangChainToolAdapter` 将自有工具转换为 LangChain 工具
5. **动态注册**：支持运行时动态注册和发现工具
6. **异步支持**：原生支持异步执行，提高并发性能

工具执行流程：
1. 用户查询通过 Agent 接收
2. Agent 使用 LangGraph 编排工作流
3. Graph 调用 LLM 生成工具调用计划
4. 执行器根据计划调用相应工具
5. 工具执行结果返回给 Agent
6. Agent 整合结果生成最终响应

---

## 9. 更新说明

本次重构主要变更：
- 移除了原有的 Planner 和 Executor 模块
- 引入了基于 LangGraph 的工作流编排机制
- 重构了工具框架，使其兼容 LangChain
- 更新了天气小助手实现，适配新的工具框架
- 修改了 API 接口以适配新的 Agent 实现

---

✨ 总结

* 架构：**前端 Web (React) + 后端 Python (FastAPI)**
* 后端提供智能体核心，前端作为管理与交互界面
* 模块化、可插拔、渐进式迭代
* 开发流程：**能力声明 + 问题声明 → Claude Code 生成实现 → 文档更新**