import { useState, useRef, useEffect } from 'react';
import { useAgentStore } from '../../store/agentStore';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronRight, ChevronLeft, MessageCircle, MessageSquarePlus, Bot, User, PenSquare, Edit, Menu } from 'lucide-react';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Card } from '../ui/card';
import { cn } from '../../utils/cn';

/**
 * 响应式会话侧边栏组件
 * 整合了新建会话和会话历史管理功能
 * @param {Function} onStateChange - 侧边栏状态变化回调
 */
const ConversationSidebar = ({ onStateChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isCreatingNew, setIsCreatingNew] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const messagesEndRef = useRef(null);
  const sidebarRef = useRef(null);
  
  // 处理点击外部区域自动收起侧边栏
  useEffect(() => {
    const handleClickOutside = (event) => {
      // 只有在侧边栏打开且点击在侧边栏外部时才自动收起
      // 并且不是在创建新会话状态下
      if (isOpen && !isCreatingNew && sidebarRef.current && !sidebarRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    
    // 添加全局点击事件监听
    document.addEventListener('mousedown', handleClickOutside);
    
    // 清理函数
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen, isCreatingNew]);
  
  const messages = useAgentStore((state) => state.messages);
  const sendMessageToAgent = useAgentStore((state) => state.sendMessageToAgent);
  
  // 预设的快速提示
  const quickPrompts = [
    { title: "天气查询", prompt: "今天北京的天气怎么样？" },
    { title: "任务规划", prompt: "帮我制定一周学习计划" },
  ];
  
  // 切换侧边栏状态
  const toggleSidebar = () => {
    const newState = !isOpen;
    setIsOpen(newState);
    // 通知父组件状态变化
    if (onStateChange) {
      onStateChange(newState);
    }
  };
  
  // 滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
    
    // 当状态变化时通知父组件
    if (onStateChange) {
      onStateChange(isOpen);
    }
  }, [messages, isOpen, onStateChange]);
  
  // 侧边栏动画变体
  const sidebarVariants = {
    open: { width: '260px', transition: { type: 'spring', damping: 20, stiffness: 250 } },
    closed: { width: '50px', transition: { type: 'spring', damping: 20, stiffness: 250 } }
  };
  
  // 响应式侧边栏变体（小屏幕）
  const mobileSidebarVariants = {
    open: { width: '85%', maxWidth: '300px', transition: { type: 'spring', damping: 20, stiffness: 250 } },
    closed: { width: '50px', transition: { type: 'spring', damping: 20, stiffness: 250 } }
  };
  
  // 根据屏幕尺寸选择变体
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);
  
  // 监听屏幕尺寸变化
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  
  // 根据屏幕尺寸选择使用的变体
  const variants = isMobile ? mobileSidebarVariants : sidebarVariants;
  
  // 内容动画变体
  const contentVariants = {
    open: { opacity: 1, x: 0 },
    closed: { opacity: 0, x: -20 }
  };
  
  // 使用预设提示
  const handleQuickPrompt = (prompt) => {
    sendMessageToAgent(prompt);
  };
  
  // 消息计数
  const messageCount = messages.length;
  const userMessageCount = messages.filter(m => m.role === 'user').length;
  const assistantMessageCount = messages.filter(m => m.role === 'assistant').length;
  
  return (
    <motion.div
      ref={sidebarRef}
      className="h-full border-r border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 shadow-sm overflow-hidden z-20 flex-shrink-0 relative"
      onClick={(e) => {
        // 当侧边栏打开且不在创建新会话状态下，点击侧边栏空白区域可以关闭侧边栏
        // 检查是否点击的是侧边栏本身，而不是其中的子元素
        if (isOpen && !isCreatingNew && e.target === e.currentTarget) {
          setIsOpen(false);
        }
      }}
      initial="closed"
      animate={isOpen ? "open" : "closed"}
      variants={sidebarVariants}
    >
      {/* 装饰性边缘渐变效果 */}
      <div className="absolute top-0 right-0 w-1 h-full bg-gradient-to-r from-transparent to-blue-100 dark:to-blue-900/20 pointer-events-none opacity-70"></div>
      {/* 侧边栏切换按钮 */}
      <Button
        variant="ghost"
        size="sm"
        onClick={toggleSidebar}
        className="absolute top-4 right-2 z-10 h-6 w-6 p-0 rounded-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-sm text-blue-500 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 hover:text-blue-600 dark:hover:text-blue-300 transition-colors duration-200"
        aria-label={isOpen ? "收起会话面板" : "展开会话面板"}
        title={isOpen ? "收起会话面板" : "展开会话面板"}
      >
        {isOpen ? <ChevronLeft size={14} /> : <ChevronRight size={14} />}
      </Button>
      
      {/* 侧边栏标题 */}
      <div className="flex items-center h-14 border-b border-gray-200 dark:border-gray-700 px-4 bg-white dark:bg-gray-800">
        {isOpen ? (
          <h3 className="font-medium text-gray-800 dark:text-gray-200 flex items-center text-base">
            <MessageCircle size={18} className="mr-2 text-blue-500 dark:text-blue-400" />
            会话列表
          </h3>
        ) : (
          <MessageCircle size={20} className="mx-auto text-blue-500 dark:text-blue-400" />
        )}
      </div>
      
      {/* 新建会话按钮 */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="p-3 border-b border-gray-200 dark:border-gray-700"
            initial="closed"
            animate="open"
            exit="closed"
            variants={contentVariants}
          >
            <Button
              className="w-full bg-blue-500 hover:bg-blue-600 text-white rounded-2xl shadow-sm"
              size="sm"
              onClick={() => setIsCreatingNew(true)}
            >
              <MessageSquarePlus size={16} className="mr-2" />
              新建会话
            </Button>
            
            {/* 快速提示区域 */}
            {isCreatingNew ? (
              <div className="mt-3 bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                <input
                  type="text"
                  className="w-full px-3 py-2 text-sm rounded-2xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm"
                  placeholder="输入会话标题..."
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  autoFocus
                />
                <div className="flex gap-2 mt-2">
                  <Button
                    size="sm"
                    className="flex-1 bg-blue-500 hover:bg-blue-600 text-white text-xs"
                    onClick={() => {
                      // 这里可以添加创建新会话的逻辑
                      setIsCreatingNew(false);
                      setNewTitle('');
                    }}
                  >
                    创建
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    className="flex-1 text-xs"
                    onClick={() => {
                      setIsCreatingNew(false);
                      setNewTitle('');
                    }}
                  >
                    取消
                  </Button>
                </div>
              </div>
            ) : (
              <div className="mt-3 space-y-2">
                <p className="text-xs text-gray-500 dark:text-gray-400 px-1">快速提示:</p>
                {quickPrompts.map((item, index) => (
                  <Card 
                    key={index}
                    className="p-2 cursor-pointer bg-white hover:bg-gray-50 dark:bg-gray-800 dark:hover:bg-gray-700 transition-colors border border-gray-200 dark:border-gray-700 rounded-2xl shadow-sm"
                    onClick={() => handleQuickPrompt(item.prompt)}
                  >
                    <div className="flex items-start">
                      <PenSquare size={14} className="mr-2 mt-0.5 text-gray-500 dark:text-gray-400" />
                      <div>
                        <h4 className="text-sm font-medium">{item.title}</h4>
                        <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{item.prompt}</p>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* 会话统计信息 */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="px-4 py-3 border-b border-gray-200 dark:border-gray-700"
            initial="closed"
            animate="open"
            exit="closed"
            variants={contentVariants}
          >
            <div className="flex flex-col gap-1">
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-500">消息总数</span>
                <Badge variant="secondary" className="text-xs">{messageCount}</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-500">我的消息</span>
                <Badge variant="outline" className="text-xs">{userMessageCount}</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-500">助手回复</span>
                <Badge variant="outline" className="text-xs">{assistantMessageCount}</Badge>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* 消息历史列表 */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="h-[calc(100%-200px)] overflow-y-auto p-3"
            initial="closed"
            animate="open"
            exit="closed"
            variants={contentVariants}
          >
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-gray-400">
                <MessageCircle size={32} className="mb-2 opacity-50" />
                <p className="text-sm text-center">暂无会话记录</p>
              </div>
            ) : (
              <div className="space-y-3">
                {messages.map((message, index) => {
                  // 检查是否与前一条消息是同一角色
                  const isPreviousSameRole = index > 0 && messages[index - 1].role === message.role;
                  // 检查是否与下一条消息是同一角色
                  const isNextSameRole = index < messages.length - 1 && messages[index + 1].role === message.role;
                  
                  // 根据消息连续性添加不同的圆角样式
                  const borderRadiusClass = message.role === 'user'
                    ? isPreviousSameRole && isNextSameRole ? 'rounded-r-md' 
                      : isPreviousSameRole ? 'rounded-tr-md rounded-br-xl' 
                      : isNextSameRole ? 'rounded-tr-xl rounded-br-md' 
                      : 'rounded-r-xl'
                    : isPreviousSameRole && isNextSameRole ? 'rounded-l-md' 
                      : isPreviousSameRole ? 'rounded-tl-md rounded-bl-xl' 
                      : isNextSameRole ? 'rounded-tl-xl rounded-bl-md' 
                      : 'rounded-l-xl';
                  
                  return (
                    <Card 
                      key={message.id} 
                      className={cn(
                        `p-2 text-sm overflow-hidden hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer transition-colors ${borderRadiusClass}`,
                        message.role === 'user' 
                          ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-100 dark:border-blue-800' 
                          : 'bg-gray-50 dark:bg-gray-700/30',
                        isPreviousSameRole ? 'mt-0.5' : 'mt-2'
                      )}
                    >
                      <div className="flex items-start gap-1.5">
                        {/* 只在序列中第一个相同角色消息上显示图标 */}
                        {!isPreviousSameRole ? (
                          <div className={cn("mt-0.5", message.role === 'user' ? "text-blue-500" : "text-gray-500")}>
                            {message.role === 'user' ? <User size={14} /> : <Bot size={14} />}
                          </div>
                        ) : (
                          <div className="w-3.5">{/* 留出空间以保持对齐 */}</div>
                        )}
                        <div className={cn(
                          "flex-1 text-xs",
                          isPreviousSameRole && isNextSameRole ? 'line-clamp-2' : 'line-clamp-3'
                        )}>
                          {message.content}
                        </div>
                      </div>
                    </Card>
                  );
                })}
                <div ref={messagesEndRef} />
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* 最小化视图只显示友好按钮 */}
      {!isOpen && (
        <div className="flex flex-col items-center gap-3 mt-6">
          <Button
            variant="ghost"
            size="sm"
            className="w-8 h-8 p-0 rounded-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-700 text-blue-600 dark:text-blue-300 shadow-sm transition-all duration-200"
            onClick={toggleSidebar}
            title="展开会话面板"
            aria-label="展开会话面板"
          >
            <ChevronRight size={16} />
          </Button>
          <Badge 
            variant="secondary" 
            className="text-xs flex justify-center px-2 bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-300 border border-gray-200 dark:border-gray-700"
          >
            {messageCount}
          </Badge>
        </div>
      )}
    </motion.div>
  );
};

export default ConversationSidebar;