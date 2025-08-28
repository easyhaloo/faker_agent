# Faker Agent 架构设计

## 总体架构

Faker Agent 是一个模块化、可扩展的智能体系统，具有以下核心组件：

1. **Tool Registry**：工具注册与管理中心
2. **Tool Filter & Strategy Layer**：工具过滤策略层
3. **LangGraph Flow Orchestrator**：基于 LangGraph 的工作流编排器
4. **LLM-based Assembler**：将用户输入转化为工具链的组装器
5. **Protocol Layer**：统一协议层，支持 HTTP/SSE/WebSocket
6. **API 接口**：FastAPI 路由及端点

## 组件详解

### 1. Tool Registry

工具注册中心负责管理所有可用的工具，提供统一的注册、查询和列出工具的接口。主要包括：

- **BaseTool**：所有工具的基类，提供统一接口
- **ToolRegistry**：基础工具注册表
- **FilteredToolRegistry**：增强版注册表，支持过滤策略

工具定义包含名称、描述、参数定义、标签和优先级等元数据，便于智能体发现和调用。

### 2. Tool Filter & Strategy Layer

工具过滤策略层负责在 LangGraph 编排前对工具集合进行预选择，减少工具绑定数量，提高效率。

- **ToolFilterStrategy**：过滤策略基类
- **ThresholdToolFilter**：限制工具数量的策略
- **TagToolFilter**：基于标签的过滤策略
- **PriorityToolFilter**：基于优先级的过滤策略
- **CompositeToolFilter**：组合多种过滤策略
- **ToolFilterManager**：管理多种过滤策略

### 3. LangGraph Flow Orchestrator

基于 LangGraph 的工作流编排器，负责编排工具执行流程和生成统一事件流。

- **FlowOrchestrator**：核心编排器，管理工具执行流程
- **Event Types**：统一事件类型定义（tool_call_start, tool_call_result, token, final, error）
- **Graph Builder**：构建 LangGraph 工作流图

### 4. LLM-based Assembler

LLM-based Assembler 负责将用户输入转化为可执行的工具链。

- **LLMAssembler**：核心组装器，使用 LLM 生成工具调用计划
- **ToolSpec**：工具规范数据模型
- **ToolChain**：工具链数据模型
- **ExecutionPlan**：执行计划数据模型

### 5. Protocol Layer

协议层负责将工作流生成的事件流转换为不同协议格式，支持多种前端交互方式。

- **BaseProtocol**：协议基类
- **HTTPProtocol**：HTTP 协议处理器
- **SSEProtocol**：Server-Sent Events 协议处理器
- **WebSocketProtocol**：WebSocket 协议处理器
- **ProtocolFactory**：协议工厂，动态创建协议处理器

### 6. API 接口

FastAPI 路由及端点，提供统一的 API 接口供前端调用。

- **/api/agent/v1/respond**：主要智能体响应端点，支持多种协议
- **/api/agent/v1/ws**：WebSocket 端点
- **/api/agent/v1/analyze**：分析端点，不执行工具但返回执行计划
- **/api/agent/v1/strategies**：策略列表端点

## 数据流

1. 用户输入通过 API 接口发送到后端
2. LLM-based Assembler 将输入转化为工具链
3. Tool Filter 根据策略过滤可用工具
4. Flow Orchestrator 编排工具执行流程
5. 工具执行结果通过 Protocol Layer 转换为对应协议格式
6. 响应返回给前端

## 扩展点

1. **新工具**：继承 BaseTool 实现新工具，并注册到 Registry
2. **新过滤策略**：继承 ToolFilterStrategy 实现新策略
3. **新协议**：继承 BaseProtocol 实现新协议
4. **新模块**：在 modules 目录下添加新模块，提供专用功能
