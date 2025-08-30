# Faker Agent 架构设计总结

## 核心目标

- 构建模块化、可扩展的智能体平台，前后端分离
- 前端（React）提供用户交互界面，后端（Python/FastAPI）提供智能体核心
- 保留六大核心组件：Registry → Filter → Orchestrator → Assembler → Protocol → API
- 实现自底向上开发，避免硬编码，全部配置化

## 分层架构

```
backend/
  core/                     # 核心协议和抽象
    contracts/              # 基础数据模型
    errors.py
  tools/                    # 工具体系
    base.py                 # BaseTool
    registry.py             # ToolRegistry
    filters.py              # 工具过滤策略
  orchestrator/             # 基于LangGraph的流程编排
    flow.py
    events.py
  assembler/                # LLM组装器
    llm_assembler.py
    models.py
  protocol/                 # 协议层（HTTP/SSE/WS）
    base.py
    http_protocol.py
    sse_protocol.py
    ws_protocol.py
  infrastructure/           # 外部依赖适配
    llm/
    graph/
  application/              # 应用层服务
  interface/                # API接口
    api/
  config/                   # 配置管理
```

## 实施阶段（自底向上）

1. **核心协议与错误体系**
   - 定义基础数据模型：`ChatTurn`, `ToolSpec`, `ModelRequest/Response`, `ExecutionPlan`
   - 定义统一接口，确保各模块解耦

2. **工具体系（Registry + Filter）**
   - 实现 `BaseTool` 和 `ToolRegistry`
   - 实现工具过滤策略：`ThresholdToolFilter`, `TagToolFilter`, `PriorityToolFilter`

3. **LLM适配**
   - 优先使用 `langchain_litellm.ChatLiteLLM`
   - 配置通过 `settings.py` 注入，严禁硬编码

4. **LangGraph流程编排**
   - 使用 `StateGraph` 实现工具调用流程
   - 统一事件处理：`tool_call_start`, `tool_call_result`, `token`等

5. **LLM组装器**
   - 使用LLM生成 `ExecutionPlan`
   - 确保工具在 `ToolRegistry` 中可用

6. **协议层**
   - 实现 `BaseProtocol` 及具体协议：HTTP, SSE, WebSocket
   - 使用工厂模式创建协议对象

7. **API层**
   - 实现主要端点：`/api/agent/v1/respond`, `/api/agent/v1/ws`等
   - 保持路由瘦身，业务逻辑放在service层

8. **测试与优化**
   - 单元测试和集成测试
   - 使用 `pytest + coverage`，目标覆盖率80%+

## 开发原则

1. **自底向上**：先实现底层协议，再逐层向上
2. **避免硬编码**：通过配置和元数据管理一切
3. **三方库优先**：充分利用 `langchain`, `langgraph`, `pydantic`, `fastapi`
4. **职责明确**：每层代码保持简洁，避免跨层hack
5. **接口对齐**：上层严格遵循下层接口

## 工具模块设计

- **标准化接口**：所有工具继承自 `BaseTool`
- **参数定义**：通过 `ToolParameter` 明确定义参数
- **元数据管理**：包含完整元数据便于注册和发现
- **适配器模式**：通过 `LangChainToolAdapter` 转换为LangChain工具
- **动态注册**：支持运行时注册和发现
- **异步支持**：原生支持异步执行

## 实施建议

- 每个阶段任务独立提交，避免长上下文丢失
- 先写测试或接口定义，保证接口稳定
- 记录错误和架构决策，避免重复犯错
- 定期更新进度文档

# Phase 3 Implementation Plan - Protocol Layer

## Overview

This document outlines the implementation plan for Phase 3 of the Faker Agent refactoring, focusing on the Protocol Layer components. The Protocol Layer is responsible for handling different communication protocols between the client and the Faker Agent system, enabling flexible interaction patterns such as HTTP request-response, SSE streaming, and WebSocket bidirectional communication.

## Protocol Layer Architecture

### Core Components

