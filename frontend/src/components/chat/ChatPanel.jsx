import { useState, useRef, useEffect } from 'react';
import { useConversationStore } from '../../store/conversationStore';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Bot, User, CornerDownRight, Copy, RefreshCw, ThumbsUp, ThumbsDown, Download, Trash2, Square, Paperclip, Image, MoreVertical } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator
} from '../ui/dropdown-menu';
import { Button } from '../ui/button';
import { Textarea } from '../ui/textarea';
import { Card } from '../ui/card';
import { useI18n } from '../../i18n/index.jsx';

/**
 * Chat Panel Component
 * 
 * Displays the conversation messages and handles sending new messages.
 */
const ChatPanel = ({ conversation, onSendMessage }) => {
  const { t, language } = useI18n();
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);
  const { isLoading } = useConversationStore();
  
  // Auto-resize textarea based on content
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        200
      )}px`;
    }
  }, [inputValue]);
  
  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [conversation?.messages]);
  
  // Handle input change
  const handleInputChange = (e) => {
    setInputValue(e.target.value);
    setIsTyping(e.target.value.length > 0);
  };
  
  // Handle sending a message
  const handleSendMessage = () => {
    if (inputValue.trim() && !isLoading) {
      onSendMessage(inputValue.trim());
      setInputValue('');
      setIsTyping(false);
    }
  };
  
  // Handle key press (Enter to send, Shift+Enter for new line)
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };
  
  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  // Format timestamp
  const formatTimestamp = (timestamp) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch (error) {
      return '';
    }
  };
  
  // If no conversation is selected
  if (!conversation) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-6 bg-gray-50 dark:bg-gray-900">
        <div className="max-w-md text-center">
          <Bot className="mx-auto h-12 w-12 text-blue-500 mb-4" />
          <h2 className="text-2xl font-bold mb-2">{t('conversation.startConversation')}</h2>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            {t('conversation.selectExisting')}
          </p>
          
          {/* 提示卡片区域 */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full mb-4">
            <Card 
              className="p-3 cursor-pointer hover:bg-gray-50 transition-colors" 
              onClick={() => onSendMessage(t('promptCards.weatherPrompt'))}
            >
              <h4 className="font-medium text-gray-800">{t('promptCards.weatherTitle')}</h4>
              <p className="text-sm text-gray-500 mt-1">"{t('promptCards.weatherPrompt')}"</p>
            </Card>
            <Card 
              className="p-3 cursor-pointer hover:bg-gray-50 transition-colors"
              onClick={() => onSendMessage(t('promptCards.planningPrompt'))}
            >
              <h4 className="font-medium text-gray-800">{t('promptCards.planningTitle')}</h4>
              <p className="text-sm text-gray-500 mt-1">"{t('promptCards.planningPrompt')}"</p>
            </Card>
          </div>
          
          <Button onClick={() => onSendMessage(language === 'zh' ? '你好！你能帮我做什么？' : 'Hello! How can you help me today?')}>
            {t('common.startChat')}
          </Button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="flex-1 flex flex-col h-full">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 bg-gray-50 dark:bg-gray-900">
        {/* Empty conversation state */}
        {(!conversation.messages || conversation.messages.length === 0) ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-6">
            <Bot className="h-12 w-12 text-blue-500 mb-4" />
            <h3 className="text-xl font-medium mb-2">{t('conversation.startYourConversation')}</h3>
            <p className="text-gray-600 dark:text-gray-400 max-w-md mb-6">
              {t('conversation.typeMessage')}
            </p>
            
            {/* 提示卡片区域 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full max-w-lg mb-4">
              <Card 
                className="p-3 cursor-pointer hover:bg-gray-50 transition-colors" 
                onClick={() => onSendMessage(t('promptCards.weatherPrompt'))}
              >
                <h4 className="font-medium text-gray-800">天气查询</h4>
                <p className="text-sm text-gray-500 mt-1">"今天北京的天气怎么样？"</p>
              </Card>
              <Card 
                className="p-3 cursor-pointer hover:bg-gray-50 transition-colors"
                onClick={() => onSendMessage(t('promptCards.planningPrompt'))}
              >
                <h4 className="font-medium text-gray-800">任务规划</h4>
                <p className="text-sm text-gray-500 mt-1">"帮我制定一周学习计划"</p>
              </Card>
            </div>
            
            {/* 原有按钮区域 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-w-lg">
              <Button 
                variant="outline" 
                className="text-left justify-start"
                onClick={() => onSendMessage(t('promptCards.helpPrompt'))}
              >
                <CornerDownRight className="mr-2 h-4 w-4" />
                {t('promptCards.helpTitle')}
              </Button>
              <Button 
                variant="outline" 
                className="text-left justify-start"
                onClick={() => onSendMessage(t('promptCards.aboutPrompt'))}
              >
                <CornerDownRight className="mr-2 h-4 w-4" />
                {t('promptCards.aboutTitle')}
              </Button>
            </div>
          </div>
        ) : (
          <div className="space-y-8 px-4 max-w-3xl mx-auto">
            <AnimatePresence>
              {conversation.messages.map((message, index) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.3, type: "spring", damping: 25, stiffness: 300 }}
                  className={`flex ${
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  } w-full max-w-3xl mx-auto mb-4`}
                >
                  {/* AI 回复中状态指示器 */}
                  {isLoading && index === conversation.messages.length - 1 && message.role === 'assistant' && (
                    <div className="absolute left-12 bottom-0 flex items-center">
                      <div className="flex space-x-1">
                        <span className="animate-pulse inline-block h-1.5 w-1.5 rounded-full bg-blue-400 dark:bg-blue-500" style={{ animationDelay: '0ms' }}></span>
                        <span className="animate-pulse inline-block h-1.5 w-1.5 rounded-full bg-blue-400 dark:bg-blue-500" style={{ animationDelay: '150ms' }}></span>
                        <span className="animate-pulse inline-block h-1.5 w-1.5 rounded-full bg-blue-400 dark:bg-blue-500" style={{ animationDelay: '300ms' }}></span>
                      </div>
                    </div>
                  )}
                  <div className={`flex max-w-[70%] group ${
                    message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                  }`}>
                    {/* Avatar */}
                    <div className={`flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center ${
                      message.role === 'user' 
                        ? 'bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-300 ml-2' 
                        : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300 mr-2'
                    }`}>
                      {message.role === 'user' ? <User size={16} /> : <Bot size={16} />}
                    </div>
                    
                    {/* Message Bubble */}
                    <div className={`rounded-2xl px-4 py-3 relative shadow-sm group/message ${
                      message.role === 'user'
                        ? 'bg-blue-500 text-white dark:bg-blue-600 rounded-tr-md rounded-br-md'
                        : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-tl-md rounded-bl-md'
                    }`}>
                      {/* Message Actions - 鼠标悬停时才显示 */}
                      <div className="absolute bottom-0 right-0 transform translate-y-full opacity-0 group-hover/message:opacity-100 transition-opacity pb-1 flex items-center gap-1 bg-white dark:bg-gray-800 p-1 rounded-md shadow-sm border border-gray-200 dark:border-gray-700">
                        <button className="h-7 w-7 p-0 flex items-center justify-center rounded-md bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-600 dark:text-gray-300">
                          <Copy size={14} />
                        </button>
                        {message.role === 'assistant' && (
                          <button className="h-7 w-7 p-0 flex items-center justify-center rounded-md bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-600 dark:text-gray-300">
                            <RefreshCw size={14} />
                          </button>
                        )}
                        <button className="h-7 w-7 p-0 flex items-center justify-center rounded-md bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-red-500 hover:text-red-700">
                          <Trash2 size={14} />
                        </button>
                      </div>
                      <div className="whitespace-pre-wrap break-words text-sm">
                        {message.content}
                      </div>
                      <div className={`text-xs mt-1 ${
                        message.role === 'user'
                          ? 'text-blue-100 dark:text-blue-200'
                          : 'text-gray-500 dark:text-gray-400'
                      }`}>
                        {formatTimestamp(message.created_at)}
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>
      
      {/* Input Area */}
      <div className="border-t border-gray-200 dark:border-gray-800 p-4 bg-white dark:bg-gray-900">
        {isLoading && (
          <div className="flex justify-end mb-2">
            <button className="h-8 px-3 text-sm text-red-500 hover:text-red-700 border border-red-200 hover:border-red-300 dark:border-red-800 dark:hover:border-red-700 rounded-full flex items-center gap-1 bg-white dark:bg-gray-800 shadow-sm">
              <Square size={14} />
              {t('common.stop')}
            </button>
          </div>
        )}
        <div className="relative max-w-3xl mx-auto">
          <div className="flex items-center"> 
            <button className="h-9 w-9 rounded-full flex items-center justify-center mr-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
              <Paperclip size={18} />
            </button>
            <div className="flex-1 relative">
              <Textarea
                ref={textareaRef}
                value={inputValue}
                onChange={handleInputChange}
                onKeyDown={handleKeyDown}
                placeholder={t('common.inputPlaceholder')}
                className="pr-12 resize-none overflow-hidden min-h-[48px] max-h-[200px] rounded-3xl border-gray-300 dark:border-gray-700 focus:border-blue-400 dark:focus:border-blue-500 focus:ring focus:ring-blue-200 dark:focus:ring-blue-900 focus:ring-opacity-50 shadow-sm"
                disabled={isLoading}
              />
              <button
                className={`absolute right-3 bottom-2.5 h-8 w-8 rounded-full flex items-center justify-center ${
                  !isTyping || isLoading 
                    ? 'bg-gray-300 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-not-allowed' 
                    : 'bg-blue-500 hover:bg-blue-600 text-white cursor-pointer shadow-sm'
                } transition-colors`}
                onClick={handleSendMessage}
                disabled={!isTyping || isLoading}
              >
                <Send size={16} />
              </button>
            </div>
          </div>
        </div>
        
        {/* Loading Indicator - 不再显示在底部 */}
      </div>
    </div>
  );
};

export default ChatPanel;