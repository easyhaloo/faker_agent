import React, { useState, useEffect, useRef } from 'react';
import { Bot, Terminal, ArrowRight, Check, AlertTriangle } from 'lucide-react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { useAgentStore } from '../store/agentStore';
import { cn } from '../utils/cn';

/**
 * 流式响应组件
 * 用于显示实时流式响应和工具调用
 */
const StreamingResponse = ({ taskId }) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const responseRef = useRef(null);
  
  const task = useAgentStore((state) => state.tasks[taskId]);
  const isLoading = useAgentStore((state) => state.isLoading);
  
  // 自动滚动到底部
  useEffect(() => {
    if (responseRef.current && isExpanded) {
      responseRef.current.scrollTop = responseRef.current.scrollHeight;
    }
  }, [task, isExpanded]);

  // 如果没有任务ID或任务不存在，显示占位符
  if (!taskId || !task) {
    return null;
  }

  const toolCalls = task.toolCalls || [];
  
  // 切换展开/收起状态
  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  // 渲染工具调用信息
  const renderToolCall = (toolCall) => {
    const isCompleted = Boolean(toolCall.completed);
    
    return (
      <div key={toolCall.id} className="mb-3 border border-gray-200 dark:border-gray-700 rounded-md overflow-hidden">
        {/* 工具调用头部 */}
        <div className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 px-3 py-2 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <Terminal size={14} className="mr-2 text-gray-600" />
            <span className="font-medium text-sm">{toolCall.toolCall.name}</span>
          </div>
          <Badge 
            variant={isCompleted ? "secondary" : "outline"}
            className="text-xs"
          >
            {isCompleted ? (
              <span className="flex items-center">
                <Check size={10} className="mr-1" /> 已完成
              </span>
            ) : (
              <span className="flex items-center">
                <span className="w-2 h-2 rounded-full bg-blue-400 animate-pulse mr-1"></span> 执行中
              </span>
            )}
          </Badge>
        </div>
        
        {/* 工具调用参数 */}
        <div className="px-3 py-2 bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
          <div className="text-xs text-gray-500 mb-1">参数:</div>
          <pre className="text-xs bg-gray-100 dark:bg-gray-700 p-2 rounded overflow-x-auto text-gray-800 dark:text-gray-200">
            {JSON.stringify(toolCall.toolCall.arguments, null, 2)}
          </pre>
        </div>
        
        {/* 工具调用结果 */}
        {isCompleted && (
          <div className="px-3 py-2">
            <div className="text-xs text-gray-500 mb-1">结果:</div>
            <pre className="text-xs bg-gray-100 dark:bg-gray-700 p-2 rounded overflow-x-auto max-h-32 text-gray-800 dark:text-gray-200">
              {typeof toolCall.result === 'object' 
                ? JSON.stringify(toolCall.result, null, 2)
                : toolCall.result}
            </pre>
          </div>
        )}
      </div>
    );
  };

  return (
    <Card className="mb-4 overflow-hidden">
      {/* 头部信息 */}
      <div className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 px-4 py-2 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center">
          <Bot size={16} className="mr-2 text-gray-600" />
          <span className="font-medium">{isLoading ? "任务处理中" : (task.response ? "任务已完成" : "任务处理失败")}</span>
          {isLoading && (
            <div className="ml-2 flex space-x-1">
              <div className="w-2 h-2 rounded-full bg-blue-400 animate-bounce"></div>
              <div className="w-2 h-2 rounded-full bg-blue-400 animate-bounce delay-75"></div>
              <div className="w-2 h-2 rounded-full bg-blue-400 animate-bounce delay-150"></div>
            </div>
          )}
        </div>
        <div className="flex items-center">
          <Badge variant="outline" className="mr-2 text-xs">
            ID: {taskId.substring(0, 8)}
          </Badge>
          <button 
            onClick={toggleExpanded}
            className="text-gray-500 hover:text-gray-700"
          >
            {isExpanded ? '收起' : '展开'}
          </button>
        </div>
      </div>
      
      {/* 工具调用和响应内容 */}
      {isExpanded && (
        <div 
          className="p-4 max-h-96 overflow-y-auto"
          ref={responseRef}
        >
          {toolCalls.length > 0 ? (
            <div>
              <div className="text-sm font-medium mb-2">执行步骤:</div>
              {toolCalls.map(renderToolCall)}
            </div>
          ) : (
            <div className="text-gray-500 text-sm italic flex items-center justify-center py-4">
              <AlertTriangle size={16} className="mr-2" />
              暂无执行步骤
            </div>
          )}
          
          {/* 显示响应或错误消息 */}
          {task.response && (
            <div className="mt-3">
              <div className="text-sm font-medium mb-2">最终响应:</div>
              <div className="whitespace-pre-wrap text-sm bg-gray-50 dark:bg-gray-800 p-3 rounded-md border border-gray-200 dark:border-gray-700 text-gray-800 dark:text-gray-200">
                {task.response}
              </div>
            </div>
          )}
          
          {/* 错误消息 - 当没有响应但任务已完成时显示 */}
          {!task.response && !isLoading && (
            <div className="mt-3">
              <div className="text-sm font-medium mb-2 text-orange-500">系统提示:</div>
              <div className="whitespace-pre-wrap text-sm bg-orange-50 dark:bg-orange-900/20 p-3 rounded-md border border-orange-200 dark:border-orange-800/30 text-orange-700 dark:text-orange-300">
                AI暂时无法回答您的问题，请稍后重试。
              </div>
            </div>
          )}
        </div>
      )}
    </Card>
  );
};

export default StreamingResponse;