1. **BaseProtocol**
   - Abstract base class defining the interface for all protocol handlers
   - Key methods: `handle_events`, `format_event`, `format_error`
   - Ensures consistency across all protocol implementations

2. **Protocol Implementations**
   - **HTTPProtocol**: Traditional request-response HTTP communication
   - **SSEProtocol**: Server-Sent Events for streaming responses
   - **WebSocketProtocol**: Real-time bidirectional communication
   - Each implementation handles protocol-specific formatting and delivery

3. **ProtocolFactory**
   - Factory pattern for creating protocol handlers based on type
   - Centralizes protocol instance management
   - Allows runtime registration of new protocol handlers

4. **FilteredProtocolRegistry**
   - Extends ProtocolFactory with filtering capabilities
   - Provides dynamic enabling/disabling of protocols
   - Applies filter strategies to control protocol availability

5. **Protocol Contracts**
   - `ProtocolType`: Enum of supported protocol types
   - `ProtocolRequest`: Base model for protocol-specific requests
   - `ProtocolResponse`: Base model for protocol-specific responses
   - Protocol-specific request/response models for each protocol type

### Protocol Filter System

1. **ProtocolFilterStrategy**
   - Abstract base class for protocol filtering strategies
   - Key method: `should_allow` to determine if a protocol should be available

2. **Filter Strategy Implementations**
   - **AllowAllProtocolFilter**: Permits all protocols (default)
   - **DenyAllProtocolFilter**: Blocks all protocols
   - **WhitelistProtocolFilter**: Allows only specific protocols
   - **BlacklistProtocolFilter**: Blocks specific protocols
   - **CompositeProtocolFilter**: Combines multiple strategies

3. **FilterManager**
   - Manages both tool and protocol filtering strategies
   - Provides methods to create, register, and apply filter strategies
   - Serves as the central point for filtering configuration

### Data Flow

1. **Request Processing**
   - Client connects with a specific protocol type (HTTP, SSE, WebSocket)
   - API layer identifies protocol type and forwards to protocol handler
   - FilteredProtocolRegistry checks if protocol is enabled and passes filters
   - Appropriate protocol handler processes the request

2. **Event Handling**
   - Events generated by the agent/graph are passed to protocol handler
   - Protocol handler formats events according to protocol specifications
   - Formatted events are delivered to the client based on protocol semantics

3. **Response Delivery**
   - HTTP: Collects all events and returns a single JSON response
   - SSE: Streams events as they occur, formatted as SSE messages
   - WebSocket: Sends events as they occur as WebSocket messages

## Implementation Files

- `backend/core/contracts/protocol.py`: Protocol-related data models
- `backend/core/protocol/base_protocol.py`: Base protocol interface
- `backend/core/protocol/http_protocol.py`: HTTP protocol implementation
- `backend/core/protocol/sse_protocol.py`: SSE protocol implementation
- `backend/core/protocol/websocket_protocol.py`: WebSocket protocol implementation
- `backend/core/protocol/protocol_factory.py`: Protocol factory
- `backend/core/protocol/filtered_registry.py`: Filtered protocol registry
- `backend/core/filters/protocol_filter_strategy.py`: Protocol filter strategies
- `backend/core/filters/filter_manager.py`: Combined filter manager

## Benefits

1. **Flexibility**: Support multiple communication protocols without code duplication
2. **Extensibility**: Easy addition of new protocols through the factory pattern
3. **Consistency**: Unified event handling across all protocols
4. **Security**: Filter system to control protocol availability
5. **Performance**: Protocol-specific optimizations for different use cases

## Next Steps (After Phase 3)

1. Develop the API layer with FastAPI endpoints that leverage the Protocol Layer
2. Implement protocol-specific middleware for request processing
3. Create client SDKs that can work with different protocols
4. Add monitoring and metrics for protocol performance

# Phase 2 Implementation Plan - Orchestrator and LLM Integration

## Overview

