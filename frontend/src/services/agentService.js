import { apiClient } from './apiClient';
import { webSocketManager } from './connectionManager';

/**
 * 协议类型枚举
 */
export const ProtocolType = {
  HTTP: 'http',
  SSE: 'sse',
  WEBSOCKET: 'websocket'
};

/**
 * 模式类型枚举
 */
export const ModeType = {
  SYNC: 'sync',
  STREAM: 'stream'
};

/**
 * 事件类型枚举
 */
export const EventType = {
  TOOL_CALL_START: 'tool_call_start',
  TOOL_CALL_RESULT: 'tool_call_result',
  TOKEN: 'token',
  FINAL: 'final',
  ERROR: 'error'
};

export class AgentService {
  constructor() {
    this.baseUrl = '/agent/v1';
    this.eventListeners = {};
    this.websocket = null;
    this.eventSource = null;
    this.activeRequests = new Map();
  }

  /**
   * 发送查询到智能体（HTTP协议）
   * @param {string} input - 用户输入
   * @param {string} conversationId - 会话ID
   * @param {string} filterStrategy - 过滤策略
   * @param {Array} toolTags - 工具标签
   * @param {Object} params - 其他参数
   * @returns {Promise} 响应结果
   */
  async sendHttpRequest(input, { 
    conversationId = null,
    filterStrategy = null,
    toolTags = null,
    params = {}
  } = {}) {
    const response = await apiClient.post(`${this.baseUrl}/respond`, {
      input,
      conversation_id: conversationId,
      protocol: ProtocolType.HTTP,
      mode: ModeType.SYNC,
      filter_strategy: filterStrategy,
      tool_tags: toolTags,
      params
    });
    
    return response.data;
  }

  /**
   * 使用SSE协议发送查询到智能体
   * @param {string} input - 用户输入
   * @param {string} conversationId - 会话ID
   * @param {string} filterStrategy - 过滤策略
   * @param {Array} toolTags - 工具标签
   * @param {Object} params - 其他参数
   * @param {function} onEvent - 事件回调
   * @returns {Promise} 事件源对象
   */
  async sendSSERequest(input, { 
    conversationId = null,
    filterStrategy = null,
    toolTags = null,
    params = {},
    onEvent = null
  } = {}) {
    // 关闭之前的连接
    this.closeSSEConnection();
    
    // 构建URL参数
    const queryParams = new URLSearchParams();
    queryParams.append('protocol', ProtocolType.SSE);
    queryParams.append('mode', ModeType.STREAM);
    
    // 创建POST请求（使用fetch API）
    fetch(`${apiClient.defaults.baseURL}${this.baseUrl}/respond`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        input,
        conversation_id: conversationId,
        protocol: ProtocolType.SSE,
        mode: ModeType.STREAM,
        filter_strategy: filterStrategy,
        tool_tags: toolTags,
        params
      })
    });
    
    // 创建SSE连接
    const eventSource = new EventSource(`${apiClient.defaults.baseURL}${this.baseUrl}/respond?${queryParams.toString()}`);
    
    // 存储EventSource实例
    this.eventSource = eventSource;
    
    // 设置事件处理器
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (onEvent) {
          onEvent(data);
        }
        
        // 如果是最终事件或错误，关闭连接
        if (data.type === EventType.FINAL || data.type === EventType.ERROR) {
          this.closeSSEConnection();
        }
      } catch (error) {
        console.error('Error parsing SSE event:', error);
        if (onEvent) {
          onEvent({ type: EventType.ERROR, error: 'Failed to parse event data' });
        }
      }
    };
    
    eventSource.onerror = (error) => {
      console.error('SSE connection error:', error);
      if (onEvent) {
        onEvent({ type: EventType.ERROR, error: 'SSE connection error' });
      }
      this.closeSSEConnection();
    };
    
    return eventSource;
  }

  /**
   * 关闭SSE连接
   */
  closeSSEConnection() {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }

  /**
   * 使用WebSocket协议发送查询到智能体
   * @param {string} input - 用户输入
   * @param {string} conversationId - 会话ID
   * @param {string} filterStrategy - 过滤策略
   * @param {Array} toolTags - 工具标签
   * @param {Object} params - 其他参数
   * @param {function} onEvent - 事件回调
   * @returns {WebSocket} WebSocket连接对象
   */
  sendWebSocketRequest(input, { 
    conversationId = null,
    filterStrategy = null,
    toolTags = null,
    params = {},
    onEvent = null
  } = {}) {
    // 确保旧的连接已关闭
    this.closeWebSocketConnection();
    
    // 创建WebSocket连接
    const wsUrl = apiClient.defaults.baseURL.replace(/^http/, 'ws');
    
    // 使用连接管理器创建连接
    webSocketManager.connect(`${wsUrl}${this.baseUrl}/ws`)
      .then(() => {
        // 连接建立后发送请求
        webSocketManager.send(JSON.stringify({
          input,
          conversation_id: conversationId,
          filter_strategy: filterStrategy,
          tool_tags: toolTags,
          params
        }));
      })
      .catch(error => {
        console.error('WebSocket connection error:', error);
        if (onEvent) {
          onEvent({ type: EventType.ERROR, error: 'WebSocket connection error' });
        }
      });
    
    // 注册消息处理
    const messageHandler = (event) => {
      try {
        const data = typeof event.data === 'string' 
          ? JSON.parse(event.data) 
          : event.data;
        
        if (onEvent) {
          onEvent(data);
        }
        
        // 如果是最终事件或错误，关闭连接
        if (data.type === EventType.FINAL || data.type === EventType.ERROR) {
          webSocketManager.off('message', messageHandler);
          webSocketManager.close();
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
        if (onEvent) {
          onEvent({ type: EventType.ERROR, error: 'Failed to parse WebSocket message' });
        }
      }
    };
    
    // 注册错误处理
    const errorHandler = (error) => {
      console.error('WebSocket error:', error);
      if (onEvent) {
        onEvent({ type: EventType.ERROR, error: 'WebSocket connection error' });
      }
    };
    
    // 注册关闭处理
    const closeHandler = () => {
      console.log('WebSocket connection closed');
      // 移除所有事件监听器
      webSocketManager.off('message', messageHandler);
      webSocketManager.off('error', errorHandler);
      webSocketManager.off('close', closeHandler);
    };
    
    // 添加事件监听器
    webSocketManager.on('message', messageHandler);
    webSocketManager.on('error', errorHandler);
    webSocketManager.on('close', closeHandler);
    
    return webSocketManager;
  }

  /**
   * 关闭WebSocket连接
   */
  closeWebSocketConnection() {
    webSocketManager.close();
  }

  /**
   * 分析查询（不执行）
   * @param {string} input - 用户输入
   * @returns {Promise} 分析结果
   */
  async analyzeQuery(input) {
    const response = await apiClient.post(`${this.baseUrl}/analyze`, {
      input
    });
    
    return response.data;
  }

  /**
   * 获取可用的过滤策略
   * @returns {Promise} 策略列表
   */
  async getFilterStrategies() {
    const response = await apiClient.get(`${this.baseUrl}/strategies`);
    return response.data;
  }

  /**
   * 获取可用的工具列表
   * @returns {Promise} 工具列表
   */
  async getAvailableTools() {
    const response = await apiClient.get('/tools');
    return response.data;
  }

  /**
   * 清理所有连接
   */
  cleanup() {
    this.closeSSEConnection();
    this.closeWebSocketConnection();
  }
}

// 创建单例实例
export const agentService = new AgentService();

export default agentService;