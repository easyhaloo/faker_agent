/**
 * 响应适配器测试
 * 
 * 这个文件提供了测试响应适配器的工具函数，用于验证适配器是否能正确处理各种响应格式。
 * 执行方法：在浏览器控制台中引入此模块并调用testAdapter函数。
 */

import { 
  adaptAgentResponse, 
  extractTextResponse, 
  isEmptyResponse, 
  isErrorResponse, 
  createLoadingResponse,
  DEFAULT_FALLBACK_MESSAGES 
} from './responseAdapter';

/**
 * 测试响应适配器
 * 打印测试结果到控制台
 */
export function testAdapter() {
  console.group('响应适配器测试');
  
  // 测试案例1：null响应
  const nullResponse = null;
  const adaptedNull = adaptAgentResponse(nullResponse);
  console.log('1. Null响应:');
  console.log('原始数据:', nullResponse);
  console.log('适配结果:', adaptedNull);
  console.log('是否为空响应:', isEmptyResponse(adaptedNull));
  console.log('是否为错误响应:', isErrorResponse(adaptedNull));
  console.log('提取文本:', extractTextResponse(adaptedNull));
  console.log('-----------------------');
  
  // 测试案例2：空对象响应
  const emptyResponse = {};
  const adaptedEmpty = adaptAgentResponse(emptyResponse);
  console.log('2. 空对象响应:');
  console.log('原始数据:', emptyResponse);
  console.log('适配结果:', adaptedEmpty);
  console.log('是否为空响应:', isEmptyResponse(adaptedEmpty));
  console.log('是否为错误响应:', isErrorResponse(adaptedEmpty));
  console.log('提取文本:', extractTextResponse(adaptedEmpty));
  console.log('-----------------------');
  
  // 测试案例3：标准成功响应
  const successResponse = {
    status: 'success',
    data: {
      response: '这是一个成功的响应',
      tool_calls: [],
      execution_time: 0.5
    },
    error: null
  };
  const adaptedSuccess = adaptAgentResponse(successResponse);
  console.log('3. 标准成功响应:');
  console.log('原始数据:', successResponse);
  console.log('适配结果:', adaptedSuccess);
  console.log('是否为空响应:', isEmptyResponse(adaptedSuccess));
  console.log('是否为错误响应:', isErrorResponse(adaptedSuccess));
  console.log('提取文本:', extractTextResponse(adaptedSuccess));
  console.log('-----------------------');
  
  // 测试案例4：标准错误响应
  const errorResponse = {
    status: 'error',
    data: null,
    error: {
      code: 'ERROR_CODE',
      message: '发生了一个错误'
    }
  };
  const adaptedError = adaptAgentResponse(errorResponse);
  console.log('4. 标准错误响应:');
  console.log('原始数据:', errorResponse);
  console.log('适配结果:', adaptedError);
  console.log('是否为空响应:', isEmptyResponse(adaptedError));
  console.log('是否为错误响应:', isErrorResponse(adaptedError));
  console.log('提取文本:', extractTextResponse(adaptedError));
  console.log('-----------------------');
  
  // 测试案例5：成功但没有内容的响应
  const emptySuccessResponse = {
    status: 'success',
    data: {
      response: '',
      tool_calls: [],
      execution_time: 0
    },
    error: null
  };
  const adaptedEmptySuccess = adaptAgentResponse(emptySuccessResponse);
  console.log('5. 成功但没有内容的响应:');
  console.log('原始数据:', emptySuccessResponse);
  console.log('适配结果:', adaptedEmptySuccess);
  console.log('是否为空响应:', isEmptyResponse(adaptedEmptySuccess));
  console.log('是否为错误响应:', isErrorResponse(adaptedEmptySuccess));
  console.log('提取文本:', extractTextResponse(adaptedEmptySuccess));
  console.log('-----------------------');
  
  // 测试案例6：没有状态字段的响应（后向兼容）
  const legacyResponse = {
    response: '这是旧格式的响应',
    tool_calls: [],
    execution_time: 0.3
  };
  const adaptedLegacy = adaptAgentResponse(legacyResponse);
  console.log('6. 没有状态字段的响应:');
  console.log('原始数据:', legacyResponse);
  console.log('适配结果:', adaptedLegacy);
  console.log('是否为空响应:', isEmptyResponse(adaptedLegacy));
  console.log('是否为错误响应:', isErrorResponse(adaptedLegacy));
  console.log('提取文本:', extractTextResponse(adaptedLegacy));
  console.log('-----------------------');
  
  // 测试案例7：字符串响应
  const stringResponse = '这是一个字符串响应';
  const adaptedString = adaptAgentResponse(stringResponse);
  console.log('7. 字符串响应:');
  console.log('原始数据:', stringResponse);
  console.log('适配结果:', adaptedString);
  console.log('是否为空响应:', isEmptyResponse(adaptedString));
  console.log('是否为错误响应:', isErrorResponse(adaptedString));
  console.log('提取文本:', extractTextResponse(adaptedString));
  console.log('-----------------------');
  
  // 测试案例8：空字符串响应
  const emptyStringResponse = '';
  const adaptedEmptyString = adaptAgentResponse(emptyStringResponse);
  console.log('8. 空字符串响应:');
  console.log('原始数据:', emptyStringResponse);
  console.log('适配结果:', adaptedEmptyString);
  console.log('是否为空响应:', isEmptyResponse(adaptedEmptyString));
  console.log('是否为错误响应:', isErrorResponse(adaptedEmptyString));
  console.log('提取文本:', extractTextResponse(adaptedEmptyString));
  console.log('-----------------------');
  
  // 测试案例9：带有自定义兜底消息的适配
  const customFallbacks = {
    empty: '没有找到相关内容',
    error: '出错了，请稍后再试'
  };
  const customAdapted = adaptAgentResponse(null, { fallbackMessages: customFallbacks });
  console.log('9. 自定义兜底消息:');
  console.log('原始数据: null');
  console.log('适配结果:', customAdapted);
  console.log('提取文本:', extractTextResponse(customAdapted, { fallbackMessages: customFallbacks }));
  console.log('-----------------------');
  
  // 测试案例10：加载状态响应
  const loadingResponse = createLoadingResponse();
  console.log('10. 加载状态响应:');
  console.log('适配结果:', loadingResponse);
  console.log('是否为空响应:', isEmptyResponse(loadingResponse));
  console.log('是否为错误响应:', isErrorResponse(loadingResponse));
  console.log('提取文本:', extractTextResponse(loadingResponse));
  console.log('-----------------------');
  
  console.groupEnd();
  
  return '测试完成，请查看控制台输出';
}

// 默认导出测试函数
export default testAdapter;