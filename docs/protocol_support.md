# 多协议通信支持

本文档详细介绍了Faker Agent系统的多协议通信支持，包括实现原理、使用方法和技术细节。

## 1. 概述

Faker Agent支持三种通信协议与模式的组合，为不同场景提供最佳用户体验：

| 协议 | 模式 | 特点 | 适用场景 |
|------|------|------|----------|
| HTTP | 同步 | 简单可靠，等待完整响应 | 简单查询，无需实时反馈 |
| SSE  | 流式 | 服务器推送事件流，实时显示执行过程 | 需要实时反馈的复杂任务 |
| WebSocket | 流式 | 双向实时通信，完整工具执行可视化 | 交互式任务，需要实时更新 |

## 2. 前端实现

### 2.1 核心组件

- **ProtocolSelector**：用户选择通信协议和模式
- **ToolTagSelector**：筛选使用的工具标签
- **StreamingResponse**：显示实时工具执行过程
- **EnhancedChatPanel**：整合多协议UI和流式响应

### 2.2 状态管理

```javascript
// Store状态示例
{
  protocol: 'http',     // http, sse, websocket
  mode: 'sync',         // sync, stream
  toolTags: [],         // 选定的工具标签
  connection: null,     // 当前连接对象
  tasks: {              // 任务执行状态
    'task-123': {
      toolCalls: [],    // 工具调用记录
      status: 'pending' // 任务状态
    }
  }
}
```

### 2.3 通信服务

`AgentService` 类提供三种协议的通信方法：

```javascript
// HTTP同步请求
sendHttpRequest(input, options)

// SSE流式请求
sendSSERequest(input, options)

// WebSocket流式请求
sendWebSocketRequest(input, options)
```

## 3. 工具执行可视化

流式模式（SSE和WebSocket）支持实时工具执行可视化，显示以下信息：

- 工具调用开始事件
- 工具调用参数
- 工具执行结果
- 执行状态和进度

用户可以清晰看到智能体的工作过程，增强透明度和可解释性。

## 4. 数据流

### 4.1 HTTP同步模式

```
用户 -> 前端 -> HTTP请求 -> 后端处理 -> HTTP响应 -> 前端展示 -> 用户
```

### 4.2 SSE流式模式

```
用户 -> 前端 -> HTTP请求 -> 后端处理开始 
                         -> SSE事件1(工具调用) -> 前端实时展示
                         -> SSE事件2(工具结果) -> 前端实时展示
                         -> ... 
                         -> SSE事件N(最终响应) -> 前端展示完整结果 -> 用户
```

### 4.3 WebSocket流式模式

```
用户 -> 前端 -> WebSocket连接 -> 发送查询 -> 后端处理开始
                                        -> WS消息1(工具调用) -> 前端实时展示
                                        -> WS消息2(工具结果) -> 前端实时展示
                                        -> ...
                                        -> WS消息N(最终响应) -> 前端展示完整结果 -> 用户
```

## 5. WebSocket连接管理

WebSocket连接通过专用的`WebSocketManager`管理，提供以下功能：

- 自动重连机制（指数退避策略）
- 连接状态监控
- 错误处理和恢复
- 事件订阅模式

## 6. 工具标签过滤

系统支持通过工具标签过滤智能体可用的工具集：

- 用户可选择特定标签组合
- 后端根据标签限制可用工具
- 减少不必要的工具调用，提升相关性

## 7. 使用示例

### 7.1 基本用法

1. 选择协议和模式（默认HTTP同步）
2. 可选：选择工具标签过滤
3. 输入查询内容并发送
4. 流式模式下可实时查看工具执行过程

### 7.2 场景推荐

- **简单问答**：使用HTTP同步模式
- **复杂查询**：使用SSE流式模式，查看工具执行过程
- **持续交互**：使用WebSocket流式模式，获得最佳实时体验

## 8. 后续计划

- [ ] 增加连接状态指示器
- [ ] 支持流式响应的部分渲染（逐字显示）
- [ ] 添加工具执行时间统计
- [ ] 实现中断请求功能

## 9. 技术细节

### 9.1 事件类型

系统定义了以下事件类型用于流式通信：

```javascript
EventType = {
  TOOL_CALL_START: 'tool_call_start',   // 工具调用开始
  TOOL_CALL_RESULT: 'tool_call_result', // 工具调用结果
  TOKEN: 'token',                       // 文本流标记
  FINAL: 'final',                       // 最终响应
  ERROR: 'error'                        // 错误事件
}
```

### 9.2 连接状态

WebSocket连接状态包括：

```javascript
ConnectionState = {
  DISCONNECTED: 'disconnected',   // 未连接
  CONNECTING: 'connecting',       // 连接中
  CONNECTED: 'connected',         // 已连接
  RECONNECTING: 'reconnecting',   // 重连中
  ERROR: 'error'                  // 错误状态
}
```

## 10. 总结

多协议支持为Faker Agent提供了灵活的通信方式，结合工具执行可视化，大幅提升了系统的透明度和用户体验。用户可以根据具体场景选择最合适的协议和模式，获得最佳交互体验。