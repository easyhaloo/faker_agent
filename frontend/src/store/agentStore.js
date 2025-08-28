import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { agentService } from '../services/agentService';
import { ProtocolType, ModeType, EventType } from '../services/agentService';

// 智能压缩消息历史以控制上下文长度
const compressMessagesIntelligently = (messages, maxLength = 10) => {
  if (messages.length <= maxLength) return messages;
  
  // 保留系统消息（如果有的话）
  const systemMessages = messages.filter(msg => msg.role === 'system');
  const nonSystemMessages = messages.filter(msg => msg.role !== 'system');
  
  // 如果非系统消息数量仍然超过限制，则压缩
  if (nonSystemMessages.length > maxLength) {
    // 保留第一条消息和最后几条消息
    const firstMessage = nonSystemMessages[0];
    const latestMessages = nonSystemMessages.slice(-maxLength + 1);
    
    // 合并系统消息（如果有）
    return [...systemMessages, firstMessage, ...latestMessages];
  }
  
  return messages;
};

// 计算消息总token数（简化版本）
const estimateTokens = (messages) => {
  return messages.reduce((total, msg) => {
    // 简单估算：每个字符约0.25个token，中文字符约0.5个token
    const charCount = msg.content?.length || 0;
    const tokenEstimate = Math.ceil(charCount * 0.4); // 综合考虑中英文
    return total + tokenEstimate;
  }, 0);
};

// 压缩消息以适应token限制
const compressMessagesByTokenLimit = (messages, maxTokens = 3000) => {
  // 如果当前token数未超限，直接返回
  const currentTokens = estimateTokens(messages);
  if (currentTokens <= maxTokens) return messages;
  
  // 需要压缩，使用智能压缩算法
  let compressedMessages = [...messages];
  let tokenCount = currentTokens;
  
  // 循环压缩直到满足token限制
  while (tokenCount > maxTokens && compressedMessages.length > 2) {
    // 移除中间的消息，保留首尾
    if (compressedMessages.length > 2) {
      compressedMessages = [
        compressedMessages[0],
        ...compressedMessages.slice(2) // 移除第二条消息
      ];
      tokenCount = estimateTokens(compressedMessages);
    } else {
      break;
    }
  }
  
  return compressedMessages;
};

