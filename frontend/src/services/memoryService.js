import { apiClient } from './apiClient';

/**
 * Memory service for interacting with the memory API.
 */
export const memoryService = {
  /**
   * Get profile memories.
   * 
   * @param {Object} options - Query options
   * @param {string} options.scope - Memory scope (global, project, session)
   * @param {string} options.project_id - Project ID for project-scoped memories
   * @param {string} options.memory_type - Memory type filter
   * @param {string} options.key - Key filter
   * @param {string} options.user_id - User ID filter
   * @returns {Promise<Object>} Response with memories
   */
  async getProfileMemories(options = {}) {
    try {
      const queryParams = new URLSearchParams();
      
      if (options.scope) queryParams.append('scope', options.scope);
      if (options.project_id) queryParams.append('project_id', options.project_id);
      if (options.memory_type) queryParams.append('memory_type', options.memory_type);
      if (options.key) queryParams.append('key', options.key);
      if (options.user_id) queryParams.append('user_id', options.user_id);
      
      const response = await apiClient.get(`/memory/profile?${queryParams.toString()}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching profile memories:', error);
      throw error;
    }
  },
  
  /**
   * Create a new profile memory.
   * 
   * @param {Object} memory - Memory data
   * @returns {Promise<Object>} Created memory
   */
  async createProfileMemory(memory) {
    try {
      const response = await apiClient.post('/memory/profile', memory);
      return response.data;
    } catch (error) {
      console.error('Error creating profile memory:', error);
      throw error;
    }
  },
  
  /**
   * Update an existing profile memory.
   * 
   * @param {string} memoryId - Memory ID
   * @param {Object} updates - Updates to apply
   * @returns {Promise<Object>} Updated memory
   */
  async updateProfileMemory(memoryId, updates) {
    try {
      const response = await apiClient.put(`/memory/profile/${memoryId}`, updates);
      return response.data;
    } catch (error) {
      console.error(`Error updating profile memory ${memoryId}:`, error);
      throw error;
    }
  },
  
  /**
   * Delete a profile memory.
   * 
   * @param {string} memoryId - Memory ID
   * @returns {Promise<Object>} Deletion result
   */
  async deleteProfileMemory(memoryId) {
    try {
      const response = await apiClient.delete(`/memory/profile/${memoryId}`);
      return response.data;
    } catch (error) {
      console.error(`Error deleting profile memory ${memoryId}:`, error);
      throw error;
    }
  },
  
  /**
   * Get episode memories for a conversation.
   * 
   * @param {string} conversationId - Conversation ID
   * @param {string} memoryType - Optional memory type filter
   * @returns {Promise<Object>} Response with memories
   */
  async getEpisodeMemories(conversationId, memoryType = null) {
    try {
      let url = `/memory/episode/${conversationId}`;
      if (memoryType) {
        url += `?memory_type=${memoryType}`;
      }
      
      const response = await apiClient.get(url);
      return response.data;
    } catch (error) {
      console.error(`Error fetching episode memories for conversation ${conversationId}:`, error);
      throw error;
    }
  },
  
  /**
   * Create a new episode memory.
   * 
   * @param {Object} memory - Memory data
   * @returns {Promise<Object>} Created memory
   */
  async createEpisodeMemory(memory) {
    try {
      const response = await apiClient.post('/memory/episode', memory);
      return response.data;
    } catch (error) {
      console.error('Error creating episode memory:', error);
      throw error;
    }
  },
  
  /**
   * Update an existing episode memory.
   * 
   * @param {string} memoryId - Memory ID
   * @param {Object} updates - Updates to apply
   * @returns {Promise<Object>} Updated memory
   */
  async updateEpisodeMemory(memoryId, updates) {
    try {
      const response = await apiClient.put(`/memory/episode/${memoryId}`, updates);
      return response.data;
    } catch (error) {
      console.error(`Error updating episode memory ${memoryId}:`, error);
      throw error;
    }
  },
  
  /**
   * Delete an episode memory.
   * 
   * @param {string} memoryId - Memory ID
   * @returns {Promise<Object>} Deletion result
   */
  async deleteEpisodeMemory(memoryId) {
    try {
      const response = await apiClient.delete(`/memory/episode/${memoryId}`);
      return response.data;
    } catch (error) {
      console.error(`Error deleting episode memory ${memoryId}:`, error);
      throw error;
    }
  },
  
  /**
   * Get the latest conversation summary.
   * 
   * @param {string} conversationId - Conversation ID
   * @returns {Promise<Object>} Latest summary or null
   */
  async getConversationSummary(conversationId) {
    try {
      const response = await apiClient.get(`/memory/summary/${conversationId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching summary for conversation ${conversationId}:`, error);
      throw error;
    }
  },
  
  /**
   * Get memory settings.
   * 
   * @param {string} userId - Optional user ID
   * @returns {Promise<Object>} Memory settings
   */
  async getMemorySettings(userId = 'default_user') {
    try {
      const response = await apiClient.get(`/memory/settings?user_id=${userId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching memory settings:', error);
      throw error;
    }
  },
  
  /**
   * Update memory settings.
   * 
   * @param {Object} settings - Memory settings
   * @param {string} userId - Optional user ID
   * @returns {Promise<Object>} Updated settings
   */
  async updateMemorySettings(settings, userId = 'default_user') {
    try {
      const response = await apiClient.post('/memory/settings', {
        ...settings,
        user_id: userId
      });
      return response.data;
    } catch (error) {
      console.error('Error updating memory settings:', error);
      throw error;
    }
  },
  
  /**
   * Get memory audit logs.
   * 
   * @param {Object} options - Query options
   * @param {string} options.target_type - Target type filter
   * @param {string} options.action - Action filter
   * @param {number} options.limit - Max number of logs to return
   * @returns {Promise<Object>} Response with audit logs
   */
  async getMemoryAuditLogs(options = {}) {
    try {
      const queryParams = new URLSearchParams();
      
      if (options.target_type) queryParams.append('target_type', options.target_type);
      if (options.action) queryParams.append('action', options.action);
      if (options.limit) queryParams.append('limit', options.limit);
      
      const response = await apiClient.get(`/memory/audit?${queryParams.toString()}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching memory audit logs:', error);
      throw error;
    }
  },
};

export default memoryService;