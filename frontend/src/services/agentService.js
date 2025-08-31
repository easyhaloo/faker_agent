import { apiClient } from './apiClient';
import { webSocketManager } from './connectionManager';
import { adaptAgentResponse, extractTextResponse, extractToolCalls, isEmptyResponse, createLoadingResponse, DEFAULT_FALLBACK_MESSAGES } from './responseAdapter';

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
    try {
      const response = await apiClient.post(`${this.baseUrl}/respond`, {
        input,
        conversation_id: conversationId,
        protocol: ProtocolType.HTTP,
        mode: ModeType.SYNC,
        filter_strategy: filterStrategy,
        tool_tags: toolTags,
        params
      });
      
      // Response is already adapted by apiClient interceptor
      // Double check if the response is empty and apply fallback if needed
      if (isEmptyResponse(response.data)) {
        return adaptAgentResponse({
          status: 'success',
          data: { response: DEFAULT_FALLBACK_MESSAGES.empty }
        });
      }
      return response.data;
    } catch (error) {
      // Handle error cases with the adapter as well
      if (error.response && error.response.data) {
        const adaptedResponse = adaptAgentResponse(error.response.data);
        // Check if the adapted response is empty and provide a fallback
        if (isEmptyResponse(adaptedResponse)) {
          return adaptAgentResponse({
            status: 'error',
            error: {
              code: error.response.status,
              message: DEFAULT_FALLBACK_MESSAGES.error
            }
          });
        }
        return adaptedResponse;
      }
      
      // Create a standardized error response
      return adaptAgentResponse({
        status: 'error',
        error: {
          code: 'REQUEST_FAILED',
          message: error.message || 'Failed to communicate with the agent'
        }
      });
    }
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
    
    try {
      // 首先尝试使用专用的SSE端点
      let response;
      
      try {
        // 构建查询参数
        const queryParams = new URLSearchParams({
          input
        });
        
        if (conversationId) {
          queryParams.append('conversation_id', conversationId);
        }
        
        if (filterStrategy) {
          queryParams.append('filter_strategy', filterStrategy);
        }
        
        if (toolTags && toolTags.length > 0) {
          queryParams.append('tool_tags', toolTags.join(','));
        }
        
        // 使用GET请求创建SSE连接
        response = await fetch(`${apiClient.defaults.baseURL}${this.baseUrl}/sse_respond?${queryParams.toString()}`, {
          headers: {
            'Accept': 'text/event-stream'
          }
        });
      } catch (error) {
        console.warn('SSE GET endpoint failed, falling back to POST method:', error);
        
        // 如果GET端点失败，回退到POST方法
        // 准备请求数据
        const requestData = {
          input,
          conversation_id: conversationId,
          protocol: ProtocolType.SSE,
          mode: ModeType.STREAM,
          filter_strategy: filterStrategy,
          tool_tags: toolTags,
          params
        };
        
        // 使用POST请求创建SSE连接
        response = await fetch(`${apiClient.defaults.baseURL}${this.baseUrl}/respond`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream'
          },
          body: JSON.stringify(requestData)
        });
      }
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      // 创建基于Response的ReadableStream的事件处理
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      // 存储用于清理的函数
      this.eventSource = {
        close: () => {
          reader.cancel();
        }
      };
      
      // 处理流数据
      let buffer = '';
      const processStream = async () => {
        try {
          while (true) {
            const { value, done } = await reader.read();
            
            if (done) {
              // 流结束
              break;
            }
            
            // 解码并添加到缓冲区
            buffer += decoder.decode(value, { stream: true });
            
            // 处理缓冲区中的完整事件
            const events = buffer.split('\n\n');
            buffer = events.pop() || ''; // 保留最后一个不完整的事件（如果有）
            
            // 处理完整的事件
            for (const eventText of events) {
              if (!eventText.trim()) continue;
              
              // 解析事件数据
              const dataMatch = eventText.match(/data: (.+)/);
              if (dataMatch && dataMatch[1]) {
                try {
                  const eventData = JSON.parse(dataMatch[1]);
                  const adaptedData = adaptAgentResponse(eventData);
                  
                  // 处理空响应
                  if (isEmptyResponse(adaptedData)) {
                    this._handleEmptyResponse(adaptedData, onEvent, () => this.closeSSEConnection());
                    return;
                  }
                  
                  if (onEvent) {
                    onEvent(adaptedData);
                  }
                  
                  // 如果是最终事件或错误，关闭连接
                  if (adaptedData.type === EventType.FINAL || adaptedData.type === EventType.ERROR) {
                    this.closeSSEConnection();
                    return;
                  }
                } catch (error) {
                  // 处理解析错误
                  if (onEvent) {
                    onEvent(adaptAgentResponse({
                      type: EventType.ERROR,
                      status: 'error',
                      error: {
                        code: 'PARSE_ERROR',
                        message: 'Failed to parse event data'
                      }
                    }));
                  }
                }
              }
            }
          }
        } catch (error) {
          // 处理流读取错误
          if (onEvent) {
            onEvent(adaptAgentResponse({
              type: EventType.ERROR,
              status: 'error',
              error: {
                code: 'STREAM_ERROR',
                message: 'Error reading event stream'
              }
            }));
          }
          this.closeSSEConnection();
        }
      };
      
      // 开始处理流
      processStream();
      
      return this.eventSource;
    } catch (error) {
      // 处理请求错误
      if (onEvent) {
        onEvent(adaptAgentResponse({
          type: EventType.ERROR,
          status: 'error',
          error: {
            code: 'CONNECTION_ERROR',
            message: error.message || 'SSE connection error'
          }
        }));
      }
      return null;
    }
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
          onEvent(adaptAgentResponse({
          type: EventType.ERROR,
            status: 'error',
            error: {
              code: 'CONNECTION_ERROR',
              message: 'WebSocket connection error'
            }
          }));
        }
      });
    
    // 注册消息处理
    const messageHandler = (event) => {
      try {
        const data = typeof event.data === 'string' 
          ? JSON.parse(event.data) 
          : event.data;
        
        // Adapt event data for consistent handling
        const adaptedData = adaptAgentResponse(data);
        
        // 处理空响应
        if (isEmptyResponse(adaptedData)) {
          this._handleEmptyResponse(adaptedData, onEvent, () => {
            webSocketManager.off('message', messageHandler);
            webSocketManager.close();
          });
          return;
        }
        
        if (onEvent) {
          onEvent(adaptedData);
        }
        
        // 如果是最终事件或错误，关闭连接
        if (adaptedData.type === EventType.FINAL || adaptedData.type === EventType.ERROR) {
          webSocketManager.off('message', messageHandler);
          webSocketManager.close();
        }
      } catch (error) {
        // 处理WebSocket消息解析错误
        if (onEvent) {
          onEvent(adaptAgentResponse({
          type: EventType.ERROR,
            status: 'error',
            error: {
              code: 'PARSE_ERROR',
              message: 'Failed to parse WebSocket message'
            }
          }));
        }
      }
    };
    
    // 注册错误处理
    const errorHandler = (error) => {
      // 处理WebSocket错误
      if (onEvent) {
        onEvent(adaptAgentResponse({
          type: EventType.ERROR,
          status: 'error',
          error: {
            code: 'WEBSOCKET_ERROR',
            message: 'WebSocket connection error'
          }
        }));
      }
    };
    
    // 注册关闭处理
    const closeHandler = () => {
      // WebSocket连接已关闭
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
   * 处理空响应的辅助方法
   * @private
   * @param {Object} response - 适配后的响应数据
   * @param {Function} onEvent - 事件回调
   * @param {Function} closeCallback - 关闭连接的回调
   */
  _handleEmptyResponse(response, onEvent, closeCallback) {
    if (onEvent) {
      // 发送一个带有默认空响应消息的事件
      onEvent(adaptAgentResponse({
        type: EventType.FINAL,
        status: 'success',
        data: { response: DEFAULT_FALLBACK_MESSAGES.empty }
      }));
    }
    
    // 调用关闭连接的回调函数
    if (closeCallback && typeof closeCallback === 'function') {
      closeCallback();
    }
  }

  /**
   * 分析查询（不执行）
   * @param {string} input - 用户输入
   * @returns {Promise} 分析结果
   */
  async analyzeQuery(input) {
    try {
      const response = await apiClient.post(`${this.baseUrl}/analyze`, {
        input
      });
      
      const adaptedResponse = adaptAgentResponse(response.data);
      // Check if the response is empty and apply fallback
      if (isEmptyResponse(adaptedResponse)) {
        return adaptAgentResponse({
          status: 'success',
          data: { response: DEFAULT_FALLBACK_MESSAGES.empty }
        });
      }
      return adaptedResponse;
    } catch (error) {
      // 分析查询错误
      return adaptAgentResponse({
        status: 'error',
        error: {
          code: 'ANALYSIS_ERROR',
          message: error.message || 'Failed to analyze query'
        }
      });
    }
  }

  /**
   * 获取可用的过滤策略
   * @returns {Promise} 策略列表
   */
  async getFilterStrategies() {
    try {
      const response = await apiClient.get(`${this.baseUrl}/strategies`);
      const adaptedResponse = adaptAgentResponse(response.data);
      if (isEmptyResponse(adaptedResponse)) {
        return adaptAgentResponse({
          status: 'success',
          data: { response: 'No filter strategies available' }
        });
      }
      return adaptedResponse;
    } catch (error) {
      // 获取过滤策略失败
      return adaptAgentResponse({
        status: 'error',
        error: {
          code: 'STRATEGY_ERROR',
          message: error.message || 'Failed to fetch strategies'
        }
      });
    }
  }

  /**
   * 获取可用的工具列表
   * @returns {Promise} 工具列表
   */
  async getAvailableTools() {
    try {
      const response = await apiClient.get(`${this.baseUrl}/tools`);
      
      // Skip adaptation for tools API, use response directly
      if (response.data && response.data.status === 'success' && response.data.data && response.data.data.tools) {
        return response.data;
      }
      
      // Otherwise adapt the response
      const adaptedResponse = adaptAgentResponse(response.data);
      
      if (isEmptyResponse(adaptedResponse) || !adaptedResponse.data.tools) {
        return {
          status: 'success',
          data: { tools: [] },
          error: null
        };
      }
      
      return adaptedResponse;
    } catch (error) {
      // 获取可用工具失败
      return {
        status: 'error',
        data: { tools: [] },
        error: {
          code: 'TOOLS_ERROR',
          message: error.message || 'Failed to fetch tools'
        }
      };
    }
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