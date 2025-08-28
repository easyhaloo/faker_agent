# 多协议通信集成

本文档详细介绍了Faker Agent系统的多协议通信支持架构，包括前后端集成、通信流程和技术选型。

## 1. 概述

Faker Agent支持三种通信协议与模式的组合，为不同场景提供最佳用户体验：

| 协议 | 模式 | 特点 | 适用场景 |
|------|------|------|----------|
| HTTP | 同步 | 简单可靠，等待完整响应 | 简单查询，无需实时反馈 |
| SSE  | 流式 | 服务器推送事件流，实时显示执行过程 | 需要实时反馈的复杂任务 |
| WebSocket | 流式 | 双向实时通信，完整工具执行可视化 | 交互式任务，需要实时更新 |

## 2. 架构设计

### 2.1 整体架构

```
+-------------------+                  +-------------------+
|                   |                  |                   |
|  Frontend (React) |<---------------->| Backend (FastAPI) |
|                   |                  |                   |
+-------------------+                  +-------------------+
        |                                       |
        v                                       v
+-------------------+                  +-------------------+
|                   |                  |                   |
|  Protocol Handler |                  |  Protocol Layer   |
|  - HTTP           |                  |  - HTTPProtocol   |
|  - SSE            |                  |  - SSEProtocol    |
|  - WebSocket      |                  |  - WebSocketProt. |
|                   |                  |                   |
+-------------------+                  +-------------------+
        |                                       |
        v                                       v
+-------------------+                  +-------------------+
|                   |                  |                   |
|  Store & UI       |                  |  Agent & Tools    |
|  - AgentStore     |                  |  - Agent          |
|  - StreamingResp. |                  |  - ToolFilter     |
|  - EnhancedChat   |                  |  - Graph          |
|                   |                  |                   |
+-------------------+                  +-------------------+
```

### 2.2 前后端接口定义

所有协议共享相同的基本请求参数结构：

```json
{
  "input": "用户查询内容",
  "conversation_id": "可选的会话ID",
  "protocol": "http|sse|websocket",
  "mode": "sync|stream",
  "filter_strategy": "可选的过滤策略",
  "tool_tags": ["可选的工具标签"],
  "params": {}
}
```

## 3. 通信流程

### 3.1 HTTP同步模式

```
用户 -> 前端 -> HTTP请求 -> 后端处理 -> HTTP响应 -> 前端展示 -> 用户
```

**请求示例**:
```http
POST /api/agent/v1/respond HTTP/1.1
Content-Type: application/json

{
  "input": "今天北京天气怎么样？",
  "protocol": "http",
  "mode": "sync",
  "tool_tags": ["weather"]
}
```

**响应示例**:
```json
{
  "status": "success",
  "data": {
    "task_id": "task-123",
    "response": "北京今天晴朗，温度28-33℃，空气质量良好。"
  }
}
```

### 3.2 SSE流式模式

```
用户 -> 前端 -> HTTP请求 -> 后端处理开始 
                         -> SSE事件1(工具调用) -> 前端实时展示
                         -> SSE事件2(工具结果) -> 前端实时展示
                         -> ... 
                         -> SSE事件N(最终响应) -> 前端展示完整结果 -> 用户
```

**请求示例**:
```http
POST /api/agent/v1/respond HTTP/1.1
Content-Type: application/json

{
  "input": "今天北京天气怎么样？",
  "protocol": "sse",
  "mode": "stream"
}
```

**SSE事件示例**:
```
event: message
data: {"type":"tool_call_start","data":{"task_id":"task-123","tool_call":{"id":"call-1","name":"get_weather","arguments":{"city":"北京"}}}}

event: message
data: {"type":"tool_call_result","data":{"task_id":"task-123","tool_call_id":"call-1","result":{"temp":30,"condition":"晴朗","humidity":45}}}

event: message
data: {"type":"final","data":{"task_id":"task-123","response":"北京今天晴朗，温度30℃，湿度45%。"}}
```

### 3.3 WebSocket流式模式

```
用户 -> 前端 -> WebSocket连接 -> 发送查询 -> 后端处理开始
                                        -> WS消息1(工具调用) -> 前端实时展示
                                        -> WS消息2(工具结果) -> 前端实时展示
                                        -> ...
                                        -> WS消息N(最终响应) -> 前端展示完整结果 -> 用户
```

**WebSocket连接**:
```
连接到: ws://example.com/api/agent/v1/ws
```

**WebSocket消息示例**:
```json
// 客户端发送
{
  "input": "今天北京天气怎么样？",
  "conversation_id": "conv-123",
  "filter_strategy": null,
  "tool_tags": ["weather"]
}

// 服务器响应 (多条消息)
{"type":"tool_call_start","data":{"task_id":"task-123","tool_call":{"id":"call-1","name":"get_weather","arguments":{"city":"北京"}}}}
{"type":"tool_call_result","data":{"task_id":"task-123","tool_call_id":"call-1","result":{"temp":30,"condition":"晴朗","humidity":45}}}
{"type":"final","data":{"task_id":"task-123","response":"北京今天晴朗，温度30℃，湿度45%。"}}
```

## 4. 事件类型定义

系统定义了以下事件类型用于流式通信：

```
TOOL_CALL_START: 工具调用开始
TOOL_CALL_RESULT: 工具调用结果
TOKEN: 文本流标记
FINAL: 最终响应
ERROR: 错误事件
```

## 5. 前后端技术实现

### 5.1 后端实现

* **协议层**: 使用协议工厂模式，根据请求动态创建处理器
* **SSE实现**: 使用 `sse-starlette` 库支持 Server-Sent Events
* **WebSocket实现**: 使用 FastAPI 内置的 WebSocket 支持

### 5.2 前端实现

* **HTTP请求**: 使用 Axios 发送同步请求
* **SSE处理**: 使用原生 EventSource API 处理服务器事件
* **WebSocket处理**: 使用自定义 WebSocketManager 管理连接

## 6. 协议选择策略

系统根据以下因素自动选择或建议合适的协议：

* **任务复杂度**: 简单任务使用 HTTP，复杂任务使用流式协议
* **网络环境**: 不稳定网络优先使用 SSE（自动恢复）
* **交互需求**: 需要实时反馈使用 WebSocket
* **客户端能力**: 根据浏览器支持情况选择协议

## 7. 性能考虑

* **连接复用**: WebSocket 模式下复用连接，减少握手开销
* **流量优化**: 流式模式下使用增量更新，减少数据传输
* **超时处理**: 所有协议都有合理的超时设置和恢复机制
* **降级策略**: 高级协议失败时自动降级到更简单的协议

## 8. 安全考虑

* **认证**: 所有协议支持相同的认证机制
* **数据验证**: 请求和响应数据经过严格验证
* **速率限制**: 针对不同协议设置合适的速率限制
* **超时控制**: 防止长时间占用服务器资源

## 9. 总结

多协议架构为 Faker Agent 提供了灵活的通信选择，使系统能够适应不同的使用场景和网络环境。通过统一的事件模型和清晰的协议分层，确保了前后端集成的一致性和可扩展性。