/**
 * Test script for response adapter
 * 
 * This script simulates different API response formats
 * and shows how the adapter normalizes them.
 */
import { adaptAgentResponse, extractTextResponse, extractToolCalls, isErrorResponse } from '../services/responseAdapter';

/**
 * Run tests for the response adapter
 */
export function testResponseAdapter() {
  console.group('Response Adapter Tests');
  
  // Test Case 1: Standard success response
  testCase(
    'Standard success response', 
    {
      status: 'success',
      data: {
        response: 'Hello, how can I help you?',
        tool_calls: [],
        execution_time: 0.5
      },
      error: null
    }
  );
  
  // Test Case 2: Success response with tool calls
  testCase(
    'Success response with tool calls',
    {
      status: 'success',
      data: {
        response: 'The weather in New York is sunny',
        tool_calls: [
          {
            tool_name: 'weather',
            tool_args: { city: 'New York' },
            tool_call_id: '123',
            status: 'completed',
            result: { temp: 72, condition: 'sunny' }
          }
        ],
        execution_time: 1.2
      }
    }
  );
  
  // Test Case 3: Error response
  testCase(
    'Error response',
    {
      status: 'error',
      error: {
        code: 'PROCESSING_ERROR',
        message: 'Failed to process request'
      }
    }
  );
  
  // Test Case 4: Raw object response (no status)
  testCase(
    'Raw object response (no status)',
    {
      response: 'This is a direct response',
      tool_calls: [],
      execution_time: 0.3
    }
  );
  
  // Test Case 5: Simple string response
  testCase(
    'Simple string response',
    'This is a simple text response'
  );
  
  // Test Case 6: Empty response
  testCase(
    'Empty response',
    null
  );

  // Test Case 7: Partial response with only text
  testCase(
    'Partial response with only text',
    {
      data: {
        response: 'Partial response'
      }
    }
  );
  
  // Test Case 8: Empty success response
  testCase(
    'Empty success response',
    {
      status: 'success',
      data: {}
    }
  );
  
  console.groupEnd();
  
  return 'Response adapter tests completed successfully';
}

/**
 * Run a single test case
 * 
 * @param {string} name - Test case name
 * @param {any} input - The input to adapt
 */
function testCase(name, input) {
  console.group(`Test: ${name}`);
  
  try {
    console.log('Input:', input);
    
    // Adapt the response
    const adapted = adaptAgentResponse(input);
    console.log('Adapted:', adapted);
    
    // Extract text
    const text = extractTextResponse(adapted);
    console.log('Extracted text:', text);
    
    // Extract tool calls
    const toolCalls = extractToolCalls(adapted);
    console.log('Extracted tool calls:', toolCalls);
    
    // Check if error
    const isError = isErrorResponse(adapted);
    console.log('Is error?', isError);
    
  } catch (error) {
    console.error('Test failed:', error);
  }
  
  console.groupEnd();
}

// Export a function to run the tests
export default testResponseAdapter;