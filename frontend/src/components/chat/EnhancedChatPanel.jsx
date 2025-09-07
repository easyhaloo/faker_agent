import { useState, useRef, useEffect, useMemo } from 'react';
import { useAgentStore } from '../../store/agentStore';
import { useConversationStore } from '../../store/conversationStore';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '../ui/button';
import { Textarea } from '../ui/textarea';
import { Input } from '../ui/input';
import { Card, CardContent } from '../ui/card';
import { Badge } from '../ui/badge';
import { Send, Bot, User, ChevronDown, Paperclip, Square, CornerDownRight } from 'lucide-react';
import StreamingResponse from '../StreamingResponse';
import { cn } from '../../utils/cn';
import { useI18n } from '../../i18n/index.jsx';

const EnhancedChatPanel = ({ conversation, onSendMessage }) => {
  const { t, language } = useI18n();
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);
  
  // 优先使用外部传入的conversation，否则使用当前会话
  const { currentConversationId, conversations, sendMessage: sendConversationMessage } = useConversationStore();
  const currentConversation = conversation || conversations.find(c => c.id === currentConversationId);
  
  // 使用会话消息或代理消息作为后备
  const agentMessages = useAgentStore((state) => state.messages);
  const isLoading = useAgentStore((state) => state.isLoading);
  const error = useAgentStore((state) => state.error);
  const currentTaskId = useAgentStore((state) => state.currentTaskId);
  const protocol = useAgentStore((state) => state.protocol);
  const mode = useAgentStore((state) => state.mode);
  const sendMessageToAgent = useAgentStore((state) => state.sendMessageToAgent);
  
  // 强制重新加载会话消息 - 修复消息不显示的问题
  useEffect(() => {
    if (currentConversationId && currentConversation && !currentConversation.messages) {
      // 如果当前会话没有消息，尝试从store重新加载
      const { loadConversation } = useConversationStore.getState();
      loadConversation(currentConversationId);
    }
  }, [currentConversationId]);
  
  // 使用会话消息或代理消息作为后备
  const messages = currentConversation?.messages || agentMessages;
  
  // 消息记忆化 - 优化性能，避免不必要的重新渲染
  const memoizedMessages = useMemo(() => {
    if (!messages || !Array.isArray(messages)) return [];
    return messages.map((message, index) => ({
      ...message,
      _renderKey: `${message.id || index}-${message.role}-${message.content?.length || 0}`
    }));
  }, [messages, currentConversationId]); // 依赖currentConversationId确保会话切换时重新渲染
  
  // 滚动到底部
  const scrollToBottom = (behavior = 'smooth') => {
    if (messagesEndRef.current) {
      // 使用平滑滚动到底部
      messagesEndRef.current.scrollIntoView({ behavior, block: 'end' });
    }
  };
  
  // 测试监听滚动事件并检测是否需要自动滚动
  const [isUserScrolling, setIsUserScrolling] = useState(false);
  const [isScrollAtBottom, setIsScrollAtBottom] = useState(true);
  const scrollTimeout = useRef(null);
  const messagesContainerRef = useRef(null);
  
  // 检测是否滚动到底部
  const checkIfScrollAtBottom = () => {
    if (!messagesContainerRef.current) return true;
    
    const { scrollTop, scrollHeight, clientHeight } = messagesContainerRef.current;
    const isAtBottom = scrollHeight - scrollTop - clientHeight <= 2;
    setIsScrollAtBottom(isAtBottom);
    return isAtBottom;
  };
  
  // Auto-resize textarea based on content
  useEffect(() => {
    if (textareaRef.current) {
      // Store current height to prevent layout shake
      const currentHeight = textareaRef.current.style.height;
      // Temporarily set to auto to get accurate scrollHeight
      textareaRef.current.style.height = 'auto';
      const newHeight = Math.min(textareaRef.current.scrollHeight, 200);
      // Only update if height actually changes
      if (currentHeight !== `${newHeight}px`) {
        textareaRef.current.style.height = `${newHeight}px`;
      }
    }
  }, [inputValue]);
  
  // Handle input change
  const handleInputChange = (e) => {
    setInputValue(e.target.value);
    setIsTyping(e.target.value.length > 0);
  };
  
  // 监听滚动事件
  const handleScroll = () => {
    if (scrollTimeout.current) {
      clearTimeout(scrollTimeout.current);
    }
    
    setIsUserScrolling(true);
    checkIfScrollAtBottom();
    
    // 300ms 后设置用户不再滚动
    scrollTimeout.current = setTimeout(() => {
      setIsUserScrolling(false);
    }, 300);
  };
  
  // 添加滚动监听
  useEffect(() => {
    const container = messagesContainerRef.current;
    if (container) {
      container.addEventListener('scroll', handleScroll);
      
      return () => {
        container.removeEventListener('scroll', handleScroll);
      };
    }
  }, []);
  
  // 消息更新时自动滚动到底部
  useEffect(() => {
    // 如果用户没有手动滚动或者滚动到了底部，则自动滚动到底部
    if (!isUserScrolling || isScrollAtBottom) {
      // 等待DOM更新后再滚动
      const timeoutId = setTimeout(() => {
        scrollToBottom();
      }, 100);
      
      return () => clearTimeout(timeoutId);
    }
  }, [messages, isUserScrolling, isScrollAtBottom]);
  
  // 初始加载时强制滚动到底部
  useEffect(() => {
    scrollToBottom('auto');
    checkIfScrollAtBottom();
  }, []);

  
  // 确保助手消息渲染完成后停止加载状态
  useEffect(() => {
    const lastMessage = messages[messages.length - 1];
    if (messages.length > 0 && lastMessage?.role === 'assistant') {
      // 在下一个渲染周期确保加载状态关闭
      requestAnimationFrame(() => {
        if (isLoading) {
          useAgentStore.getState().setLoading(false);
        }
      });
    }
  }, [messages.length, isLoading]);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;
    
    // 支持外部传入的onSendMessage或内部处理
    if (onSendMessage) {
      await onSendMessage(inputValue.trim());
    } else {
      // 使用对话存储发送消息，它会正确处理新对话的创建
      await sendConversationMessage(inputValue.trim());
    }
    setInputValue('');
    setIsTyping(false);
  };
  
  // 空状态处理 - 修复：只有当确实没有消息时才显示空状态
  const hasMessages = messages && messages.length > 0;
  const showEmptyState = !hasMessages && !isLoading;

  return (
    <div className="flex flex-col h-full relative w-full bg-gradient-to-b from-white to-gray-50 dark:from-gray-800 dark:to-gray-900 max-w-4xl mx-auto">
      {/* 功能区域 - 已移除系统设置按钮 */}
      {/* <div className="flex justify-end px-4 py-2 bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700"> */}
        {/* 保留空白区域供布局占位 */}
      {/* </div> */}
      
      {/* 任务状态和工具调用信息 */}
      {currentTaskId && (
        <div className="px-4 py-2">
          <StreamingResponse taskId={currentTaskId} />
        </div>
      )}
      
      {/* 空状态处理 - 修复：只有当确实没有消息时才显示空状态 */}
      {showEmptyState ? (
        <div className="flex-1 flex flex-col items-center justify-center p-6 bg-white dark:bg-gray-800">
          <div className="max-w-md text-center">
            <div className="bg-gray-100 p-4 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4 dark:bg-gray-700">
              <Bot className="h-8 w-8 text-gray-400" />
            </div>
            <h3 className="text-xl font-semibold mb-2 text-gray-800 dark:text-gray-200">
              {currentConversation ? t('conversation.startYourConversation') : 'Welcome to Faker Agent'}
            </h3>
            <p className="text-gray-600 dark:text-gray-400 max-w-md mb-6">
              {currentConversation ? t('conversation.typeMessage') : 'Start a conversation by sending a message. I can help you with various tasks and answer your questions.'}
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full max-w-lg">
              <Card 
                className="p-3 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors border-gray-200 dark:border-gray-700" 
                onClick={() => {
                  setInputValue(t('promptCards.weatherPrompt'));
                  setTimeout(() => {
                    handleSubmit(new Event('submit'));
                  }, 100);
                }}
              >
                <h4 className="font-medium text-gray-800 dark:text-gray-200">{t('promptCards.weatherTitle')}</h4>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">"{t('promptCards.weatherPrompt')}"</p>
              </Card>
              <Card 
                className="p-3 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors border-gray-200 dark:border-gray-700"
                onClick={() => {
                  setInputValue(t('promptCards.planningPrompt'));
                  setTimeout(() => {
                    handleSubmit(new Event('submit'));
                  }, 100);
                }}
              >
                <h4 className="font-medium text-gray-800 dark:text-gray-200">{t('promptCards.planningTitle')}</h4>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">"{t('promptCards.planningPrompt')}"</p>
              </Card>
            </div>
          </div>
        </div>
      ) : (
        <CardContent className="flex-1 overflow-y-auto p-4 flex flex-col bg-white dark:bg-gray-800" ref={messagesContainerRef}>
          {/* 错误消息显示 */}
          {error && (
            <div className="mb-3 p-3 bg-red-50 text-red-700 rounded-lg text-sm border border-red-200 sticky top-0 z-10">
              <div className="font-medium">Error</div>
              <div>{error}</div>
            </div>
          )}
          <div className="flex-1 flex flex-col space-y-4">
            {memoizedMessages.map((message, index) => {
              // 检查是否与前一条消息是同一角色
              const isPreviousSameRole = index > 0 && messages[index - 1].role === message.role;
              // 检查是否与下一条消息是同一角色
              const isNextSameRole = index < messages.length - 1 && messages[index + 1].role === message.role;
              
              // 根据消息连续性设置不同的圆角和间距
              const messageContainerClass = cn(
                message.role === 'user' ? 'justify-end' : 'justify-start',
                isPreviousSameRole ? 'mt-1' : 'mt-4'
              );
              
              // 设置消息气泡的圆角样式
              const bubbleRadiusClass = message.role === 'user'
                ? isPreviousSameRole && isNextSameRole ? 'rounded-l-2xl rounded-r-md' 
                  : isPreviousSameRole ? 'rounded-l-2xl rounded-tr-md rounded-br-2xl' 
                  : isNextSameRole ? 'rounded-l-2xl rounded-tr-2xl rounded-br-md' 
                  : 'rounded-2xl rounded-tr-none'
                : isPreviousSameRole && isNextSameRole ? 'rounded-r-2xl rounded-l-md' 
                  : isPreviousSameRole ? 'rounded-r-2xl rounded-tl-md rounded-bl-2xl' 
                  : isNextSameRole ? 'rounded-r-2xl rounded-tl-2xl rounded-bl-md' 
                  : 'rounded-2xl rounded-tl-none';
              
              return (
                <div 
                  key={message.id} 
                  className={`flex ${messageContainerClass}`}
                >
                  {/* 只在序列中第一个助手消息上显示图标 */}
                  {message.role === 'assistant' && !isPreviousSameRole && (
                    <div className="flex items-center justify-center h-8 w-8 rounded-full bg-gray-200 dark:bg-gray-700 mr-2">
                      <Bot size={18} className="text-gray-600 dark:text-gray-300" />
                    </div>
                  )}
                  {message.role === 'assistant' && isPreviousSameRole && (
                    <div className="w-8 mr-2"></div>
                  )}
                  
                  <div 
                    className={cn(
                      "max-w-[70%] p-3",
                      bubbleRadiusClass,
                      message.role === 'user' 
                        ? "bg-blue-500 text-white" 
                        : "bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200"
                    )}
                  >
                    <div className="flex items-start">
                      {/* 只在序列中第一个用户消息上显示图标 */}
                      {message.role === 'user' && !isPreviousSameRole && (
                        <div className="text-white mr-2 mt-0.5">
                          <User size={16} />
                        </div>
                      )}
                      <div className="flex-1">
                        <div className="whitespace-pre-wrap break-words">
                          {message.content}
                        </div>
                        {message.taskId && message.role === 'assistant' && (
                          <div className="mt-2">
                            <Badge variant="secondary" className="text-xs">
                              Task ID: {message.taskId}
                            </Badge>
                            {protocol !== 'http' && (
                              <Badge variant="outline" className="ml-2 text-xs">
                                {protocol.toUpperCase()}
                              </Badge>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  {/* 只在序列中第一个用户消息上显示头像 */}
                  {message.role === 'user' && !isPreviousSameRole && (
                    <div className="flex items-center justify-center h-8 w-8 rounded-full bg-blue-200 dark:bg-blue-700 ml-2">
                      <User size={18} className="text-blue-600 dark:text-blue-200" />
                    </div>
                  )}
                  {message.role === 'user' && isPreviousSameRole && (
                    <div className="w-8 ml-2"></div>
                  )}
                </div>
              );
            })}
          </div>
          {messages.length > 0 && isLoading && (
            <div className="flex justify-start mt-1" data-testid="loading-indicator">
              <div className="flex items-center">
                <div className="flex items-center justify-center h-8 w-8 rounded-full bg-gray-200 dark:bg-gray-700 mr-2">
                  <Bot size={18} className="text-gray-600 dark:text-gray-300" />
                </div>
                <div className="bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-2xl rounded-tl-none p-3">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce"></div>
                    <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce delay-75"></div>
                    <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce delay-150"></div>
                  </div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} className="h-1" />
          
          {/* 滚动到底部按钮 - 当用户不在底部时显示 */}
          {!isScrollAtBottom && messages.length > 2 && (
            <Button
              size="sm"
              variant="secondary"
              className="fixed bottom-20 right-4 rounded-full shadow-md opacity-90 hover:opacity-100 z-10 transition-opacity duration-200"
              onClick={() => scrollToBottom()}
              aria-label="滚动到底部"
            >
              <ChevronDown size={16} className="mr-1" />
              <span className="text-xs">新消息</span>
            </Button>
          )}
        </CardContent>
      )}
      
      <div className={showEmptyState ? 'p-4' : 'px-4 pb-4 bg-transparent'}>
        {isLoading && (
          <div className="flex justify-end px-2 pb-2">
            <button className="h-8 px-3 text-sm text-red-500 hover:text-red-700 border border-red-200 hover:border-red-300 dark:border-red-800 dark:hover:border-red-700 rounded-full flex items-center gap-1 bg-white dark:bg-gray-800 shadow-sm">
              <Square size={14} />
              {t('common.stop')}
            </button>
          </div>
        )}
        <form onSubmit={handleSubmit} className="flex items-center gap-2">
          <button className="h-9 w-9 rounded-full flex items-center justify-center text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
            <Paperclip size={18} />
          </button>
          <div className="flex-1 relative min-h-[48px]">
            <Textarea
              ref={textareaRef}
              value={inputValue}
              onChange={handleInputChange}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
              placeholder={t('common.inputPlaceholder')}
              className="pr-12 resize-none overflow-hidden min-h-[48px] max-h-[200px] rounded-2xl border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 focus:border-blue-400 dark:focus:border-blue-500 focus:ring focus:ring-blue-200 dark:focus:ring-blue-900 focus:ring-opacity-50"
              disabled={isLoading}
              rows={1}
            />
            <Button
              type="submit"
              size="icon"
              className={`absolute right-3 bottom-2.5 h-8 w-8 rounded-full flex items-center justify-center ${
                !isTyping || isLoading 
                  ? 'bg-gray-300 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-not-allowed' 
                  : 'bg-blue-500 hover:bg-blue-600 text-white cursor-pointer shadow-sm'
              } transition-colors`}
              onClick={handleSubmit}
              disabled={!isTyping || isLoading}
            >
              <Send size={16} />
            </Button>
          </div>
        </form>
        <div className={`${showEmptyState ? 'mt-2' : 'mt-1'} text-xs text-gray-400 dark:text-gray-500 text-center flex items-center justify-center`}>
          <span className="mr-3">{t('common.sendShortcut')}</span>
          <div className="flex items-center">
            <Badge variant="outline" className="text-xs border-gray-300 dark:border-gray-600">
              {protocol.toUpperCase()}
            </Badge>
            <Badge variant="outline" className="ml-1 text-xs border-gray-300 dark:border-gray-600">
              {mode === 'sync' ? t('common.sync') : t('common.stream')}
            </Badge>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedChatPanel;