# API 交互规范文档

## 概述

本文档定义了前后端交互的 API 规范，采用 RESTful 风格设计，确保前后端开发的一致性和可维护性。

## 基础信息

- **基础URL**: `http://localhost:8000/api`
- **数据格式**: JSON
- **认证方式**: Bearer Token (JWT)

## 通用响应格式

所有 API 响应遵循以下统一格式：

```json
{
  "status": "success", // 或 "error"
  "data": {}, // 成功时返回的数据
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述"
  } // 失败时返回的错误信息
}
```

## API 端点

### 1. 智能体交互 API

#### 1.1 发送任务

- **URL**: `/agent/task`
- **方法**: POST
- **描述**: 向智能体发送任务请求
- **请求体**:
  ```json
  {
    "query": "查询北京今天的天气",
    "context": {}, // 可选的上下文信息
    "stream": false // 是否使用流式响应
  }
  ```
- **响应**:
  ```json
  {
    "status": "success",
    "data": {
      "task_id": "task_12345",
      "response": "北京今天天气晴朗，气温25°C-32°C，东南风3-4级。",
      "actions": [] // 智能体执行的动作列表
    }
  }
  ```

#### 1.2 获取任务状态

- **URL**: `/agent/task/{task_id}`
- **方法**: GET
- **描述**: 获取特定任务的执行状态
- **响应**:
  ```json
  {
    "status": "success",
    "data": {
      "task_id": "task_12345",
      "status": "completed", // pending, running, completed, failed
      "progress": 100,
      "result": {} // 任务结果
    }
  }
  ```

#### 1.3 流式响应

- **URL**: `/agent/stream`
- **方法**: POST
- **描述**: 流式处理任务，用于实时反馈
- **请求体**: 同 `/agent/task`
- **响应**: 使用 Server-Sent Events (SSE) 格式返回流式数据

### 2. 工具与插件 API

#### 2.1 获取可用工具列表

- **URL**: `/tools`
- **方法**: GET
- **描述**: 获取所有注册的工具/插件
- **响应**:
  ```json
  {
    "status": "success",
    "data": {
      "tools": [
        {
          "id": "weather_query",
          "name": "天气查询",
          "description": "查询指定城市的天气信息",
          "parameters": {
            "city": {
              "type": "string",
              "description": "城市名称"
            }
          }
        }
      ]
    }
  }
  ```

#### 2.2 调用特定工具

- **URL**: `/tools/{tool_id}`
- **方法**: POST
- **描述**: 直接调用特定工具
- **请求体**:
  ```json
  {
    "parameters": {
      "city": "北京"
    }
  }
  ```
- **响应**:
  ```json
  {
    "status": "success",
    "data": {
      "result": {
        "temperature": "28°C",
        "condition": "晴",
        "humidity": "45%"
      }
    }
  }
  ```

### 3. 天气查询特定 API

#### 3.1 获取城市天气

- **URL**: `/weather/{city}`
- **方法**: GET
- **描述**: 获取指定城市的天气信息
- **响应**:
  ```json
  {
    "status": "success",
    "data": {
      "city": "北京",
      "date": "2025-08-26",
      "temperature": {
        "current": "28°C",
        "min": "25°C",
        "max": "32°C"
      },
      "condition": "晴",
      "humidity": "45%",
      "wind": {
        "direction": "东南风",
        "speed": "3-4级"
      }
    }
  }
  ```

### 4. 系统管理 API

#### 4.1 系统状态

- **URL**: `/system/status`
- **方法**: GET
- **描述**: 获取系统运行状态
- **响应**:
  ```json
  {
    "status": "success",
    "data": {
      "version": "1.0.0",
      "uptime": "2d 5h 30m",
      "memory_usage": "256MB",
      "active_tasks": 2
    }
  }
  ```

## WebSocket 接口

### 实时任务状态更新

- **URL**: `/ws/tasks`
- **描述**: 提供任务状态的实时更新
- **事件类型**:
  - `task_created`: 任务创建
  - `task_updated`: 任务状态更新
  - `task_completed`: 任务完成
  - `task_failed`: 任务失败

## 数据模型

### Task (任务)

```json
{
  "id": "string",
  "query": "string",
  "status": "enum(pending, running, completed, failed)",
  "created_at": "datetime",
  "updated_at": "datetime",
  "result": "object",
  "error": "object"
}
```

### Tool (工具)

```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "parameters": "object",
  "return_schema": "object"
}
```

### WeatherData (天气数据)

```json
{
  "city": "string",
  "date": "date",
  "temperature": {
    "current": "string",
    "min": "string",
    "max": "string"
  },
  "condition": "string",
  "humidity": "string",
  "wind": {
    "direction": "string",
    "speed": "string"
  }
}
```

## 错误码列表

| 错误码 | 描述 |
|--------|------|
| AUTH_FAILED | 认证失败 |
| INVALID_PARAMS | 无效参数 |
| TASK_NOT_FOUND | 任务不存在 |
| TOOL_NOT_FOUND | 工具不存在 |
| RATE_LIMIT | 请求频率超限 |
| SERVER_ERROR | 服务器内部错误 |
| MODEL_ERROR | 模型调用错误 |