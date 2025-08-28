import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { agentService } from '../services/api';

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
      
      // 初始化
      initialize: () => {
        set({ 
          messages: [], 
          tasks: {}, 
          currentTaskId: null, 
          isLoading: false, 
          error: null 
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
      
      // 发送消息到代理
      sendMessageToAgent: async (content) => {
        const messageId = get().addUserMessage(content);
        get().setLoading(true);
        get().clearError();
        
        try {
          // 提交任务给后端
          const response = await agentService.sendTask(content);
          
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
        } catch (error) {
          console.error('Error sending message to agent:', error);
          const errorMessage = error.message || 'Failed to communicate with the agent';
          get().setError(errorMessage);
          get().addAssistantMessage(`Error: ${errorMessage}`);
        } finally {
          get().setLoading(false);
        }
      },
    }),
    {
      name: 'agent-storage',
      partialize: (state) => ({ 
        messages: state.messages.slice(-20), // 只持久化最近20条消息
        tasks: state.tasks 
      }),
    }
  )
);

export default useAgentStore;