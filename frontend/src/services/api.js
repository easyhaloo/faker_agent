import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const agentService = {
  /**
   * Send a task to the agent
   * @param {string} query - The task query
   * @param {object} context - Optional context information
   * @returns {Promise} Promise with the response
   */
  sendTask: async (query, context = {}) => {
    const response = await apiClient.post('/agent/task', {
      query,
      context,
      stream: false,
    });
    return response.data;
  },

  /**
   * Get task status
   * @param {string} taskId - The task ID
   * @returns {Promise} Promise with the task status
   */
  getTaskStatus: async (taskId) => {
    const response = await apiClient.get(`/agent/task/${taskId}`);
    return response.data;
  },
};

export const weatherService = {
  /**
   * Get weather for a city
   * @param {string} city - The city name
   * @returns {Promise} Promise with the weather data
   */
  getWeather: async (city) => {
    const response = await apiClient.get(`/weather/${city}`);
    return response.data;
  },
};

export const systemService = {
  /**
   * Get system status
   * @returns {Promise} Promise with the system status
   */
  getStatus: async () => {
    const response = await apiClient.get('/system/status');
    return response.data;
  },
};

export default {
  agent: agentService,
  weather: weatherService,
  system: systemService,
};