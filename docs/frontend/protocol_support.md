# 前端多协议支持

本文档详细介绍了 Faker Agent 前端系统的多协议通信支持，包括实现原理、组件设计和使用方法。

## 1. 概述

Faker Agent 前端支持三种通信协议与模式的组合：

| 协议 | 模式 | 特点 | 适用场景 |
|------|------|------|----------|
| HTTP | 同步 | 简单可靠，等待完整响应 | 简单查询，无需实时反馈 |
| SSE  | 流式 | 服务器推送事件流，实时显示执行过程 | 需要实时反馈的复杂任务 |
| WebSocket | 流式 | 双向实时通信，完整工具执行可视化 | 交互式任务，需要实时更新 |

## 2. 核心组件

### 2.1 协议选择器组件

`ProtocolSelector` 组件允许用户选择通信协议和响应模式：

```javascript
// ProtocolSelector.jsx
const ProtocolSelector = () => {
  const protocol = useAgentStore((state) => state.protocol);
  const mode = useAgentStore((state) => state.mode);
  const setProtocol = useAgentStore((state) => state.setProtocol);
  const setMode = useAgentStore((state) => state.setMode);
  
  // 处理协议变更
  const handleProtocolChange = (newProtocol) => {
    setProtocol(newProtocol);
    
    // 当选择HTTP协议时，自动设置为同步模式
    if (newProtocol === ProtocolType.HTTP) {
      setMode(ModeType.SYNC);
    } 
    // 当选择SSE或WebSocket协议时，自动设置为流式模式
    else if (newProtocol === ProtocolType.SSE || newProtocol === ProtocolType.WEBSOCKET) {
      setMode(ModeType.STREAM);
    }
  };
  
  // ...渲染协议和模式选择按钮
}
```

### 2.2 工具标签选择器

`ToolTagSelector` 组件允许用户选择要使用的工具标签：

```javascript
// ToolTagSelector.jsx
const ToolTagSelector = () => {
  const toolTags = useAgentStore((state) => state.toolTags);
  const availableTools = useAgentStore((state) => state.availableTools);
  const addToolTag = useAgentStore((state) => state.addToolTag);
  const removeToolTag = useAgentStore((state) => state.removeToolTag);
  
  // 从可用工具中提取所有唯一标签
  const extractAllTags = () => {
    if (!availableTools || availableTools.length === 0) return [];
    
    const allTags = new Set();
    availableTools.forEach(tool => {
      if (tool.tags && Array.isArray(tool.tags)) {
        tool.tags.forEach(tag => allTags.add(tag));
      }
    });
    
    return Array.from(allTags).sort();
  };
  
  // ...渲染标签选择界面
}
```

### 2.3 流式响应组件

`StreamingResponse` 组件显示实时工具执行过程：

```javascript
// StreamingResponse.jsx
const StreamingResponse = ({ taskId }) => {
  const task = useAgentStore((state) => state.tasks[taskId]);
  
  // 渲染工具调用信息
  const renderToolCall = (toolCall) => {
    const isCompleted = Boolean(toolCall.completed);
    
    return (
      <div key={toolCall.id} className="mb-3 border border-gray-200 rounded-md">
        {/* 工具调用头部 */}
        <div className="flex items-center justify-between bg-gray-50 px-3 py-2">
          <div className="flex items-center">
            <Terminal size={14} className="mr-2" />
            <span className="font-medium">{toolCall.toolCall.name}</span>
          </div>
          <Badge variant={isCompleted ? "secondary" : "outline"}>
            {isCompleted ? "已完成" : "执行中"}
          </Badge>
        </div>
        
        {/* 工具调用参数和结果 */}
        {/* ... */}
      </div>
    );
  };
  
  // ...渲染工具调用列表和响应
}
```

## 3. 服务层实现

### 3.1 AgentService 类

`AgentService` 类提供了与后端通信的核心方法：

```javascript
// agentService.js
export class AgentService {
  constructor() {
    this.baseUrl = '/agent/v1';
    this.eventSource = null;
    this.websocket = null;
  }

  // HTTP 同步请求
  async sendHttpRequest(input, options = {}) {
    const response = await apiClient.post(`${this.baseUrl}/respond`, {
      input,
      conversation_id: options.conversationId,
      protocol: ProtocolType.HTTP,
      mode: ModeType.SYNC,
      filter_strategy: options.filterStrategy,
      tool_tags: options.toolTags,
      params: options.params
    });
    
    return response.data;
  }

  // SSE 流式请求
  async sendSSERequest(input, options = {}) {
    // 关闭之前的连接
    this.closeSSEConnection();
    
    // 创建 SSE 连接
    const eventSource = new EventSource(`${apiClient.defaults.baseURL}${this.baseUrl}/respond?protocol=sse&mode=stream`);
    this.eventSource = eventSource;
    
    // 设置事件处理器
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (options.onEvent) {
          options.onEvent(data);
        }
        
        // 如果是最终事件或错误，关闭连接
        if (data.type === EventType.FINAL || data.type === EventType.ERROR) {
          this.closeSSEConnection();
        }
      } catch (error) {
        console.error('Error parsing SSE event:', error);
      }
    };
    
    // 发送请求
    fetch(`${apiClient.defaults.baseURL}${this.baseUrl}/respond`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        input,
        conversation_id: options.conversationId,
        protocol: ProtocolType.SSE,
        mode: ModeType.STREAM,
        filter_strategy: options.filterStrategy,
        tool_tags: options.toolTags,
        params: options.params
      })
    });
    
    return eventSource;
  }

  // WebSocket 流式请求
  sendWebSocketRequest(input, options = {}) {
    // 实现 WebSocket 通信
    // ...
  }
}
```

