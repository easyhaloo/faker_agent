import axios from 'axios';
import { apiClient } from './apiClient';

export interface ChatResponse {
  reply: string;
}

export async function sendMessage(content: string): Promise<ChatResponse> {
  try {
    const response = await apiClient.post('/agent/task', {
      query: content,
      stream: false,
    });
    
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