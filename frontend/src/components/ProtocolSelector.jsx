import React from 'react';
import { Button } from './ui/button';
import { useAgentStore } from '../store/agentStore';
import { ProtocolType, ModeType } from '../services/agentService';
import { cn } from '../utils/cn';

/**
 * 协议选择器组件
 * 允许用户选择与智能体通信的协议和模式
 */
const ProtocolSelector = () => {
  const protocol = useAgentStore((state) => state.protocol);
  const mode = useAgentStore((state) => state.mode);
  const setProtocol = useAgentStore((state) => state.setProtocol);
  const setMode = useAgentStore((state) => state.setMode);
  const isLoading = useAgentStore((state) => state.isLoading);

  // 协议选项
  const protocolOptions = [
    { value: ProtocolType.HTTP, label: 'HTTP', description: '标准HTTP请求' },
    { value: ProtocolType.SSE, label: 'SSE', description: '服务器发送事件' },
    { value: ProtocolType.WEBSOCKET, label: 'WebSocket', description: '双向通信' },
  ];

  // 模式选项
  const modeOptions = [
    { value: ModeType.SYNC, label: '同步', description: '等待完整响应' },
    { value: ModeType.STREAM, label: '流式', description: '实时响应流' },
  ];

  /**
   * 处理协议变更
   * @param {string} newProtocol - 新协议类型
   */
  const handleProtocolChange = (newProtocol) => {
    setProtocol(newProtocol);
    
    // 当选择HTTP协议时，自动设置为同步模式
    if (newProtocol === ProtocolType.HTTP) {
      setMode(ModeType.SYNC);
    } 
    // 当选择SSE或WebSocket协议时，自动设置为流式模式
    else if (newProtocol === ProtocolType.SSE || newProtocol === ProtocolType.WEBSOCKET) {
      setMode(ModeType.STREAM);
    }
  };

  /**
   * 处理模式变更
   * @param {string} newMode - 新模式类型
   */
  const handleModeChange = (newMode) => {
    setMode(newMode);
    
    // 当选择同步模式时，只能使用HTTP协议
    if (newMode === ModeType.SYNC) {
      setProtocol(ProtocolType.HTTP);
    }
  };

  return (
    <div className="space-y-3">
      <div className="space-y-3">
        {/* 协议选择 */}
        <div>
          <label className="text-sm text-gray-700 dark:text-gray-300 mb-1.5 block">通信协议:</label>
          <div className="flex flex-wrap gap-2">
            {protocolOptions.map((option) => (
              <Button
                key={option.value}
                onClick={() => handleProtocolChange(option.value)}
                variant={protocol === option.value ? "default" : "outline"}
                size="sm"
                className={cn(
                  "text-xs px-3 py-1 h-7",
                  protocol === option.value 
                    ? "bg-blue-500 hover:bg-blue-600" 
                    : "bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600"
                )}
                disabled={isLoading}
                title={option.description}
              >
                {option.label}
              </Button>
            ))}
          </div>
        </div>
        
        {/* 模式选择 */}
        <div>
          <label className="text-sm text-gray-700 dark:text-gray-300 mb-1.5 block">响应模式:</label>
          <div className="flex flex-wrap gap-2">
            {modeOptions.map((option) => (
              <Button
                key={option.value}
                onClick={() => handleModeChange(option.value)}
                variant={mode === option.value ? "default" : "outline"}
                size="sm"
                className={cn(
                  "text-xs px-3 py-1 h-7",
                  mode === option.value 
                    ? "bg-blue-500 hover:bg-blue-600" 
                    : "bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600"
                )}
                disabled={
                  isLoading || 
                  // 如果是同步模式，禁用除HTTP以外的协议
                  (option.value === ModeType.SYNC && protocol !== ProtocolType.HTTP) ||
                  // 如果是流式模式，禁用HTTP协议
                  (option.value === ModeType.STREAM && protocol === ProtocolType.HTTP)
                }
                title={option.description}
              >
                {option.label}
              </Button>
            ))}
          </div>
        </div>
      </div>
      
      <div className="text-xs text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-800 rounded-md p-2 mt-2">
        {protocol === ProtocolType.HTTP && mode === ModeType.SYNC && (
          <div className="flex items-center gap-1.5">
            <span className="inline-block w-2 h-2 rounded-full bg-green-500"></span>
            HTTP同步模式: 发送请求后等待完整响应
          </div>
        )}
        {protocol === ProtocolType.SSE && mode === ModeType.STREAM && (
          <div className="flex items-center gap-1.5">
            <span className="inline-block w-2 h-2 rounded-full bg-blue-500"></span>
            SSE流式模式: 服务器持续发送事件流，支持工具调用可视化
          </div>
        )}
        {protocol === ProtocolType.WEBSOCKET && mode === ModeType.STREAM && (
          <div className="flex items-center gap-1.5">
            <span className="inline-block w-2 h-2 rounded-full bg-purple-500"></span>
            WebSocket流式模式: 双向实时通信，支持工具调用可视化
          </div>
        )}
      </div>
    </div>
  );
};

export default ProtocolSelector;