/**
 * Conversation Service
 * 
 * Provides APIs for conversation management, including creating, retrieving,
 * updating, and deleting conversations, as well as adding messages.
 */
import { apiClient } from './apiClient';

// API endpoint prefix
const CONVERSATIONS_ENDPOINT = '/conversations/';

/**
 * Create a new conversation
 * 
 * @param {Object} data - Conversation data
 * @param {string} data.title - Conversation title (optional, defaults to "New Conversation")
 * @param {Object} data.metadata - Additional metadata (optional)
 * @returns {Promise<Object>} - Created conversation
 */
export const createConversation = async (data = {}) => {
  try {
    const response = await apiClient.post(CONVERSATIONS_ENDPOINT, {
      title: data.title || 'New Conversation',
      metadata: data.metadata || {}
    });
    
    return response.data;
  } catch (error) {
    console.error('Error creating conversation:', error);
    throw error;
  }
};

/**
 * Get all conversations with pagination
 * 
 * @param {Object} options - Query options
 * @param {number} options.skip - Number of conversations to skip (default: 0)
 * @param {number} options.limit - Maximum number of conversations to return (default: 10)
 * @param {boolean} options.include_total - Whether to include total count (default: true)
 * @returns {Promise<Object>} - List of conversations with pagination info
 */
export const getConversations = async (options = {}) => {
  try {
    const { skip = 0, limit = 10, include_total = true } = options;
    const response = await apiClient.get(CONVERSATIONS_ENDPOINT, {
      params: { skip, limit, include_total }
    });
    
    // Ensure response has proper pagination structure
    const data = response.data;
    if (data.data && Array.isArray(data.data.conversations)) {
      return {
        status: 'success',
        data: {
          conversations: data.data.conversations,
          total_count: data.data.total_count || 0,
          skip: data.data.skip || skip,
          limit: data.data.limit || limit
        }
      };
    }
    
    return data;
  } catch (error) {
    console.error('Error fetching conversations:', error);
    throw error;
  }
};

/**
 * Get a single conversation by ID with its messages
 * 
 * @param {string} conversationId - Conversation ID
 * @returns {Promise<Object>} - Conversation with messages
 */
export const getConversation = async (conversationId) => {
  try {
    // Remove trailing slash from CONVERSATIONS_ENDPOINT to avoid double slashes
    const endpoint = CONVERSATIONS_ENDPOINT.endsWith('/') 
      ? CONVERSATIONS_ENDPOINT.slice(0, -1) 
      : CONVERSATIONS_ENDPOINT;
    const response = await apiClient.get(`${endpoint}/${conversationId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching conversation ${conversationId}:`, error);
    throw error;
  }
};

/**
 * Update a conversation
 * 
 * @param {string} conversationId - Conversation ID
 * @param {Object} data - Data to update
 * @param {string} data.title - New conversation title (optional)
 * @param {Object} data.metadata - New metadata (optional)
 * @returns {Promise<Object>} - Updated conversation
 */
export const updateConversation = async (conversationId, data = {}) => {
  try {
    // Remove trailing slash from CONVERSATIONS_ENDPOINT to avoid double slashes
    const endpoint = CONVERSATIONS_ENDPOINT.endsWith('/') 
      ? CONVERSATIONS_ENDPOINT.slice(0, -1) 
      : CONVERSATIONS_ENDPOINT;
    const response = await apiClient.put(`${endpoint}/${conversationId}`, data);
    return response.data;
  } catch (error) {
    console.error(`Error updating conversation ${conversationId}:`, error);
    throw error;
  }
};

/**
 * Update just the title of a conversation
 * 
 * @param {string} conversationId - Conversation ID
 * @param {string} title - New title
 * @returns {Promise<Object>} - Updated conversation
 */
export const updateConversationTitle = async (conversationId, title) => {
  try {
    console.log(`[DEBUG] ConversationService: Updating title for ${conversationId} to: ${title}`);
    // Remove trailing slash from CONVERSATIONS_ENDPOINT to avoid double slashes
    const endpoint = CONVERSATIONS_ENDPOINT.endsWith('/') 
      ? CONVERSATIONS_ENDPOINT.slice(0, -1) 
      : CONVERSATIONS_ENDPOINT;
    const url = `${endpoint}/${conversationId}`;
    console.log(`[DEBUG] ConversationService: Making PUT request to ${url}`);
    const response = await apiClient.put(url, { title });
    console.log(`[DEBUG] ConversationService: API response status:`, response.status);
    console.log(`[DEBUG] ConversationService: API response data:`, response.data);
    return response.data;
  } catch (error) {
    console.error(`Error updating conversation title ${conversationId}:`, error);
    console.error(`Error details:`, error.response?.data, error.response?.status);
    throw error;
  }
};

