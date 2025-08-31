/**
 * Conversation Service
 * 
 * Provides APIs for conversation management, including creating, retrieving,
 * updating, and deleting conversations, as well as adding messages.
 */
import { apiClient } from './apiClient';

// API endpoint prefix
const CONVERSATIONS_ENDPOINT = '/conversations';

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
 * @returns {Promise<Object>} - List of conversations with pagination info
 */
export const getConversations = async (options = {}) => {
  try {
    const { skip = 0, limit = 10 } = options;
    const response = await apiClient.get(CONVERSATIONS_ENDPOINT, {
      params: { skip, limit }
    });
    
    return response.data;
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
    const response = await apiClient.get(`${CONVERSATIONS_ENDPOINT}/${conversationId}`);
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
    const response = await apiClient.put(`${CONVERSATIONS_ENDPOINT}/${conversationId}`, data);
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
    const response = await apiClient.put(`${CONVERSATIONS_ENDPOINT}/${conversationId}/title`, { title });
    return response.data;
  } catch (error) {
    console.error(`Error updating conversation title ${conversationId}:`, error);
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
    const response = await apiClient.delete(`${CONVERSATIONS_ENDPOINT}/${conversationId}`);
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
    const response = await apiClient.post(`${CONVERSATIONS_ENDPOINT}/${conversationId}/messages`, {
      role: message.role,
      content: message.content,
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
    const response = await apiClient.post(`${CONVERSATIONS_ENDPOINT}/${conversationId}/messages`, {
      role: 'user',
      content
    });
    
    return response.data;
  } catch (error) {
    console.error(`Error sending user message to conversation ${conversationId}:`, error);
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
  sendUserMessage
};