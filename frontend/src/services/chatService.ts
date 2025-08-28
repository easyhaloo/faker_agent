import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface ChatResponse {
  reply: string;
}

export async function sendMessage(content: string): Promise<ChatResponse> {
  try {
    const response = await apiClient.post('/agent/task', {
      query: content,
      stream: false,
    });
    
    // 根据实际API响应结构调整
    return {
      reply: response.data.response || response.data.data?.response || "No response from agent"
    };
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.error?.message || 'Failed to send message');
    }
    throw new Error('An unexpected error occurred');
  }
}