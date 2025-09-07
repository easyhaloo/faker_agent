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
      listLoading: false, // Separate loading state for list operations
      error: null,
      pagination: {
        currentPage: 1,
        pageSize: 10,
        totalCount: 0,
        hasMore: true,
        isLoadingMore: false
      },
      
      // Initialize store
      initialize: async () => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await conversationService.getConversations();
          set({
            conversations: response.data?.conversations || [],
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
      
      // Smart refresh - only refresh if needed
      refreshConversationsIfNeeded: async () => {
        const { conversations } = get();
        
        // Only refresh if we don't have any conversations or if it's been a while
        if (conversations.length === 0) {
          await get().initialize();
          return;
        }
        
        // Check if any conversation might be outdated (simple heuristic)
        const oldestConversation = conversations[conversations.length - 1];
        const lastUpdate = new Date(oldestConversation.updated_at || 0);
        const now = new Date();
        const hoursSinceUpdate = (now - lastUpdate) / (1000 * 60 * 60);
        
        // Refresh if last update was more than 1 hour ago
        if (hoursSinceUpdate > 1) {
          await get().initialize();
        }
      },
      
      // Background sync - silently update conversations without affecting UI
      backgroundSyncConversations: async () => {
        try {
          const response = await conversationService.getConversations();
          const serverConversations = response.data?.conversations || [];
          
          set(state => {
            // Merge server data with local data, preserving local changes
            const mergedConversations = serverConversations.map(serverConv => {
              const localConv = state.conversations.find(c => c.id === serverConv.id);
              if (localConv) {
                // Preserve local messages and any unsaved changes
                return {
                  ...serverConv,
                  messages: localConv.messages, // Preserve local messages
                  // Add any other local state that should be preserved
                };
              }
              return serverConv;
            });
            
            return {
              conversations: mergedConversations
            };
          });
        } catch (error) {
          console.warn('Background sync failed:', error);
          // Silent fail - don't affect user experience
        }
      },
      
      // Create a new conversation
      // Create a new conversation
      createConversation: async (title = 'New Conversation', initialMessage = null) => {
        set({ isLoading: true, error: null });
        
        try {
          console.log('[DEBUG] Creating conversation with title:', title);
          const response = await conversationService.createConversation({ title });
          const conversation = response.data;
          console.log('[DEBUG] Created conversation:', conversation);
          
          set(state => ({
            conversations: [conversation, ...state.conversations],
            currentConversationId: conversation.id,
            isLoading: false
          }));
          
          // If there's an initial message, send it immediately
          if (initialMessage) {
            await conversationService.sendUserMessage(conversation.id, initialMessage);
            // Reload the conversation to get the official messages
            await get().loadConversation(conversation.id);
          }
          
          // 不需要重新加载整个列表，我们已经在本地更新了数据
          // 只有当其他用户可能修改了列表时才需要刷新
          // await get().initialize();
          
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
        // Check if we already have messages for this conversation
        const existingConversation = get().conversations.find(c => c.id === conversationId);
        if (existingConversation?.messages && existingConversation.messages.length > 0) {
          return; // Already loaded, no need to reload
        }
        
        set({ isLoading: true, error: null });
        
        try {
          const response = await conversationService.getConversation(conversationId);
          const conversationData = response.data;
          
          // Create a combined conversation object with messages
          const conversation = {
            ...conversationData.conversation,
            messages: conversationData.messages || []
          };
          
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
      setCurrentConversation: (conversationId, skipLoad = false) => {
        const currentId = get().currentConversationId;
        
        // Only update if the conversation is actually changing
        if (currentId !== conversationId) {
          set({ currentConversationId: conversationId });
          
          // If we have the conversation but need to load messages
          const conversation = get().conversations.find(c => c.id === conversationId);
          if (conversation && !conversation.messages && !skipLoad) {
            get().loadConversation(conversationId);
          }
        }
      },
      
      // Update conversation title
      updateConversationTitle: async (conversationId, newTitle) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await conversationService.updateConversationTitle(
            conversationId, 
            newTitle
          );
          const updatedConversation = response.data;
          
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
          
          // 不需要重新加载整个列表，我们已经在本地更新了标题
          // 只有当需要同步服务器端变更时才需要刷新
          // await get().initialize();
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
          
          // 不需要重新加载整个列表，我们已经在本地删除了对话
          // 只有当需要同步服务器端变更时才需要刷新
          // await get().initialize();
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
        let { currentConversationId } = get();
        
        // Create a conversation if none exists
        if (!currentConversationId) {
          const newConversationId = await get().createConversation('New Conversation', content);
          if (!newConversationId) return; // Failed to create conversation
          // Update currentConversationId after creating new conversation
          currentConversationId = newConversationId;
        }
        
        const conversationId = currentConversationId;
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
          const response = await conversationService.sendUserMessage(conversationId, content);
          const result = response.data;
          
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
      
      // Load more conversations for pagination
      loadMoreConversations: async (page = 1, limit = 10) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await conversationService.getConversations({ 
            skip: (page - 1) * limit, 
            limit 
          });
          
          set(state => {
            const newConversations = response.data?.conversations || [];
            
            // 如果是第一页，直接替换数据
            if (page === 1) {
              return {
                conversations: newConversations,
                isLoading: false
              };
            }
            
            // 如果不是第一页，合并数据并去重
            const existingIds = new Set(state.conversations.map(c => c.id));
            const uniqueNewConversations = newConversations.filter(
              conversation => !existingIds.has(conversation.id)
            );
            
            return {
              conversations: [...state.conversations, ...uniqueNewConversations],
              isLoading: false
            };
          });
          
          // Return whether there are more conversations to load
          return response.data?.conversations?.length === limit;
        } catch (error) {
          console.error('Error loading more conversations:', error);
          set({
            error: error.message || 'Failed to load conversations',
            isLoading: false
          });
          return false;
        }
      },
      
      // Clear error
      clearError: () => set({ error: null }),
      
      // Set list loading state (separate from main loading)
      setListLoading: (loading) => set({ listLoading: loading }),
      
      // Update pagination state
      updatePagination: (updates) => set(state => ({
        pagination: { ...state.pagination, ...updates }
      })),
      
      // Load conversations with proper pagination - optimized to prevent unnecessary re-renders
      loadConversationsPage: async (page = 1, append = false) => {
        const { pagination } = get();
        const pageSize = pagination.pageSize;
        
        // Set appropriate loading state
        if (append) {
          set(state => ({
            pagination: { ...state.pagination, isLoadingMore: true }
          }));
        } else if (page === 1) {
          // Only show loading for first page, not for refresh
          set({ listLoading: true });
        }
        
        try {
          const response = await conversationService.getConversations({ 
            skip: (page - 1) * pageSize, 
            limit: pageSize 
          });
          
          const newConversations = response.data?.conversations || [];
          const totalCount = response.data?.total_count || 0;
          
          set(state => {
            let updatedConversations;
            
            if (append) {
              // Append mode: add to existing conversations
              const existingIds = new Set(state.conversations.map(c => c.id));
              const uniqueNewConversations = newConversations.filter(
                conversation => !existingIds.has(conversation.id)
              );
              
              // If no new conversations, don't update state to prevent re-render
              if (uniqueNewConversations.length === 0) {
                return {
                  pagination: {
                    ...state.pagination,
                    hasMore: false,
                    isLoadingMore: false
                  },
                  listLoading: false
                };
              }
              
              // Append new conversations to the end without replacing existing ones
              updatedConversations = [...state.conversations, ...uniqueNewConversations];
            } else {
              // Replace mode: only for first page
              // Use efficient comparison to prevent unnecessary re-renders
              const conversationsEqual = state.conversations.length === newConversations.length &&
                state.conversations.every((conv, index) => conv.id === newConversations[index]?.id);
              
              if (conversationsEqual) {
                return {
                  pagination: {
                    ...state.pagination,
                    currentPage: page,
                    totalCount,
                    hasMore: newConversations.length === pageSize,
                    isLoadingMore: false
                  },
                  listLoading: false,
                  error: null
                };
              }
              updatedConversations = newConversations;
            }
            
            return {
              conversations: updatedConversations,
              pagination: {
                ...state.pagination,
                currentPage: page,
                totalCount,
                hasMore: newConversations.length === pageSize,
                isLoadingMore: false
              },
              listLoading: false,
              error: null
            };
          });
          
          return {
            conversations: newConversations,
            hasMore: newConversations.length === pageSize,
            totalCount
          };
        } catch (error) {
          console.error('Error loading conversations page:', error);
          set({
            listLoading: false,
            pagination: {
              ...get().pagination,
              isLoadingMore: false
            },
            error: error.message || 'Failed to load conversations'
          });
          return { conversations: [], hasMore: false, totalCount: 0 };
        }
      },
      
      // Load next page (for infinite scroll) - optimized for seamless pagination
      loadNextPage: async () => {
        const { pagination } = get();
        if (pagination.isLoadingMore || !pagination.hasMore) return false;
        
        const nextPage = pagination.currentPage + 1;
        const result = await get().loadConversationsPage(nextPage, true);
        
        return result.hasMore;
      }
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