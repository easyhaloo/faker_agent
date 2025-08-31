/**
 * API Response Adapter
 * 
 * This module provides adapters for different API response formats
 * to ensure consistent handling in the frontend regardless of backend changes.
 */

// Default fallback messages
export const DEFAULT_FALLBACK_MESSAGES = {
  empty: "AI暂时无法回答您的问题，请稍后重试。",
  error: "处理您的请求时出现了问题，请检查您的输入并重试。",
  timeout: "请求超时，请检查网络连接并重试。",
  loading: "正在思考中...",
  invalid: "收到无效的响应格式，请联系管理员。"
};

/**
 * Adapts agent response data to a consistent format
 * 
 * @param {Object} response - The raw API response
 * @param {Object} options - Adaptation options
 * @param {Object} options.fallbackMessages - Custom fallback messages
 * @returns {Object} - Normalized response data
 */
export const adaptAgentResponse = (response, options = {}) => {
  // Merge default fallback messages with custom ones
  const fallbackMessages = {
    ...DEFAULT_FALLBACK_MESSAGES,
    ...(options.fallbackMessages || {})
  };

  // Handle null/undefined/empty response
  if (!response) {
    return {
      status: 'error',
      data: { 
        response: fallbackMessages.empty,
        tools: [] // Ensure tools array is always present
      },
      error: { message: 'Empty response received' }
    };
  }

  // Handle case where response has proper structure
  if (response.status === 'success' || response.status === 'error') {
    // For success responses with empty data
    if (response.status === 'success' && 
        (!response.data || 
         (response.data.response === '' && 
          (!response.data.tool_calls || response.data.tool_calls.length === 0)))) {
      return {
        status: 'success',
        data: { 
          response: fallbackMessages.empty,
          tool_calls: response.data?.tool_calls || [],
          execution_time: response.data?.execution_time || 0
        },
        error: null
      };
    }
    
    // For error responses with no error message
    if (response.status === 'error' && (!response.error || !response.error.message)) {
      return {
        status: 'error',
        data: response.data || { response: '' },
        error: { 
          message: fallbackMessages.error,
          ...response.error
        }
      };
    }
    
    // Structure is already correct, ensure data and error fields exist
    // Also ensure tools array is always present in data
    let data = response.data || { response: '' };
    
    // For tools endpoint responses, ensure tools field is present
    if (data.tools === undefined && !data.tool_calls) {
      // Don't override tools field if it already exists
      data = { ...data, tools: [] };
    }
    
    return {
      status: response.status,
      data: data,
      error: response.error || null
    };
  }

  // Handle case where response itself is the data (no status wrapper)
  // This is a backward compatibility case
  if (typeof response === 'object' && !('status' in response)) {
    // Check if response is empty or has empty fields
    if (!response.response && 
        (!response.tool_calls || response.tool_calls.length === 0)) {
      return {
        status: 'success',
        data: {
          response: fallbackMessages.empty,
          tool_calls: [],
          execution_time: response.execution_time || 0
        },
        error: null
      };
    }

    return {
      status: 'success',
      data: {
        response: response.response || '',
        tool_calls: response.tool_calls || [],
        execution_time: response.execution_time || 0
      },
      error: null
    };
  }

  // Handle string response (direct text response)
  if (typeof response === 'string') {
    // Check if string is empty
    if (!response.trim()) {
      return {
        status: 'success',
        data: {
          response: fallbackMessages.empty,
          tool_calls: [],
          execution_time: 0
        },
        error: null
      };
    }

    return {
      status: 'success',
      data: {
        response: response,
        tool_calls: [],
        execution_time: 0
      },
      error: null
    };
  }

  // Default fallback - treat as error
  return {
    status: 'error',
    data: { response: fallbackMessages.invalid },
    error: {
      message: 'Invalid response format',
      details: response
    }
  };
};

/**
 * Extract the text response from an adapted response object
 * 
 * @param {Object} adaptedResponse - The adapted response 
 * @param {Object} options - Extraction options
 * @param {Object} options.fallbackMessages - Custom fallback messages
 * @returns {string} - The text response or error message
 */
export const extractTextResponse = (adaptedResponse, options = {}) => {
  const fallbackMessages = {
    ...DEFAULT_FALLBACK_MESSAGES,
    ...(options.fallbackMessages || {})
  };

  if (!adaptedResponse) {
    return fallbackMessages.empty;
  }

  if (adaptedResponse.status === 'success') {
    // Return the response if it exists and isn't empty
    return adaptedResponse.data?.response || fallbackMessages.empty;
  } else {
    // Return error message
    return `Error: ${adaptedResponse.error?.message || fallbackMessages.error}`;
  }
};

/**
 * Extract tool calls from an adapted response object
 * 
 * @param {Object} adaptedResponse - The adapted response
 * @returns {Array} - Array of tool calls or empty array
 */
export const extractToolCalls = (adaptedResponse) => {
  if (adaptedResponse?.status === 'success' && 
      adaptedResponse.data?.tool_calls) {
    return adaptedResponse.data.tool_calls;
  }
  return [];
};

/**
 * Check if response indicates an error
 * 
 * @param {Object} adaptedResponse - The adapted response
 * @returns {boolean} - True if response indicates error
 */
export const isErrorResponse = (adaptedResponse) => {
  return adaptedResponse?.status === 'error';
};

/**
 * Check if response is empty (no text response and no tool calls)
 * 
 * @param {Object} adaptedResponse - The adapted response
 * @returns {boolean} - True if response is empty
 */
export const isEmptyResponse = (adaptedResponse) => {
  if (!adaptedResponse || !adaptedResponse.data) {
    return true;
  }
  
  const hasResponse = adaptedResponse.data.response && 
                      adaptedResponse.data.response.trim() !== '';
  const hasToolCalls = adaptedResponse.data.tool_calls && 
                      adaptedResponse.data.tool_calls.length > 0;
                      
  return !hasResponse && !hasToolCalls;
};

/**
 * Create a loading state response object
 * 
 * @param {Object} options - Options for the loading state
 * @param {string} options.message - Custom loading message
 * @returns {Object} - Loading state response object
 */
export const createLoadingResponse = (options = {}) => {
  const message = options.message || DEFAULT_FALLBACK_MESSAGES.loading;
  
  return {
    status: 'loading',
    data: {
      response: message,
      tool_calls: [],
      execution_time: 0
    },
    error: null
  };
};

export default {
  adaptAgentResponse,
  extractTextResponse,
  extractToolCalls,
  isErrorResponse,
  isEmptyResponse,
  createLoadingResponse,
  DEFAULT_FALLBACK_MESSAGES
};