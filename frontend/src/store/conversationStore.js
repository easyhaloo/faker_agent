/**
 * Conversation Store
 * 
 * Manages conversation state for the application, including conversations list,
 * active conversation, messages, and loading states.
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { conversationService } from '../services/conversationService';

export const useConversationStore = create(
  persist(
    (set, get) => ({
      // State
      conversations: [],
      currentConversationId: null,
      isLoading: false,
      error: null,
      
      // Initialize store
      initialize: async () => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await conversationService.getConversations();
          set({
            conversations: response.conversations || [],
            isLoading: false
          });
        } catch (error) {
          console.error('Error initializing conversation store:', error);
          set({
            error: error.message || 'Failed to load conversations',
            isLoading: false
          });
        }
      },
      
      // Create a new conversation
      createConversation: async (title = 'New Conversation') => {
        set({ isLoading: true, error: null });
        
        try {
          const conversation = await conversationService.createConversation({ title });
          
          set(state => ({
            conversations: [conversation, ...state.conversations],
            currentConversationId: conversation.id,
            isLoading: false
          }));
          
          return conversation.id;
        } catch (error) {
          console.error('Error creating conversation:', error);
          set({
            error: error.message || 'Failed to create conversation',
            isLoading: false
          });
          return null;
        }
      },
      
      // Load a specific conversation with messages
      loadConversation: async (conversationId) => {
        set({ isLoading: true, error: null });
        
        try {
          const conversation = await conversationService.getConversation(conversationId);
          
          // Update the conversation in the list
          set(state => {
            const updatedConversations = state.conversations.map(conv => 
              conv.id === conversationId ? conversation : conv
            );
            
            return {
              conversations: updatedConversations,
              currentConversationId: conversationId,
              isLoading: false
            };
          });
        } catch (error) {
          console.error(`Error loading conversation ${conversationId}:`, error);
          set({
            error: error.message || 'Failed to load conversation',
            isLoading: false
          });
        }
      },
      
      // Set the current conversation
      setCurrentConversation: (conversationId) => {
        set({ currentConversationId: conversationId });
        
        // If we have the conversation but need to load messages
        const conversation = get().conversations.find(c => c.id === conversationId);
        if (conversation && !conversation.messages) {
          get().loadConversation(conversationId);
        }
      },
      
      // Update conversation title
      updateConversationTitle: async (conversationId, newTitle) => {
        set({ isLoading: true, error: null });
        
        try {
          const updatedConversation = await conversationService.updateConversationTitle(
            conversationId, 
            newTitle
          );
          
          // Update the conversation in the list
          set(state => {
            const updatedConversations = state.conversations.map(conv => 
              conv.id === conversationId ? updatedConversation : conv
            );
            
            return {
              conversations: updatedConversations,
              isLoading: false
            };
          });
        } catch (error) {
          console.error(`Error updating conversation title ${conversationId}:`, error);
          set({
            error: error.message || 'Failed to update conversation title',
            isLoading: false
          });
        }
      },
      
      // Delete a conversation
      deleteConversation: async (conversationId) => {
        set({ isLoading: true, error: null });
        
        try {
          await conversationService.deleteConversation(conversationId);
          
          // Remove the conversation from the list
          set(state => {
            const updatedConversations = state.conversations.filter(
              conv => conv.id !== conversationId
            );
            
            // If we're deleting the current conversation, set a new current
            let newCurrentId = state.currentConversationId;
            if (state.currentConversationId === conversationId) {
              newCurrentId = updatedConversations[0]?.id || null;
            }
            
            return {
              conversations: updatedConversations,
              currentConversationId: newCurrentId,
              isLoading: false
            };
          });
        } catch (error) {
          console.error(`Error deleting conversation ${conversationId}:`, error);
          set({
            error: error.message || 'Failed to delete conversation',
            isLoading: false
          });
        }
      },
      
      // Send a user message and get response
      sendMessage: async (content) => {
        const { currentConversationId } = get();
        
        // Create a conversation if none exists
        if (!currentConversationId) {
          const newConversationId = await get().createConversation();
          if (!newConversationId) return; // Failed to create conversation
        }
        
        const conversationId = get().currentConversationId;
        set({ isLoading: true, error: null });
        
        try {
          // Optimistically add user message to the UI
          const tempUserMessageId = Date.now().toString();
          set(state => {
            const currentConversation = state.conversations.find(
              c => c.id === conversationId
            );
            
            if (!currentConversation) return state; // Shouldn't happen
            
            const messages = [...(currentConversation.messages || [])];
            messages.push({
              id: tempUserMessageId,
              conversation_id: conversationId,
              role: 'user',
              content,
              created_at: new Date().toISOString()
            });
            
            const updatedConversation = {
              ...currentConversation,
              messages,
              updated_at: new Date().toISOString()
            };
            
            const updatedConversations = state.conversations.map(conv => 
              conv.id === conversationId ? updatedConversation : conv
            );
            
            return {
              conversations: updatedConversations
            };
          });
          
          // Send message to API
          const result = await conversationService.sendUserMessage(conversationId, content);
          
          // Reload the conversation to get the official messages
          await get().loadConversation(conversationId);
          
          set({ isLoading: false });
        } catch (error) {
          console.error(`Error sending message to conversation ${conversationId}:`, error);
          set({
            error: error.message || 'Failed to send message',
            isLoading: false
          });
        }
      },
      
      // Clear error
      clearError: () => set({ error: null })
    }),
    {
      name: 'conversation-storage',
      partialize: (state) => ({
        conversations: state.conversations.map(conv => ({
          id: conv.id,
          title: conv.title,
          created_at: conv.created_at,
          updated_at: conv.updated_at,
          message_count: conv.message_count,
          last_message: conv.last_message
        })), // Store conversations without messages for persistence
        currentConversationId: state.currentConversationId
      })
    }
  )
);

export default useConversationStore;