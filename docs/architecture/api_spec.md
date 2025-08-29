# Faker Agent API 规范

## 概述

Faker Agent 提供了一组 REST API 和 WebSocket 接口，用于与智能体交互。API 前缀为 `/api`，主要智能体接口位于 `/api/agent/v1/` 路径下。

## 通用响应格式

所有 HTTP API 返回统一的 JSON 格式：

```json
{
  "status": "success" | "error",
  "data": { ... },  // 成功时返回数据
  "error": {        // 出错时返回错误信息
    "code": "ERROR_CODE",
    "message": "错误信息"
  }
}
```

## 智能体 API

### 1. 向智能体发送查询

**请求**:
- **URL**: `/api/agent/v1/respond`
- **方法**: POST
- **内容类型**: application/json

**请求体**:
```json
{
  "input": "用户输入查询",
  "conversation_id": "可选会话ID",
  "protocol": "http" | "sse" | "websocket",
  "mode": "sync" | "stream",
  "filter_strategy": "可选过滤策略名称",
  "tool_tags": ["可选工具标签"],
  "params": { 
    // 额外参数
  }
}
```

**响应**:
- **HTTP 模式**: 返回完整 JSON 响应
```json
{
  "status": "success",
  "data": {
    "response": "智能体响应",
    "tool_calls": [
      {
        "tool_name": "工具名称",
        "tool_args": { ... },
        "tool_call_id": "调用ID",
        "status": "started" | "completed",
        "result": { ... },
        "error": "可选错误信息"
      }
    ],
    "execution_time": 1.23
  }
}
```

- **SSE 模式**: 返回事件流，每个事件为 JSON 对象
```
data: {"type":"tool_call_start","tool_name":"工具名称","tool_args":{...},"tool_call_id":"调用ID"}

data: {"type":"tool_call_result","tool_name":"工具名称","tool_call_id":"调用ID","result":{...}}

data: {"type":"final","response":"最终响应"}
```

### 2. WebSocket 接口

**连接**:
- **URL**: `/api/agent/v1/ws`
- **协议**: WebSocket

**请求消息**:
```json
{
  "input": "用户输入查询",
  "conversation_id": "可选会话ID",
  "filter_strategy": "可选过滤策略名称",
  "tool_tags": ["可选工具标签"],
  "params": { 
    // 额外参数
  }
}
```

**响应消息**:
```json
{
  "type": "tool_call_start" | "tool_call_result" | "token" | "final" | "error",
  // 根据类型包含不同字段
}
```

### 3. 分析查询（不执行）

**请求**:
- **URL**: `/api/agent/v1/analyze`
- **方法**: POST
- **内容类型**: application/json

**请求体**:
```json
{
  "input": "用户输入查询"
}
```

**响应**:
```json
{
  "status": "success",
  "data": {
    "query": "原始查询",
    "plan": {
      "query": "原始查询",
      "tools": [
        {
          "tool_name": "工具名称",
          "parameters": { ... }
        }
      ]
    }
  }
}
```

### 4. 获取可用过滤策略

**请求**:
- **URL**: `/api/agent/v1/strategies`
- **方法**: GET

**响应**:
```json
{
  "status": "success",
  "data": {
    "strategies": ["threshold_5", "priority", "tag_weather"]
  }
}
```

## 工具 API

### 1. 获取可用工具列表

**请求**:
- **URL**: `/api/tools`
- **方法**: GET

**响应**:
```json
{
  "status": "success",
  "data": {
    "tools": [
      {
        "name": "工具名称",
        "description": "工具描述",
        "parameters": [ ... ],
        "tags": ["标签1", "标签2"],
        "priority": 10
      }
    ]
  }
}
```

### 2. 天气 API

**请求**:
- **URL**: `/api/weather/{city}`
- **方法**: GET
- **参数**:
  - `city`: 城市名称（路径参数）
  - `country`: 国家代码（可选查询参数）

**响应**:
```json
{
  "status": "success",
  "data": {
    "city": "城市名",
    "temperature": {
      "current": "当前温度",
      "min": "最低温度",
      "max": "最高温度"
    },
    "condition": "天气状况",
    "humidity": "湿度",
    "wind": {
      "direction": "风向",
      "speed": "风速"
    }
  }
}
```

## 系统 API

### 1. 健康检查

**请求**:
- **URL**: `/`
- **方法**: GET

**响应**:
```json
{
  "status": "online",
  "version": "版本号"
}
```

### 2. 系统状态

**请求**:
- **URL**: `/api/system/status`
- **方法**: GET

**响应**:
```json
{
  "status": "success",
  "data": {
    "version": "版本号",
    "uptime": "运行时间",
    "memory_usage": "内存使用",
    "active_tasks": 5
  }
}
```
