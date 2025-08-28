import React from 'react';
import { Button } from './ui/button';
import { useAgentStore } from '../store/agentStore';
import { ProtocolType, ModeType } from '../services/agentService';

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
    <div className="mb-4 space-y-3">
      <div className="space-y-2">
        <div className="flex items-center">
          <label className="text-sm font-medium text-gray-700 mr-2">协议:</label>
          <div className="flex space-x-2">
            {protocolOptions.map((option) => (
              <Button
                key={option.value}
                onClick={() => handleProtocolChange(option.value)}
                variant={protocol === option.value ? "default" : "outline"}
                size="sm"
                disabled={isLoading}
                title={option.description}
              >
                {option.label}
              </Button>
            ))}
          </div>
        </div>
        
        <div className="flex items-center">
          <label className="text-sm font-medium text-gray-700 mr-2">模式:</label>
          <div className="flex space-x-2">
            {modeOptions.map((option) => (
              <Button
                key={option.value}
                onClick={() => handleModeChange(option.value)}
                variant={mode === option.value ? "default" : "outline"}
                size="sm"
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
      
      <div className="text-xs text-gray-500 italic">
        {protocol === ProtocolType.HTTP && mode === ModeType.SYNC && (
          "HTTP同步模式: 发送请求后等待完整响应"
        )}
        {protocol === ProtocolType.SSE && mode === ModeType.STREAM && (
          "SSE流式模式: 服务器持续发送事件流，支持工具调用可视化"
        )}
        {protocol === ProtocolType.WEBSOCKET && mode === ModeType.STREAM && (
          "WebSocket流式模式: 双向实时通信，支持工具调用可视化"
        )}
      </div>
    </div>
  );
};

export default ProtocolSelector;