### 3.2 WebSocket 连接管理

`WebSocketManager` 类提供了可靠的 WebSocket 连接管理：

```javascript
// connectionManager.js
export class WebSocketManager {
  constructor() {
    this.socket = null;
    this.state = ConnectionState.DISCONNECTED;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.eventHandlers = {
      message: [],
      open: [],
      close: [],
      error: [],
      stateChange: []
    };
  }

  // 连接方法
  connect(url) {
    return new Promise((resolve, reject) => {
      this._setState(ConnectionState.CONNECTING);
      
      try {
        this.socket = new WebSocket(url);
        
        this.socket.onopen = (event) => {
          this._setState(ConnectionState.CONNECTED);
          this._triggerEvent('open', event);
          resolve(this.socket);
        };
        
        // 设置其他事件处理器
        // ...
      } catch (error) {
        this._setState(ConnectionState.ERROR);
        reject(error);
      }
    });
  }

  // 其他方法: send, close, on, off 等
  // ...
}
```

## 4. 状态管理

使用 Zustand 管理协议相关状态：

```javascript
// agentStore.js
export const useAgentStore = create(
  persist(
    (set, get) => ({
      // 状态
      protocol: ProtocolType.HTTP,
      mode: ModeType.SYNC,
      filterStrategy: null,
      toolTags: [],
      connection: null,
      // ...
      
      // 设置协议类型
      setProtocol: (protocol) => set({ protocol }),
      
      // 设置模式类型
      setMode: (mode) => set({ mode }),
      
      // 工具标签管理
      setToolTags: (toolTags) => set({ toolTags }),
      addToolTag: (tag) => set((state) => ({
        toolTags: [...state.toolTags, tag]
      })),
      removeToolTag: (tag) => set((state) => ({
        toolTags: state.toolTags.filter(t => t !== tag)
      })),
      
      // 事件处理
      handleServerEvent: (event) => {
        const { type, data } = event;
        
        switch (type) {
          case EventType.TOOL_CALL_START:
            get().addToolCallStartEvent(data.task_id, data.tool_call);
            break;
          // 处理其他事件类型
          // ...
        }
      },
      
      // 发送消息
      sendMessageToAgent: async (content, conversationId = null) => {
        // 根据协议和模式选择发送方法
        // ...
      },
    }),
    // 持久化配置
    // ...
  )
);
```

## 5. 集成到聊天界面

`EnhancedChatPanel` 组件集成了多协议支持：

```javascript
// EnhancedChatPanel.jsx
const EnhancedChatPanel = () => {
  const [inputValue, setInputValue] = useState('');
  const [showSettings, setShowSettings] = useState(false);
  
  const protocol = useAgentStore((state) => state.protocol);
  const mode = useAgentStore((state) => state.mode);
  const currentTaskId = useAgentStore((state) => state.currentTaskId);
  const sendMessageToAgent = useAgentStore((state) => state.sendMessageToAgent);
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;
    
    sendMessageToAgent(inputValue.trim());
    setInputValue('');
  };
  
  return (
    <div className="flex flex-col">
      {/* 设置面板 */}
      {showSettings && (
        <div className="p-4 bg-gray-50">
          <ProtocolSelector />
          <ToolTagSelector />
        </div>
      )}
      
      {/* 流式响应区域 */}
      {isLoading && currentTaskId && mode === 'stream' && (
        <StreamingResponse taskId={currentTaskId} />
      )}
      
      {/* 消息区域 */}
      {/* ... */}
      
      {/* 输入区域 */}
      {/* ... */}
    </div>
  );
};
```

## 6. 使用示例

### 6.1 基本使用流程

1. 在设置面板中选择协议和模式
2. 可选：选择工具标签过滤
3. 输入查询内容并发送
4. 对于流式模式，可以实时查看工具执行过程

### 6.2 代码示例

```javascript
// 发送消息示例
const sendMessage = () => {
  // 使用 agentStore 中的方法发送消息
  useAgentStore.getState().sendMessageToAgent("查询今天北京的天气", {
    // 可选参数
    conversationId: "conv-123",
    filterStrategy: "tag_filter"
  });
};

// 切换协议示例
const switchToSSE = () => {
  const { setProtocol, setMode } = useAgentStore.getState();
  setProtocol(ProtocolType.SSE);
  setMode(ModeType.STREAM);
};
```

## 7. 调试和错误处理

### 7.1 常见错误处理

- 连接错误：自动重试或降级到 HTTP 模式
- 解析错误：提供友好的错误提示
- 超时错误：设置合理的超时时间

### 7.2 调试技巧

- 使用浏览器开发者工具检查网络请求
- 启用详细日志记录
- 使用 Redux DevTools 检查状态变化

## 8. 未来优化

- 添加连接状态指示器
- 支持流式响应的部分渲染（逐字显示）
- 添加工具执行时间统计
- 实现中断请求功能