export type Message = {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  createdAt?: string;
  meta?: Record<string, any>;
};

export type Conversation = {
  id: string;
  title: string;
  snippet: string;
  messages: Message[];
};

// Legacy types for backward compatibility
export interface ChatMessage {
  id: string;
  sender: "user" | "ai";
  content: string;
  timestamp: string;
  status?: "pending" | "success" | "error";
}

export interface Session {
  id: string;
  name: string;
  messages: ChatMessage[];
  createdAt: string;
  updatedAt: string;
}