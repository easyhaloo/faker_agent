

# 🔄 Faker Agent 重构实施计划（Claude Code 专用）

## 🎯 总体目标

* 将现有 `backend` 模块重构为 **职责清晰、分层合理** 的架构。
* 保留 **Faker Agent 六大核心组件**（Registry → Filter → Orchestrator → Assembler → Protocol → API）。
* 落地 **自底向上开发原则**：下层协议先行 → 中间层实现 → 上层适配。
* 避免硬编码，全部配置化，充分使用 LangChain/LiteLLM/LangGraph 提供的能力。
* 请优先使用Langchain提供的工具方法，比如Message State ChatModel Tool 工具调用等

---

## 🧩 分层架构（融合方案）

```
backend/
  core/                     # 核心协议 & 抽象
    contracts/              # ChatTurn, ToolSpec, ExecutionPlan, ModelRequest/Response
    errors.py
  tools/                    # 工具体系
    base.py                 # BaseTool
    registry.py             # ToolRegistry & FilteredToolRegistry
    filters.py              # 各类策略：Threshold/Tag/Priority/Composite
  orchestrator/             # LangGraph Flow Orchestrator
    flow.py                 # FlowOrchestrator + GraphBuilder
    events.py               # 事件类型定义 (tool_call_start, token...)
  assembler/                # LLM-based Assembler
    llm_assembler.py
    models.py               # ToolSpec, ToolChain, ExecutionPlan
  protocol/                 # 协议层
    base.py
    http_protocol.py
    sse_protocol.py
    ws_protocol.py
    factory.py
  infrastructure/           # 外部依赖适配
    llm/
      litellm_client.py     # 优先用 ChatLiteLLM
      litellm_custom.py     # 可选自定义 BaseChatModel
    graph/
      builder.py            # StateGraph + ToolNode
  application/              # 用例编排
    chat/
      service.py
  interface/                # FastAPI 路由
    api/
      routes_agent.py
  config/
    settings.py             # 配置（无硬编码）
  tests/
  docs/
```

---

## 🪜 实施阶段（自底向上）

### 阶段 1：核心协议与错误体系

* 在 `core/contracts/` 定义：

  * `ChatTurn`、`ToolSpec`、`ToolInvocation`
  * `ModelRequest`、`ModelResponse`
  * `ExecutionPlan`、`ToolChain`
* 定义 `LLMPort` 接口：`chat(req: ModelRequest) -> ModelResponse`
* 好处：后续所有模块都依赖这些协议，不会相互耦合。

---

### 阶段 2：工具体系（Registry + Filter）

* 实现 `BaseTool`（标准接口：`name`、`description`、`schema`、`invoke`）。
* 实现 `ToolRegistry`：工具注册/查询。
* 实现 `FilteredToolRegistry`：集成策略。
* 在 `filters.py` 内：

  * `ThresholdToolFilter`
  * `TagToolFilter`
  * `PriorityToolFilter`
  * `CompositeToolFilter`
  * `ToolFilterManager`

---

### 阶段 3：底层 LLM 适配

* 在 `infrastructure/llm/litellm_client.py`：

  * 优先用 **`langchain_litellm.ChatLiteLLM`**
  * 配置通过 `settings.py` 注入（模型名、API Key、Base URL、超时）。
  * 使用 `.bind_tools()` 绑定工具。
* 如需扩展，写 `litellm_custom.py`，继承 `BaseChatModel`，实现 `_generate()`。
* **注意**：严禁硬编码模型名/key。

---

### 阶段 4：LangGraph Flow Orchestrator

* 在 `orchestrator/flow.py`：

  * 定义 `FlowOrchestrator`，用 `StateGraph` 调度。
  * 集成 `ToolNode(tools)`，实现循环（模型 → 工具 → 模型）。
  * 事件流统一封装 `Event` 对象：`tool_call_start`、`tool_call_result`、`token`、`final`、`error`。
* 在 `infrastructure/graph/builder.py`：构建标准 Graph。

---

### 阶段 5：LLM-based Assembler

* 在 `assembler/llm_assembler.py`：

  * 使用 LLM 根据用户输入生成 `ExecutionPlan`。
  * 输出 JSON（符合 `ExecutionPlan` Schema）。
  * 验证工具是否在 `ToolRegistry` 内。
* 在 `models.py`：集中管理数据模型。

---

### 阶段 6：协议层实现

* 在 `protocol/`：

  * `BaseProtocol`（统一接口：`send_event`, `close`）
  * `HTTPProtocol`（一次性返回）
  * `SSEProtocol`（事件流返回）
  * `WebSocketProtocol`（双向通信）
  * `ProtocolFactory`（根据请求类型创建协议对象）

---

### 阶段 7：API 层实现

* 在 `interface/api/routes_agent.py`：

  * `POST /api/agent/v1/respond` → 执行全链路
  * `WS /api/agent/v1/ws` → WebSocket 交互
  * `POST /api/agent/v1/analyze` → 返回 `ExecutionPlan`，不执行
  * `GET /api/agent/v1/strategies` → 策略列表
