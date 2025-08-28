/**
 * WebSocket连接管理器
 * 负责处理WebSocket连接的创建、监控和关闭
 */

// 连接状态枚举
export const ConnectionState = {
  DISCONNECTED: 'disconnected',
  CONNECTING: 'connecting',
  CONNECTED: 'connected',
  RECONNECTING: 'reconnecting',
  ERROR: 'error'
};

class WebSocketManager {
  constructor() {
    this.socket = null;
    this.url = null;
    this.state = ConnectionState.DISCONNECTED;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000; // 初始重连延迟1秒
    this.eventHandlers = {
      message: [],
      open: [],
      close: [],
      error: [],
      stateChange: []
    };
  }

  /**
   * 创建新的WebSocket连接
   * @param {string} url - WebSocket连接URL
   * @returns {Promise} 连接结果Promise
   */
  connect(url) {
    return new Promise((resolve, reject) => {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.close();
      }

      this.url = url;
      this._setState(ConnectionState.CONNECTING);
      
      try {
        this.socket = new WebSocket(url);
        
        this.socket.onopen = (event) => {
          this._setState(ConnectionState.CONNECTED);
          this.reconnectAttempts = 0;
          this._triggerEvent('open', event);
          resolve(this.socket);
        };
        
        this.socket.onclose = (event) => {
          const wasConnected = this.state === ConnectionState.CONNECTED;
          this._setState(ConnectionState.DISCONNECTED);
          this._triggerEvent('close', event);
          
          // 如果连接曾经成功过，且非人为关闭，则尝试重连
          if (wasConnected && !event.wasClean && this.reconnectAttempts < this.maxReconnectAttempts) {
            this._attemptReconnect();
          }
        };
        
        this.socket.onerror = (error) => {
          this._setState(ConnectionState.ERROR);
          this._triggerEvent('error', error);
          reject(error);
        };
        
        this.socket.onmessage = (event) => {
          let data;
          try {
            data = JSON.parse(event.data);
          } catch (e) {
            data = event.data;
          }
          this._triggerEvent('message', { data, raw: event });
        };
      } catch (error) {
        this._setState(ConnectionState.ERROR);
        reject(error);
      }
    });
  }

  /**
   * 关闭WebSocket连接
   */
  close() {
    if (this.socket) {
      // 避免在关闭时触发重连
      this.reconnectAttempts = this.maxReconnectAttempts;
      
      if (this.socket.readyState === WebSocket.OPEN) {
        this.socket.close(1000, 'Normal closure');
      }
      
      this.socket = null;
      this._setState(ConnectionState.DISCONNECTED);
    }
  }

  /**
   * 发送数据到WebSocket服务器
   * @param {object|string} data - 要发送的数据
   * @returns {boolean} 发送成功状态
   */
  send(data) {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      console.error('Cannot send message: WebSocket is not connected');
      return false;
    }
    
    try {
      const payload = typeof data === 'object' ? JSON.stringify(data) : data;
      this.socket.send(payload);
      return true;
    } catch (error) {
      console.error('Error sending message:', error);
      return false;
    }
  }

  /**
   * 注册事件监听器
   * @param {string} eventType - 事件类型
   * @param {function} handler - 事件处理函数
   * @returns {function} 取消注册的函数
   */
  on(eventType, handler) {
    if (!this.eventHandlers[eventType]) {
      this.eventHandlers[eventType] = [];
    }
    
    this.eventHandlers[eventType].push(handler);
    
    // 返回取消注册的函数
    return () => {
      this.off(eventType, handler);
    };
  }

  /**
   * 移除事件监听器
   * @param {string} eventType - 事件类型
   * @param {function} handler - 事件处理函数
   */
  off(eventType, handler) {
    if (!this.eventHandlers[eventType]) return;
    
    this.eventHandlers[eventType] = this.eventHandlers[eventType].filter(
      h => h !== handler
    );
  }

  /**
   * 获取当前连接状态
   * @returns {string} 连接状态
   */
  getState() {
    return this.state;
  }

  /**
   * 设置连接状态并触发stateChange事件
   * @param {string} state - 新的连接状态
   * @private
   */
  _setState(state) {
    const previousState = this.state;
    this.state = state;
    
    if (previousState !== state) {
      this._triggerEvent('stateChange', { previous: previousState, current: state });
    }
  }

  /**
   * 触发指定类型的事件
   * @param {string} eventType - 事件类型
   * @param {*} data - 事件数据
   * @private
   */
  _triggerEvent(eventType, data) {
    if (!this.eventHandlers[eventType]) return;
    
    for (const handler of this.eventHandlers[eventType]) {
      try {
        handler(data);
      } catch (error) {
        console.error(`Error in ${eventType} event handler:`, error);
      }
    }
  }

  /**
   * 尝试重新连接
   * @private
   */
  _attemptReconnect() {
    this._setState(ConnectionState.RECONNECTING);
    this.reconnectAttempts++;
    
    // 指数退避重连策略
    const delay = Math.min(
      this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts - 1),
      30000 // 最大延迟30秒
    );
    
    console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
    
    setTimeout(() => {
      if (this.state !== ConnectionState.RECONNECTING) return;
      
      this.connect(this.url).catch(error => {
        console.error('Reconnection failed:', error);
        
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this._attemptReconnect();
        } else {
          this._setState(ConnectionState.ERROR);
          this._triggerEvent('error', { 
            type: 'reconnect_failed', 
            message: 'Maximum reconnection attempts reached' 
          });
        }
      });
    }, delay);
  }
}

// 创建并导出单例实例
export const webSocketManager = new WebSocketManager();
export default webSocketManager;