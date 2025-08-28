import { create } from 'zustand';
import { Session, ChatMessage } from '../types/chat';

interface ChatStore {
  sessions: Session[];
  currentSessionId: string | null;
  loading: boolean;
  addMessage: (message: ChatMessage) => void;
  addMessageToSession: (sessionId: string, message: ChatMessage) => void;
  setLoading: (loading: boolean) => void;
  clearMessages: () => void;
  addSession: (name: string) => string;
  deleteSession: (id: string) => void;
  setCurrentSession: (id: string) => void;
  updateMessage: (id: string, updates: Partial<ChatMessage>) => void;
}

export const useChatStore = create<ChatStore>((set, get) => ({
  sessions: [{
    id: 'default',
    name: '默认会话',
    messages: [{
      id: '1',
      sender: "ai",
      content: "Hello! How can I help you today?",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  }],
  currentSessionId: 'default',
  loading: false,
  
  addMessage: (message) => set((state) => {
    if (!state.currentSessionId) return state;
    
    const updatedSessions = state.sessions.map(session => {
      if (session.id === state.currentSessionId) {
        return {
          ...session,
          messages: [...session.messages, message],
          updatedAt: new Date().toISOString()
        };
      }
      return session;
    });
    
    return { sessions: updatedSessions };
  }),
  
  addMessageToSession: (sessionId, message) => set((state) => {
    const updatedSessions = state.sessions.map(session => {
      if (session.id === sessionId) {
        return {
          ...session,
          messages: [...session.messages, message],
          updatedAt: new Date().toISOString()
        };
      }
      return session;
    });
    
    return { sessions: updatedSessions };
  }),
  
  setLoading: (loading) => set({ loading }),
  
  clearMessages: () => set((state) => {
    if (!state.currentSessionId) return state;
    
    const updatedSessions = state.sessions.map(session => {
      if (session.id === state.currentSessionId) {
        return {
          ...session,
          messages: []
        };
      }
      return session;
    });
    
    return { sessions: updatedSessions };
  }),
  
  addSession: (name) => {
    const newSessionId = Date.now().toString();
    set((state) => ({
      sessions: [
        ...state.sessions,
        {
          id: newSessionId,
          name,
          messages: [],
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        }
      ]
    }));
    return newSessionId;
  },
  
  deleteSession: (id) => set((state) => {
    // 不允许删除最后一个会话
    if (state.sessions.length <= 1) return state;
    
    const updatedSessions = state.sessions.filter(session => session.id !== id);
    let newCurrentSessionId = state.currentSessionId;
    
    // 如果删除的是当前会话，切换到第一个会话
    if (state.currentSessionId === id) {
      newCurrentSessionId = updatedSessions[0]?.id || null;
    }
    
    return { 
      sessions: updatedSessions,
      currentSessionId: newCurrentSessionId
    };
  }),
  
  setCurrentSession: (id) => set({ currentSessionId: id }),
  
  updateMessage: (id, updates) => set((state) => {
    if (!state.currentSessionId) return state;
    
    const updatedSessions = state.sessions.map(session => {
      if (session.id === state.currentSessionId) {
        return {
          ...session,
          messages: session.messages.map(msg => 
            msg.id === id ? { ...msg, ...updates } : msg
          ),
          updatedAt: new Date().toISOString()
        };
      }
      return session;
    });
    
    return { sessions: updatedSessions };
  })
}));