/**
 * Delete a conversation
 * 
 * @param {string} conversationId - Conversation ID
 * @returns {Promise<Object>} - Success message
 */
export const deleteConversation = async (conversationId) => {
  try {
    // Remove trailing slash from CONVERSATIONS_ENDPOINT to avoid double slashes
    const endpoint = CONVERSATIONS_ENDPOINT.endsWith('/') 
      ? CONVERSATIONS_ENDPOINT.slice(0, -1) 
      : CONVERSATIONS_ENDPOINT;
    const response = await apiClient.delete(`${endpoint}/${conversationId}`);
    return response.data;
  } catch (error) {
    console.error(`Error deleting conversation ${conversationId}:`, error);
    throw error;
  }
};

/**
 * Add a message to a conversation
 * 
 * @param {string} conversationId - Conversation ID
 * @param {Object} message - Message data
 * @param {string} message.role - Message role ('user', 'assistant', etc.)
 * @param {string} message.content - Message content
 * @param {Object} message.metadata - Additional metadata (optional)
 * @returns {Promise<Object>} - Success message with message ID
 */
export const addMessage = async (conversationId, message) => {
  try {
    // Remove trailing slash from CONVERSATIONS_ENDPOINT to avoid double slashes
    const endpoint = CONVERSATIONS_ENDPOINT.endsWith('/') 
      ? CONVERSATIONS_ENDPOINT.slice(0, -1) 
      : CONVERSATIONS_ENDPOINT;
    const response = await apiClient.post(`${endpoint}/${conversationId}/messages`, {
      role: message.role,
      message: message.content,
      metadata: message.metadata || {}
    });
    
    return response.data;
  } catch (error) {
    console.error(`Error adding message to conversation ${conversationId}:`, error);
    throw error;
  }
};

/**
 * Send a user message and get the assistant's response
 * 
 * This is a convenience method that combines adding a user message
 * and handles the assistant's response automatically.
 * 
 * @param {string} conversationId - Conversation ID
 * @param {string} content - User message content
 * @returns {Promise<Object>} - Message IDs (user message and assistant response)
 */
export const sendUserMessage = async (conversationId, content) => {
  try {
    // Remove trailing slash from CONVERSATIONS_ENDPOINT to avoid double slashes
    const endpoint = CONVERSATIONS_ENDPOINT.endsWith('/') 
      ? CONVERSATIONS_ENDPOINT.slice(0, -1) 
      : CONVERSATIONS_ENDPOINT;
    const response = await apiClient.post(`${endpoint}/${conversationId}/messages`, {
      message: content
    });
    
    return response.data;
  } catch (error) {
    console.error(`Error sending user message to conversation ${conversationId}:`, error);
    throw error;
  }
};

/**
 * Export a conversation in various formats
 * 
 * @param {string} conversationId - Conversation ID
 * @param {string} format - Export format (json, txt, md)
 * @returns {Promise<Object>} - Exported conversation data
 */
export const exportConversation = async (conversationId, format = 'json') => {
  try {
    console.log(`[DEBUG] Exporting conversation ${conversationId} in ${format} format`);
    // Remove trailing slash from CONVERSATIONS_ENDPOINT to avoid double slashes
    const endpoint = CONVERSATIONS_ENDPOINT.endsWith('/') 
      ? CONVERSATIONS_ENDPOINT.slice(0, -1) 
      : CONVERSATIONS_ENDPOINT;
    const url = `${endpoint}/${conversationId}/export`;
    console.log(`[DEBUG] Making GET request to ${url}?format=${format}`);
    
    const response = await apiClient.get(url, {
      params: { format }
    });
    
    console.log(`[DEBUG] Export API response:`, response.data);
    return response.data;
  } catch (error) {
    console.error(`Error exporting conversation ${conversationId}:`, error);
    console.error(`Error details:`, error.response?.data, error.response?.status);
    throw error;
  }
};

export const conversationService = {
  createConversation,
  getConversations,
  getConversation,
  updateConversation,
  updateConversationTitle,
  deleteConversation,
  addMessage,
  sendUserMessage,
  exportConversation
};