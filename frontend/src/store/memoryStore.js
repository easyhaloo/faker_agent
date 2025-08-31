import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { memoryService } from '../services/memoryService';

export const useMemoryStore = create(
  persist(
    (set, get) => ({
      // State
      profileMemories: [],
      episodeMemories: {},
      summaries: {},
      settings: {
        use_global_memory: true,
        use_project_memory: true,
        project_id: null,
        use_session_memory: true,
        enable_memory_writing: true,
        enable_rolling_summary: true,
        max_context_messages: 20,
        summary_token_threshold: 4000,
      },
      auditLogs: [],
      isLoading: false,
      error: null,
      
      // Initialize
      initialize: () => {
        set({
          profileMemories: [],
          episodeMemories: {},
          summaries: {},
          settings: {
            use_global_memory: true,
            use_project_memory: true,
            project_id: null,
            use_session_memory: true,
            enable_memory_writing: true,
            enable_rolling_summary: true,
            max_context_messages: 20,
            summary_token_threshold: 4000,
          },
          auditLogs: [],
          isLoading: false,
          error: null,
        });
      },
      
      // Set loading state
      setLoading: (loading) => set({ isLoading: loading }),
      
      // Set error
      setError: (error) => set({ error }),
      
      // Clear error
      clearError: () => set({ error: null }),
      
      // Profile memory operations
      
      // Fetch profile memories
      fetchProfileMemories: async (options = {}) => {
        get().setLoading(true);
        get().clearError();
        try {
          const memories = await memoryService.getProfileMemories(options);
          set({ profileMemories: memories });
          get().setLoading(false);
          return memories;
        } catch (error) {
          get().setError(error.message || 'Failed to fetch profile memories');
          get().setLoading(false);
          throw error;
        }
      },
      
      // Create profile memory
      createProfileMemory: async (memory) => {
        get().setLoading(true);
        get().clearError();
        try {
          const createdMemory = await memoryService.createProfileMemory(memory);
          set((state) => ({
            profileMemories: [...state.profileMemories, createdMemory]
          }));
          get().setLoading(false);
          return createdMemory;
        } catch (error) {
          get().setError(error.message || 'Failed to create profile memory');
          get().setLoading(false);
          throw error;
        }
      },
      
      // Update profile memory
      updateProfileMemory: async (memoryId, updates) => {
        get().setLoading(true);
        get().clearError();
        try {
          const updatedMemory = await memoryService.updateProfileMemory(memoryId, updates);
          set((state) => ({
            profileMemories: state.profileMemories.map(mem => 
              mem.id === memoryId ? updatedMemory : mem
            )
          }));
          get().setLoading(false);
          return updatedMemory;
        } catch (error) {
          get().setError(error.message || `Failed to update profile memory ${memoryId}`);
          get().setLoading(false);
          throw error;
        }
      },
      
      // Delete profile memory
      deleteProfileMemory: async (memoryId) => {
        get().setLoading(true);
        get().clearError();
        try {
          await memoryService.deleteProfileMemory(memoryId);
          set((state) => ({
            profileMemories: state.profileMemories.filter(mem => mem.id !== memoryId)
          }));
          get().setLoading(false);
          return { success: true };
        } catch (error) {
          get().setError(error.message || `Failed to delete profile memory ${memoryId}`);
          get().setLoading(false);
          throw error;
        }
      },
      
      // Episode memory operations
      
      // Fetch episode memories
      fetchEpisodeMemories: async (conversationId, memoryType = null) => {
        get().setLoading(true);
        get().clearError();
        try {
          const memories = await memoryService.getEpisodeMemories(conversationId, memoryType);
          set((state) => ({
            episodeMemories: {
              ...state.episodeMemories,
              [conversationId]: memories
            }
          }));
          get().setLoading(false);
          return memories;
        } catch (error) {
          get().setError(error.message || `Failed to fetch episode memories for conversation ${conversationId}`);
          get().setLoading(false);
          throw error;
        }
      },
      
      // Create episode memory
      createEpisodeMemory: async (memory) => {
        get().setLoading(true);
        get().clearError();
        try {
          const createdMemory = await memoryService.createEpisodeMemory(memory);
          set((state) => {
            const conversationId = memory.conversation_id;
            const existingMemories = state.episodeMemories[conversationId] || [];
            return {
              episodeMemories: {
                ...state.episodeMemories,
                [conversationId]: [...existingMemories, createdMemory]
              }
            };
          });
          get().setLoading(false);
          return createdMemory;
        } catch (error) {
          get().setError(error.message || 'Failed to create episode memory');
          get().setLoading(false);
          throw error;
        }
      },
      
      // Update episode memory
      updateEpisodeMemory: async (memoryId, updates) => {
        get().setLoading(true);
        get().clearError();
        try {
          const updatedMemory = await memoryService.updateEpisodeMemory(memoryId, updates);
          set((state) => {
            const conversationId = updatedMemory.conversation_id;
            const existingMemories = state.episodeMemories[conversationId] || [];
            return {
              episodeMemories: {
                ...state.episodeMemories,
                [conversationId]: existingMemories.map(mem => 
                  mem.id === memoryId ? updatedMemory : mem
                )
              }
            };
          });
          get().setLoading(false);
          return updatedMemory;
        } catch (error) {
          get().setError(error.message || `Failed to update episode memory ${memoryId}`);
          get().setLoading(false);
          throw error;
        }
      },
      
      // Delete episode memory
      deleteEpisodeMemory: async (memoryId, conversationId) => {
        get().setLoading(true);
        get().clearError();
        try {
          await memoryService.deleteEpisodeMemory(memoryId);
          set((state) => {
            const existingMemories = state.episodeMemories[conversationId] || [];
            return {
              episodeMemories: {
                ...state.episodeMemories,
                [conversationId]: existingMemories.filter(mem => mem.id !== memoryId)
              }
            };
          });
          get().setLoading(false);
          return { success: true };
        } catch (error) {
          get().setError(error.message || `Failed to delete episode memory ${memoryId}`);
          get().setLoading(false);
          throw error;
        }
      },
      
      // Summary operations
      
      // Fetch conversation summary
      fetchConversationSummary: async (conversationId) => {
        get().setLoading(true);
        get().clearError();
        try {
          const summary = await memoryService.getConversationSummary(conversationId);
          set((state) => ({
            summaries: {
              ...state.summaries,
              [conversationId]: summary
            }
          }));
          get().setLoading(false);
          return summary;
        } catch (error) {
          get().setError(error.message || `Failed to fetch summary for conversation ${conversationId}`);
          get().setLoading(false);
          throw error;
        }
      },
      
      // Settings operations
      
      // Fetch memory settings
      fetchMemorySettings: async (userId = 'default_user') => {
        get().setLoading(true);
        get().clearError();
        try {
          const settings = await memoryService.getMemorySettings(userId);
          set({ settings });
          get().setLoading(false);
          return settings;
        } catch (error) {
          get().setError(error.message || 'Failed to fetch memory settings');
          get().setLoading(false);
          throw error;
        }
      },
      
      // Update memory settings
      updateMemorySettings: async (settings, userId = 'default_user') => {
        get().setLoading(true);
        get().clearError();
        try {
          const updatedSettings = await memoryService.updateMemorySettings(settings, userId);
          set({ settings: updatedSettings });
          get().setLoading(false);
          return updatedSettings;
        } catch (error) {
          get().setError(error.message || 'Failed to update memory settings');
          get().setLoading(false);
          throw error;
        }
      },
      
      // Audit log operations
      
      // Fetch memory audit logs
      fetchMemoryAuditLogs: async (options = {}) => {
        get().setLoading(true);
        get().clearError();
        try {
          const logs = await memoryService.getMemoryAuditLogs(options);
          set({ auditLogs: logs });
          get().setLoading(false);
          return logs;
        } catch (error) {
          get().setError(error.message || 'Failed to fetch memory audit logs');
          get().setLoading(false);
          throw error;
        }
      },
      
      // Helper methods
      
      // Set memory settings directly (without API call)
      setMemorySettings: (settings) => set({ settings }),
      
      // Toggle a memory setting
      toggleMemorySetting: (settingName) => {
        if (!Object.keys(get().settings).includes(settingName)) {
          console.error(`Invalid setting name: ${settingName}`);
          return;
        }
        
        set((state) => ({
          settings: {
            ...state.settings,
            [settingName]: !state.settings[settingName]
          }
        }));
      },
      
      // Set project ID for project-scoped memory
      setProjectId: (projectId) => set((state) => ({
        settings: {
          ...state.settings,
          project_id: projectId
        }
      })),
      
      // Clear all memories
      clearAllMemories: async () => {
        get().setLoading(true);
        get().clearError();
        
        try {
          // This would need API endpoints to clear all memories
          // For now, just clear the local state
          set({
            profileMemories: [],
            episodeMemories: {},
            summaries: {}
          });
          
          get().setLoading(false);
          return { success: true };
        } catch (error) {
          get().setError(error.message || 'Failed to clear all memories');
          get().setLoading(false);
          throw error;
        }
      },
    }),
    {
      name: 'memory-storage',
      partialize: (state) => ({
        settings: state.settings,
        // Only persist settings, not the actual memories
      }),
    }
  )
);

export default useMemoryStore;