This document outlines the implementation plan for Phase 2 of the Faker Agent refactoring, focusing on the Orchestrator and LLM integration components. Phase 1 established the core contracts, tools, and filtering systems. Phase 2 will build on this foundation to implement the LangGraph-based orchestration layer and enhanced LLM integration.

## Components to Implement

### 1. LangGraph Flow Orchestrator

The LangGraph Flow Orchestrator will be responsible for managing the execution flow of tools and LLM interactions. It will use the LangGraph library to define a graph-based workflow that coordinates tool execution based on LLM decisions.

**Key Files to Implement/Update:**
- `backend/core/graph/flow_orchestrator.py`: Core orchestrator implementation
- `backend/core/graph/event_types.py`: Event type definitions
- `backend/core/graph/agent_graph.py`: Graph definition and builder

**Key Features:**
- Support for streaming events during execution
- Tool filtering via filter strategies
- Event-based architecture for real-time updates
- Integration with the tool registry

### 2. LLM Integration Layer

The LLM Integration Layer will provide a unified interface to various LLM providers through LiteLLM, allowing the system to work with different models seamlessly.

**Key Files to Implement/Update:**
- `backend/core/infrastructure/llm/litellm_client.py`: LiteLLM adapter
- `backend/core/infrastructure/llm/factory.py`: Factory for creating LLM clients
- `backend/core/infrastructure/llm/llm_port_impl.py`: Implementation of the LLM interface

**Key Features:**
- Configuration-driven model selection
- Support for tool binding
- Unified response format
- Error handling and retry mechanisms

### 3. LLM-based Assembler

The Assembler will use an LLM to generate execution plans based on user queries, determining which tools to use and in what order.

**Key Files to Implement/Update:**
- `backend/core/assembler/llm_assembler.py`: Main assembler implementation
- `backend/core/assembler/tool_spec.py`: Tool specification adapter

**Key Features:**
- LLM-driven planning
- Tool selection based on query
- Validation against available tools
- Structured execution plan generation

## Implementation Sequence

1. **Update LLM Integration**
   - Enhance the existing LiteLLM client with improved error handling
   - Implement streaming support for token-by-token responses
   - Add configuration validation and logging

2. **Implement Flow Orchestrator**
   - Create the core `FlowOrchestrator` class with LangGraph integration
   - Implement the event system for real-time updates
   - Add support for tool filtering via the filter manager
   - Implement both synchronous and streaming interfaces

3. **Develop LLM Assembler**
   - Create the `LLMAssembler` class for generating execution plans
   - Implement the plan validation logic
   - Add support for plan optimization
   - Ensure compatibility with the tools registry

4. **Integration and Testing**
   - Connect all components
   - Implement comprehensive testing
   - Create example workflows
   - Document usage patterns

## Technical Details

### Graph Structure

The LangGraph flow will follow this structure:
```
User Input → LLM (Plan) → Tools Execution → LLM (Synthesis) → Response
```

Key nodes in the graph:
- **LLM Node**: Handles LLM interactions for planning and synthesis
- **Tool Node**: Executes tools based on LLM decisions
- **Router Node**: Determines the next step based on conditions

### Event System

Events will be emitted during execution to provide real-time updates to clients:
- `ToolCallStartEvent`: When a tool execution begins
- `ToolCallResultEvent`: When a tool execution completes
- `TokenEvent`: When a token is generated by the LLM
- `FinalEvent`: When the execution completes
- `ErrorEvent`: When an error occurs

### Configuration

The system will be configurable through settings:
- LLM provider and model selection
- API credentials
- Default temperature and token limits
- Timeout settings
- Streaming options

## Next Steps (After Phase 2)

1. Implement the Protocol layer for different client communication methods (HTTP, SSE, WebSocket)
2. Develop the API layer with FastAPI endpoints
3. Implement the memory system for conversation context
4. Add advanced features like conversational memory and reasoning capabilities

## Conclusion

Phase 2 will establish the orchestration backbone of the Faker Agent system, allowing tools to be executed in a coordinated manner based on LLM-driven planning. This implementation follows the self-bottom-up development principle, building on the foundation established in Phase 1.