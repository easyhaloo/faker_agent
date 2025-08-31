# 前端响应适配器 (Response Adapter)

## 概述

响应适配器是一个统一处理后端API响应的工具，它确保前端能够处理多种响应格式，并在遇到空响应或错误时提供合适的用户反馈。主要解决了以下问题：

1. 统一不同格式的API响应
2. 处理空响应或错误情况
3. 提供友好的错误和兜底消息
4. 简化前端组件对响应的处理逻辑

## 目录结构

```
frontend/src/services/
├── responseAdapter.js  # 响应适配器核心模块
├── apiClient.ts        # API客户端，使用响应适配器处理响应
└── agentService.js     # 智能体服务，使用响应适配器处理各种协议的响应
```

## 核心功能

### 1. 响应适配 (adaptAgentResponse)

将不同格式的响应转换为统一的格式：

```javascript
{
  status: 'success' | 'error' | 'loading',
  data: {
    response: string,      // 文本响应
    tool_calls: array,     // 工具调用结果
    execution_time: number // 执行时间
  },
  error: null | {          // 错误信息（仅当status为error时）
    code: string,
    message: string
  }
}
```

### 2. 空响应处理

当API返回空响应时，适配器会自动提供兜底消息：

- 空响应："AI暂时无法回答您的问题，请稍后重试。"
- 错误响应："处理您的请求时出现了问题，请检查您的输入并重试。"
- 超时响应："请求超时，请检查网络连接并重试。"

### 3. 实用工具函数

- `extractTextResponse`: 从适配后的响应中提取文本内容
- `extractToolCalls`: 从适配后的响应中提取工具调用结果
- `isErrorResponse`: 检查响应是否为错误
- `isEmptyResponse`: 检查响应是否为空
- `createLoadingResponse`: 创建加载状态的响应对象

## 使用方法

### 基本用法

```javascript
import { adaptAgentResponse, extractTextResponse } from '../services/responseAdapter';

// 处理API响应
const rawResponse = await fetch('/api/agent/respond').then(r => r.json());
const adaptedResponse = adaptAgentResponse(rawResponse);

// 提取文本响应
const responseText = extractTextResponse(adaptedResponse);
```

### 自定义兜底消息

```javascript
import { adaptAgentResponse, DEFAULT_FALLBACK_MESSAGES } from '../services/responseAdapter';

// 自定义兜底消息
const customFallbacks = {
  ...DEFAULT_FALLBACK_MESSAGES,
  empty: "我现在无法回答这个问题，请换一种方式提问。",
  error: "出错了，请稍后再试。"
};

// 使用自定义兜底消息
const adaptedResponse = adaptAgentResponse(rawResponse, {
  fallbackMessages: customFallbacks
});
```

### 检查响应状态

```javascript
import { isErrorResponse, isEmptyResponse } from '../services/responseAdapter';

// 处理不同响应状态
if (isErrorResponse(adaptedResponse)) {
  // 处理错误
  showErrorMessage(adaptedResponse.error.message);
} else if (isEmptyResponse(adaptedResponse)) {
  // 处理空响应
  showEmptyState();
} else {
  // 处理成功响应
  showResponse(adaptedResponse.data.response);
}
```

### 创建加载状态

```javascript
import { createLoadingResponse } from '../services/responseAdapter';

// 在请求开始时显示加载状态
const loadingResponse = createLoadingResponse({
  message: "正在思考您的问题..."
});

// 更新UI显示加载状态
updateUI(loadingResponse);
```

## 集成示例

### 在API客户端中使用

```javascript
// apiClient.ts
import axios from 'axios';
import { adaptAgentResponse, isEmptyResponse } from './responseAdapter';

const apiClient = axios.create({...});

apiClient.interceptors.response.use(
  response => {
    if (url.includes('/agent/respond')) {
      response.data = adaptAgentResponse(response.data);
      
      // 处理空响应
      if (isEmptyResponse(response.data)) {
        // 应用兜底消息
      }
    }
    return response;
  },
  error => {
    // 处理错误
    return Promise.reject(error);
  }
);
```

### 在状态管理中使用

```javascript
// agentStore.js
import { extractTextResponse, isErrorResponse } from '../services/responseAdapter';

// 处理从服务器收到的响应
handleServerResponse: (response) => {
  if (isErrorResponse(response)) {
    // 显示错误消息
  } else {
    // 提取并显示响应文本
    const responseText = extractTextResponse(response);
    addAssistantMessage(responseText);
  }
}
```

## 注意事项

1. 确保所有API响应都通过适配器处理，保持一致性
2. 根据项目需求，可以自定义兜底消息和错误处理逻辑
3. 在处理流式响应时(SSE/WebSocket)，每个事件也应通过适配器处理
4. 适配器不应包含业务逻辑，仅负责格式转换和基本验证

## 更新记录

- **2025-08-31**: 初始版本，添加了基本的响应适配功能和兜底处理