* 调用 `application/chat/service.py`，只处理 DTO 转换，保持路由瘦身。

---

### 阶段 8：测试与优化

* 单测：

  * contracts schema 校验
  * ToolRegistry/Filter 正确性
  * LLMPort 返回结构完整性
  * Orchestrator 闭环执行
* 集成测：

  * API 全链路请求 → 响应
  * SSE/WS 协议正确流转
* 工具：`pytest + coverage`，目标 80%+

---



## 📝 记忆管理建议（Claude Code 使用提示）

1. **每个阶段任务独立提交** → 避免长上下文丢失。
2. **在实现前，先写测试或接口定义** → 保证接口稳定。
3. **每次遇到错误** → 写入 `docs/ERRORS.md`，Claude Code 需要参考避免重复犯错。
4. **每完成一层** → 更新 `docs/DECISIONS.md`，记录关键架构决策。






# 🛠 Faker Agent 计划

## 一、总体目标

* **模块职责清晰**：每一层代码保持最简洁，避免 cross-layer hack。
* **自底向上开发**：优先实现底层模块（协议、工具接口），再逐层向上。
* **避免 hardcode**：所有配置均通过统一注册与元数据机制管理。
* **高扩展性**：任何新工具、新策略、新协议都能快速接入。
* **LLM驱动**：工具调用与工作流组装完全依赖 langchain/langgraph 提供的能力。

---

## 二、实施步骤

### 1. **基础模块搭建（底层优先）**

1. 创建 `core/protocols/`

   * 定义 `BaseProtocol`（事件流接口：start, stream, end, error）。
   * 实现 `HTTPProtocol`, `SSEProtocol`, `WebSocketProtocol`。
   * 编写 `ProtocolFactory`，基于请求头/参数动态选择协议。

2. 创建 `core/tools/`

   * 定义 `BaseTool`：`name`, `description`, `args_schema`, `run() → ToolResult`。
   * 实现 `ToolRegistry`：统一注册、查询工具。
   * 实现 `FilteredToolRegistry`：可结合过滤策略。

3. 创建 `core/filters/`

   * 定义 `ToolFilterStrategy` 抽象基类。
   * 实现以下策略：

     * `ThresholdToolFilter`
     * `TagToolFilter`
     * `PriorityToolFilter`
     * `CompositeToolFilter`
   * 编写 `ToolFilterManager` 管理组合策略。

---

### 2. **LangGraph 编排层**

1. `flow/orchestrator.py`

   * `FlowOrchestrator`：接收工具链与用户请求，执行工具调用。
   * 定义统一事件类型：`tool_call_start`, `tool_call_result`, `token`, `final`, `error`。
   * 基于 `langgraph` 构建执行 DAG。

2. `flow/graph_builder.py`

   * 提供 `GraphBuilder`：将 `ExecutionPlan` 转换为 LangGraph。

---

### 3. **LLM 组装层**

1. `assembler/llm_assembler.py`

   * `LLMAssembler`：基于 langchain `ChatModel` 扩展，调用 **litellm**。
   * 输入：用户请求 → 输出：`ExecutionPlan`（包含工具链顺序、依赖关系）。

2. 定义数据模型

   * `ToolSpec`（工具元信息）
   * `ToolChain`（有序工具列表）
   * `ExecutionPlan`（整体执行方案）

---

### 4. **API 层**

1. `/api/agent/v1/respond`：主响应接口，支持多协议返回。
2. `/api/agent/v1/ws`：WebSocket交互接口。
3. `/api/agent/v1/analyze`：仅返回执行计划，不执行工具。
4. `/api/agent/v1/strategies`：返回可用策略列表。

---

## 三、开发原则（Claude Code 遵循）

1. **自底向上**：必须先写 `BaseTool` / `BaseProtocol`，再写上层调用。
2. **避免硬编码**：

   * 工具参数通过 `args_schema` 定义
   * 协议通过工厂模式创建
   * 过滤条件通过策略模式实现
3. **三方库优先**：优先使用 `langchain`, `langgraph`, `pydantic`, `fastapi` 提供的机制。
4. **接口对齐**：上层调用严格遵循下层接口，不做跨层适配。
5. **错误记忆与自我纠正**：

   * Claude Code 必须记录已出现的错误（命名、导入、接口不一致）
   * 若遇到相同问题，自动修正，而不是重复错误。

---

## 四、实施阶段计划

* **阶段1**：实现 `core`（protocols, tools, filters）
* **阶段2**：实现 `flow`（orchestrator, graph\_builder）
* **阶段3**：实现 `assembler`（LLMAssembler + 数据模型）
* **阶段4**：实现 `api`（FastAPI endpoints）
* **阶段5**：联调与测试，生成端到端调用流程

---

## 五、交付产物

* **整洁的模块目录**：

  ```
  backend/
    core/
      protocols/
      tools/
      filters/
    flow/
    assembler/
    api/
  ```
* **自动化测试**：每个模块需有单测（pytest）。
* **示例工作流**：天气查询 Demo（调用 WeatherTool → 输出 SSE/HTTP）。




