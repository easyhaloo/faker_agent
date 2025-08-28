# Faker Agent 协议使用指南

Faker Agent 支持多种协议与智能体交互，本指南详细说明如何使用这些协议。

## 支持的协议

Faker Agent 支持三种主要协议：

1. **HTTP 协议**：适用于简单请求，一次性返回完整响应
2. **SSE (Server-Sent Events) 协议**：适用于流式响应，实时显示进度
3. **WebSocket 协议**：适用于双向通信，支持复杂交互

## HTTP 协议

HTTP 协议是最简单的交互方式，适合简单查询和不需要实时反馈的场景。

### 请求格式

```http
POST /api/agent/v1/respond HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "input": "查询内容",
  "protocol": "http",
  "mode": "sync",
  "filter_strategy": "threshold_5",
  "tool_tags": ["weather"]
}
```

### 响应格式

```json
{
  "status": "success",
  "data": {
    "response": "最终响应内容",
    "tool_calls": [
      {
        "tool_name": "weather_query",
        "tool_args": {"city": "Beijing"},
        "tool_call_id": "call_123",
        "status": "completed",
        "result": {"temperature": "28°C", "condition": "晴"}
      }
    ],
    "execution_time": 1.23
  }
}
```

### 使用示例

#### curl

```bash
curl -X POST http://localhost:8000/api/agent/v1/respond \
  -H "Content-Type: application/json" \
  -d '{
    "input": "北京的天气怎么样？",
    "protocol": "http",
    "mode": "sync"
  }'
```

#### JavaScript

```javascript
async function queryAgent() {
  const response = await fetch("/api/agent/v1/respond", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      input: "北京的天气怎么样？",
      protocol: "http",
      mode: "sync"
    })
  });
  
  const result = await response.json();
  console.log(result.data.response);
}
```

#### Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/agent/v1/respond",
    json={
        "input": "北京的天气怎么样？",
        "protocol": "http",
        "mode": "sync"
    }
)

result = response.json()
print(result["data"]["response"])
```

## SSE 协议

SSE (Server-Sent Events) 协议允许服务器向客户端推送事件流，非常适合实时显示工具执行进度和生成响应。

### 请求格式

```http
POST /api/agent/v1/respond HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "input": "查询内容",
  "protocol": "sse",
  "mode": "stream",
  "filter_strategy": "threshold_5",
  "tool_tags": ["weather"]
}
```

### 响应格式

SSE 响应以 `data:` 开头的事件流形式返回：

```
data: {"type":"tool_call_start","tool_name":"weather_query","tool_args":{"city":"Beijing"},"tool_call_id":"call_123","timestamp":1598012345.67}

data: {"type":"tool_call_result","tool_name":"weather_query","tool_call_id":"call_123","result":{"temperature":"28°C","condition":"晴"},"timestamp":1598012346.12}

data: {"type":"final","response":"北京今天天气晴朗，温度28°C。","timestamp":1598012346.34}
```

### 使用示例

#### JavaScript

```javascript
// 创建 EventSource 对象
const eventSource = new EventSource(
  "/api/agent/v1/respond?protocol=sse&mode=stream"
);

// 处理事件
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch (data.type) {
    case "tool_call_start":
      console.log(`开始调用工具: ${data.tool_name}`);
      updateUI("正在查询中...");
      break;
    
    case "tool_call_result":
      console.log(`工具结果: ${JSON.stringify(data.result)}`);
      updateUI(`获取到数据: ${data.result.temperature}`);
      break;
    
    case "token":
      // 处理流式 token
      appendText(data.token);
      break;
    
    case "final":
      console.log(`最终响应: ${data.response}`);
      updateUI(data.response, true);
      eventSource.close();
      break;
    
    case "error":
      console.error(`错误: ${data.error}`);
      updateUI(`出错了: ${data.error}`, true);
      eventSource.close();
      break;
  }
};

