import React, { useState, useEffect, useRef } from 'react';
import { Bot, Terminal, ArrowRight, Check, AlertTriangle } from 'lucide-react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { useAgentStore } from '../store/agentStore';

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
      <div key={toolCall.id} className="mb-3 border border-gray-200 rounded-md overflow-hidden">
        {/* 工具调用头部 */}
        <div className="flex items-center justify-between bg-gray-50 px-3 py-2 border-b border-gray-200">
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
        <div className="px-3 py-2 bg-gray-50 border-b border-gray-200">
          <div className="text-xs text-gray-500 mb-1">参数:</div>
          <pre className="text-xs bg-gray-100 p-2 rounded overflow-x-auto">
            {JSON.stringify(toolCall.toolCall.arguments, null, 2)}
          </pre>
        </div>
        
        {/* 工具调用结果 */}
        {isCompleted && (
          <div className="px-3 py-2">
            <div className="text-xs text-gray-500 mb-1">结果:</div>
            <pre className="text-xs bg-gray-100 p-2 rounded overflow-x-auto max-h-32">
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
      <div className="flex items-center justify-between bg-gray-50 px-4 py-2 border-b">
        <div className="flex items-center">
          <Bot size={16} className="mr-2 text-gray-600" />
          <span className="font-medium">任务处理中</span>
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
          
          {task.response && (
            <div className="mt-3">
              <div className="text-sm font-medium mb-2">最终响应:</div>
              <div className="whitespace-pre-wrap text-sm bg-gray-50 p-3 rounded-md border border-gray-200">
                {task.response}
              </div>
            </div>
          )}
        </div>
      )}
    </Card>
  );
};

export default StreamingResponse;