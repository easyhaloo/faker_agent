import { create } from 'zustand';
import { v4 as uuidv4 } from 'uuid';
import type { Conversation, Message } from '../types/chat';

type ChatState = {
  conversations: Conversation[];
  selectedConversationId?: string;
  selectConversation: (id: string) => void;
  addConversation: (title?:string) => string;
  addMessage: (convId: string, msg: Message) => void;
  updateMessage: (convId: string, msgId: string, patch: Partial<Message>) => void;
};

const useChatStore = create<ChatState>((set, get) => ({
  conversations: [
    { id: '1', title: '示例会话', snippet: '你好，今天天气如何？', messages: [] },
  ],
  selectedConversationId: '1',
  selectConversation: (id) => set({ selectedConversationId: id }),
  addConversation: (title = '新会话') => {
    const id = typeof crypto !== 'undefined' && crypto.randomUUID ? crypto.randomUUID() : uuidv4();
    set((s) => ({ conversations: [{ id, title, snippet: '', messages: [] }, ...s.conversations], selectedConversationId: id }));
    return id;
  },
  addMessage: (convId, msg) => {
    set((s) => ({
      conversations: s.conversations.map((c) => c.id === convId ? { ...c, messages: [...c.messages, msg], snippet: msg.content.slice(0, 120) } : c)
    }));
  },
  updateMessage: (convId, msgId, patch) => {
    set((s) => ({
      conversations: s.conversations.map((c) => c.id === convId ? {
        ...c,
        messages: c.messages.map(m => m.id === msgId ? { ...m, ...patch } : m)
      } : c)
    }));
  },
}));

export default useChatStore;