// 发送请求
fetch("/api/agent/v1/respond", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    input: "北京的天气怎么样？",
    protocol: "sse",
    mode: "stream"
  })
});
```

## WebSocket 协议

WebSocket 协议提供全双工通信通道，适合需要持续双向通信的场景。

### 连接

```javascript
const socket = new WebSocket("ws://localhost:8000/api/agent/v1/ws");
```

### 请求格式

```json
{
  "input": "查询内容",
  "conversation_id": "可选会话ID",
  "filter_strategy": "threshold_5",
  "tool_tags": ["weather"]
}
```

### 响应格式

WebSocket 服务器以 JSON 消息形式发送响应：

```json
{"type":"tool_call_start","tool_name":"weather_query","tool_args":{"city":"Beijing"},"tool_call_id":"call_123"}
```

```json
{"type":"tool_call_result","tool_name":"weather_query","tool_call_id":"call_123","result":{"temperature":"28°C","condition":"晴"}}
```

```json
{"type":"final","response":"北京今天天气晴朗，温度28°C。"}
```

### 使用示例

#### JavaScript

```javascript
// 创建 WebSocket 连接
const socket = new WebSocket("ws://localhost:8000/api/agent/v1/ws");

// 连接建立时发送请求
socket.onopen = () => {
  console.log("WebSocket 连接已建立");
  
  socket.send(JSON.stringify({
    input: "北京的天气怎么样？",
    conversation_id: "session123",
    tool_tags: ["weather"]
  }));
};

// 处理接收到的消息
socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch (data.type) {
    case "tool_call_start":
      console.log(`开始调用工具: ${data.tool_name}`);
      break;
    
    case "tool_call_result":
      console.log(`工具结果: ${JSON.stringify(data.result)}`);
      break;
    
    case "token":
      // 处理流式 token
      appendText(data.token);
      break;
    
    case "final":
      console.log(`最终响应: ${data.response}`);
      socket.close();
      break;
    
    case "error":
      console.error(`错误: ${data.error}`);
      socket.close();
      break;
  }
};

// 处理错误
socket.onerror = (error) => {
  console.error("WebSocket 错误:", error);
};

// 处理连接关闭
socket.onclose = () => {
  console.log("WebSocket 连接已关闭");
};
```

## 性能与选择建议

### 选择合适的协议

- **HTTP 协议**：适用于简单、短期查询，不需要实时反馈
- **SSE 协议**：适用于需要实时显示进度的长时间查询，如天气预报、数据分析
- **WebSocket 协议**：适用于需要持续交互的复杂场景，如对话式聊天

### 性能考虑

1. **HTTP 协议**
   - 优点：简单，兼容性好
   - 缺点：每次请求都需要建立新连接，延迟较高

2. **SSE 协议**
   - 优点：单向流式传输，延迟低，适合实时更新
   - 缺点：仅支持服务器到客户端的通信

3. **WebSocket 协议**
   - 优点：双向通信，延迟最低，适合实时交互
   - 缺点：稍微复杂，可能需要处理连接维护

### 最佳实践

1. 对于简单查询，使用 HTTP 协议
2. 对于需要显示进度的查询，使用 SSE 协议
3. 对于复杂对话场景，使用 WebSocket 协议
4. 总是处理错误和连接关闭情况
5. 使用合适的 `filter_strategy` 和 `tool_tags` 减少不必要的工具调用

## 故障排除

### 常见 SSE 问题

1. **连接超时**
   - SSE 连接默认有超时限制，长时间无响应可能导致连接关闭
   - 解决方案：实现重连逻辑或使用保活机制

2. **事件解析错误**
   - 确保正确解析 `event.data` 为 JSON

### 常见 WebSocket 问题

1. **连接关闭**
   - WebSocket 连接可能因网络问题或服务器重启而关闭
   - 解决方案：实现自动重连机制

2. **消息顺序**
   - 处理消息时注意依赖关系，确保按正确顺序处理