export const useAgentStore = create(
  persist(
    (set, get) => ({
      // 状态
      messages: [],
      tasks: {},
      currentTaskId: null,
      isLoading: false,
      error: null,
      protocol: ProtocolType.HTTP, // 默认使用HTTP协议
      mode: ModeType.SYNC, // 默认使用同步模式
      filterStrategy: null, // 默认不使用过滤策略
      toolTags: [], // 默认不使用工具标签过滤
      connection: null, // 存储SSE或WebSocket连接
      availableTools: [], // 可用工具列表
      filterStrategies: [], // 可用过滤策略列表
      
      // 初始化
      initialize: () => {
        set({ 
          messages: [], 
          tasks: {}, 
          currentTaskId: null, 
          isLoading: false, 
          error: null,
          protocol: ProtocolType.HTTP,
          mode: ModeType.SYNC,
          filterStrategy: null,
          toolTags: [],
          connection: null,
          availableTools: [],
          filterStrategies: []
        });
      },
      
      // 添加用户消息
      addUserMessage: (content) => {
        const newUserMessage = {
          id: Date.now().toString(),
          role: 'user',
          content,
          timestamp: new Date().toISOString(),
        };
        
        set((state) => {
          const updatedMessages = [...state.messages, newUserMessage];
          // 使用token限制进行压缩
          const compressedMessages = compressMessagesByTokenLimit(updatedMessages, 3000);
            
          return { messages: compressedMessages };
        });
        
        return newUserMessage.id;
      },
      
      // 添加助手消息
      addAssistantMessage: (content, taskId = null) => {
        const newAssistantMessage = {
          id: Date.now().toString(),
          role: 'assistant',
          content,
          taskId,
          timestamp: new Date().toISOString(),
        };
        
        set((state) => {
          const updatedMessages = [...state.messages, newAssistantMessage];
          // 使用token限制进行压缩
          const compressedMessages = compressMessagesByTokenLimit(updatedMessages, 3000);
            
          return { messages: compressedMessages };
        });
      },
      
      // 设置协议类型
      setProtocol: (protocol) => set({ protocol }),
      
      // 设置模式类型
      setMode: (mode) => set({ mode }),
      
      // 设置过滤策略
      setFilterStrategy: (filterStrategy) => set({ filterStrategy }),
      
      // 设置工具标签
      setToolTags: (toolTags) => set({ toolTags }),
      
      // 添加工具标签
      addToolTag: (tag) => set((state) => ({
        toolTags: [...state.toolTags, tag]
      })),
      
      // 移除工具标签
      removeToolTag: (tag) => set((state) => ({
        toolTags: state.toolTags.filter(t => t !== tag)
      })),
      
      // 清空工具标签
      clearToolTags: () => set({ toolTags: [] }),
      
      // 设置可用工具列表
      setAvailableTools: (tools) => set({ availableTools: tools }),
      
      // 设置可用过滤策略列表
      setFilterStrategies: (strategies) => set({ filterStrategies: strategies }),
      
      // 设置加载状态
      setLoading: (loading) => set({ isLoading: loading }),
      
      // 设置错误
      setError: (error) => set({ error }),
      
      // 清除错误
      clearError: () => set({ error: null }),
      
      // 设置当前任务ID
      setCurrentTaskId: (taskId) => set({ currentTaskId: taskId }),
      
      // 添加任务
      addTask: (taskId, taskData) => {
        set((state) => ({
          tasks: {
            ...state.tasks,
            [taskId]: {
              id: taskId,
              ...taskData,
              status: 'pending',
              progress: 0,
              createdAt: new Date().toISOString(),
              updatedAt: new Date().toISOString(),
            },
          },
        }));
      },
      
      // 更新任务状态
      updateTaskStatus: (taskId, status, progress = null, result = null) => {
        set((state) => ({
          tasks: {
            ...state.tasks,
            [taskId]: {
              ...state.tasks[taskId],
              status,
              ...(progress !== null ? { progress } : {}),
              ...(result !== null ? { result } : {}),
              updatedAt: new Date().toISOString(),
            },
          },
        }));
      },
      
      // 添加工具调用开始事件
      addToolCallStartEvent: (taskId, toolCall) => {
        const toolCallEvent = {
          id: Date.now().toString(),
          type: 'tool_call_start',
          taskId,
          toolCall,
          timestamp: new Date().toISOString(),
        };
        
        set((state) => {
          const updatedTasks = {
            ...state.tasks,
            [taskId]: {
              ...state.tasks[taskId],
              toolCalls: [...(state.tasks[taskId]?.toolCalls || []), toolCallEvent],
              updatedAt: new Date().toISOString(),
            },
          };
          
          return { tasks: updatedTasks };
        });
      },
      
      // 添加工具调用结果事件
      addToolCallResultEvent: (taskId, toolCallId, result) => {
        set((state) => {
          const task = state.tasks[taskId];
          if (!task) return state;
          
          const toolCalls = task.toolCalls || [];
          const updatedToolCalls = toolCalls.map(tc => {
            if (tc.toolCall.id === toolCallId) {
              return {
                ...tc,
                result,
                completed: true,
                completedAt: new Date().toISOString(),
              };
            }
            return tc;
          });
          
          return {
            tasks: {
              ...state.tasks,
              [taskId]: {
                ...task,
                toolCalls: updatedToolCalls,
                updatedAt: new Date().toISOString(),
              },
            },
          };
        });
      },
      
      // 处理从服务器收到的事件
      handleServerEvent: (event) => {
        const { type, data } = event;
        
        switch (type) {
          case EventType.TOOL_CALL_START:
            get().addToolCallStartEvent(data.task_id, data.tool_call);
            break;
            
          case EventType.TOOL_CALL_RESULT:
            get().addToolCallResultEvent(data.task_id, data.tool_call_id, data.result);
            break;
            
          case EventType.TOKEN:
            // 处理流式文本token
            break;
            
          case EventType.FINAL:
            // 处理最终响应
            if (data.response) {
              get().addAssistantMessage(data.response, data.task_id);
            }
            get().setLoading(false);
            get().closeConnection();
            break;
            
          case EventType.ERROR:
            get().setError(data.error || 'Unknown error');
            get().setLoading(false);
            get().closeConnection();
            break;
            
          default:
            console.warn('Unknown event type:', type);
        }
      },
      
      // 关闭连接
      closeConnection: () => {
        const connection = get().connection;
        if (connection) {
          if (connection instanceof EventSource) {
            connection.close();
          } else if (connection.readyState === WebSocket.OPEN) {
            connection.close();
          }
          set({ connection: null });
        }
      },
      
      // 发送消息到代理
      sendMessageToAgent: async (content, conversationId = null) => {
        const messageId = get().addUserMessage(content);
        get().setLoading(true);
        get().clearError();
        
        try {
          const protocol = get().protocol;
          const mode = get().mode;
          const filterStrategy = get().filterStrategy;
          const toolTags = get().toolTags;
          
          // 根据协议和模式选择发送方法
          let response;
          
          if (protocol === ProtocolType.HTTP && mode === ModeType.SYNC) {
            // 同步HTTP请求
            response = await agentService.sendHttpRequest(content, {
              conversationId,
              filterStrategy,
              toolTags
            });
            
            if (response.status === 'success') {
              // 如果有任务ID，设置为当前任务
              if (response.data.task_id) {
                get().setCurrentTaskId(response.data.task_id);
                get().addTask(response.data.task_id, {
                  query: content,
                  response: response.data.response,
                });
              }
              
              // 添加助手回复
              get().addAssistantMessage(response.data.response, response.data.task_id);
            } else {
              const errorMessage = response.error?.message || 'Unknown error occurred';
              get().setError(errorMessage);
              get().addAssistantMessage(`Error: ${errorMessage}`);
            }
          } else if (protocol === ProtocolType.SSE && mode === ModeType.STREAM) {
            // 流式SSE请求
            const eventSource = await agentService.sendSSERequest(content, {
              conversationId,
              filterStrategy,
              toolTags,
              onEvent: get().handleServerEvent
            });
            
            // 存储连接以便稍后关闭
            set({ connection: eventSource });
          } else if (protocol === ProtocolType.WEBSOCKET && mode === ModeType.STREAM) {
            // WebSocket请求
            const socket = agentService.sendWebSocketRequest(content, {
              conversationId,
              filterStrategy,
              toolTags,
              onEvent: get().handleServerEvent
            });
            
            // 存储连接以便稍后关闭
            set({ connection: socket });
          }
        } catch (error) {
          console.error('Error sending message to agent:', error);
          const errorMessage = error.message || 'Failed to communicate with the agent';
          get().setError(errorMessage);
          get().addAssistantMessage(`Error: ${errorMessage}`);
          get().setLoading(false);
        }
      },
      
      // 获取可用工具列表
      fetchAvailableTools: async () => {
        try {
          const response = await agentService.getAvailableTools();
          if (response.status === 'success') {
            get().setAvailableTools(response.data);
          }
        } catch (error) {
          console.error('Error fetching available tools:', error);
        }
      },
      
      // 获取可用过滤策略
      fetchFilterStrategies: async () => {
        try {
          const response = await agentService.getFilterStrategies();
          if (response.status === 'success') {
            get().setFilterStrategies(response.data);
          }
        } catch (error) {
          console.error('Error fetching filter strategies:', error);
        }
      },
      
      // 分析查询（不执行）
      analyzeQuery: async (content) => {
        try {
          const response = await agentService.analyzeQuery(content);
          return response;
        } catch (error) {
          console.error('Error analyzing query:', error);
          throw error;
        }
      },
    }),
    {
      name: 'agent-storage',
      partialize: (state) => ({ 
        messages: state.messages.slice(-20), // 只持久化最近20条消息
        tasks: state.tasks,
        protocol: state.protocol,
        mode: state.mode,
        filterStrategy: state.filterStrategy,
        toolTags: state.toolTags,
      }),
    }
  )
);

export default useAgentStore;