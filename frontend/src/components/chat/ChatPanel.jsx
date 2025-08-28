import { useState, useRef, useEffect } from 'react';
import { useAgentStore } from '../../store/agentStore';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Card, CardContent } from '../ui/card';
import { Badge } from '../ui/badge';
import { Send, Bot, User } from 'lucide-react';

const ChatPanel = () => {
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null);
  
  const messages = useAgentStore((state) => state.messages);
  const isLoading = useAgentStore((state) => state.isLoading);
  const error = useAgentStore((state) => state.error);
  const sendMessageToAgent = useAgentStore((state) => state.sendMessageToAgent);
  
  // 滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;
    
    sendMessageToAgent(inputValue.trim());
    setInputValue('');
  };
  
  return (
    <div className="flex flex-col h-[calc(100vh-200px)]">
      {/* 消息区域 */}
      <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <div className="text-center mb-6">
              <div className="bg-gray-100 p-4 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <Bot className="h-8 w-8 text-gray-400" />
              </div>
              <h3 className="text-xl font-semibold mb-2 text-gray-700">Welcome to Faker Agent</h3>
              <p className="text-gray-500 max-w-md">Start a conversation by sending a message. I can help you with various tasks and answer your questions.</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full max-w-lg">
              <Card className="p-3 cursor-pointer hover:bg-gray-50 transition-colors">
                <h4 className="font-medium text-gray-800">天气查询</h4>
                <p className="text-sm text-gray-500 mt-1">"今天北京的天气怎么样？"</p>
              </Card>
              <Card className="p-3 cursor-pointer hover:bg-gray-50 transition-colors">
                <h4 className="font-medium text-gray-800">任务规划</h4>
                <p className="text-sm text-gray-500 mt-1">"帮我制定一周学习计划"</p>
              </Card>
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <div 
              key={message.id} 
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div 
                className={`max-w-[85%] rounded-2xl p-4 ${
                  message.role === 'user' 
                    ? 'bg-blue-500 text-white rounded-tr-none' 
                    : 'bg-gray-100 text-gray-800 rounded-tl-none'
                }`}
              >
                <div className="flex items-start gap-2">
                  <div className={`mt-0.5 ${message.role === 'user' ? 'text-white' : 'text-gray-500'}`}>
                    {message.role === 'user' ? <User size={16} /> : <Bot size={16} />}
                  </div>
                  <div className="flex-1">
                    <div className="whitespace-pre-wrap break-words">
                      {message.content}
                    </div>
                    {message.taskId && message.role === 'assistant' && (
                      <div className="mt-2">
                        <Badge variant="secondary" className="text-xs">
                          Task ID: {message.taskId}
                        </Badge>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-800 rounded-2xl rounded-tl-none p-4">
              <div className="flex space-x-2">
                <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce"></div>
                <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce delay-75"></div>
                <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce delay-150"></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </CardContent>
      
      {/* 输入区域 */}
      <div className="p-4 border-t border-gray-200">
        {error && (
          <div className="mb-3 p-3 bg-red-50 text-red-700 rounded-lg text-sm border border-red-200">
            <div className="font-medium">Error</div>
            <div>{error}</div>
          </div>
        )}
        <form onSubmit={handleSubmit} className="flex gap-2">
          <div className="flex-1 relative">
            <Input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Type your message here..."
              className="pr-12 py-5"
              disabled={isLoading}
            />
            <Button
              type="submit"
              size="icon"
              className="absolute right-2 top-1/2 transform -translate-y-1/2 h-8 w-8 rounded-full"
              disabled={!inputValue.trim() || isLoading}
            >
              <Send size={16} />
              <span className="sr-only">Send</span>
            </Button>
          </div>
        </form>
        <div className="mt-2 text-xs text-gray-500 text-center">
          Press Enter to send, Shift+Enter for new line
        </div>
      </div>
    </div>
  );
};

export default ChatPanel;