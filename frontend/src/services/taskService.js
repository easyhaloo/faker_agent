"""
Frontend service for real-time task status updates.
"""
import axios from 'axios';

// API base URL
const API_BASE_URL = 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

/**
 * Submit a task to the agent asynchronously.
 * @param {string} query - The query to process
 * @returns {Promise<Object>} The task submission response
 */
export async function submitTask(query) {
  try {
    const response = await api.post('/agent/task/async', { query });
    return response.data;
  } catch (error) {
    console.error('Error submitting task:', error);
    throw error;
  }
}

/**
 * Get the status of a task.
 * @param {string} taskId - The task ID
 * @returns {Promise<Object>} The task status
 */
export async function getTaskStatus(taskId) {
  try {
    const response = await api.get(`/agent/task/${taskId}`);
    return response.data;
  } catch (error) {
    console.error('Error getting task status:', error);
    throw error;
  }
}

/**
 * Stream task status updates in real-time.
 * @param {string} taskId - The task ID
 * @param {Function} onProgress - Callback function to handle progress updates
 * @returns {EventSource} The EventSource connection
 */
export function streamTaskStatus(taskId, onProgress) {
  // Create EventSource connection
  const eventSource = new EventSource(`${API_BASE_URL}/agent/task/${taskId}/stream`);
  
  // Handle progress updates
  eventSource.onmessage = (event) => {
    const progress = parseInt(event.data, 10);
    onProgress(progress);
  };
  
  // Handle connection errors
  eventSource.onerror = (error) => {
    console.error('Error streaming task status:', error);
    eventSource.close();
  };
  
  return eventSource;
}

/**
 * List all available tools.
 * @returns {Promise<Object>} The tools list
 */
export async function listTools() {
  try {
    const response = await api.get('/tools');
    return response.data;
  } catch (error) {
    console.error('Error listing tools:', error);
    throw error;
  }
}

/**
 * Get system status.
 * @returns {Promise<Object>} The system status
 */
export async function getSystemStatus() {
  try {
    const response = await api.get('/system/status');
    return response.data;
  } catch (error) {
    console.error('Error getting system status:', error);
    throw error;
  }
}