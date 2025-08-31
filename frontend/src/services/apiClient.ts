import axios from 'axios';
import { adaptAgentResponse, isEmptyResponse, DEFAULT_FALLBACK_MESSAGES } from './responseAdapter';

const API_BASE_URL = 'http://localhost:8000/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Global response transformation and error handling
apiClient.interceptors.response.use(
  response => {
    // For agent endpoints, apply response adaptation
    const url = response.config.url || '';
    if (url.includes('/agent/v1/respond')) {
      response.data = adaptAgentResponse(response.data);
      
      // Handle empty responses with fallback
      if (isEmptyResponse(response.data)) {
        response.data = adaptAgentResponse({
          status: 'success',
          data: { 
            response: DEFAULT_FALLBACK_MESSAGES.empty,
            tool_calls: [],
            execution_time: 0
          }
        });
      }
    }
    return response;
  },
  error => {
    console.error('API Error:', error);
    
    // If the error has a response, adapt it for agent endpoints
    if (error.response && error.config && error.config.url) {
      const url = error.config.url || '';
      if (url.includes('/agent/v1/respond')) {
        error.response.data = adaptAgentResponse(error.response.data);
        
        // If response is empty, provide a fallback error message
        if (isEmptyResponse(error.response.data)) {
          error.response.data = adaptAgentResponse({
            status: 'error',
            error: {
              code: error.response.status,
              message: DEFAULT_FALLBACK_MESSAGES.error
            }
          });
        }
      }
    } else if (!error.response) {
      // Network errors or timeout
      const errorMessage = error.code === 'ECONNABORTED' 
        ? DEFAULT_FALLBACK_MESSAGES.timeout
        : DEFAULT_FALLBACK_MESSAGES.error;
        
      error.response = {
        data: adaptAgentResponse({
          status: 'error',
          error: {
            code: 'NETWORK_ERROR',
            message: errorMessage
          }
        })
      };
    }
    
    return Promise.reject(error);
  }
);