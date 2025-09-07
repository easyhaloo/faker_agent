import { useState, useEffect } from 'react';
import { useConversationStore } from '../../store/conversationStore';
import ConversationDrawer from './ConversationDrawer';
import EnhancedChatPanel from './EnhancedChatPanel';
import { Button } from '../ui/button';
import { MessageSquarePlus, Menu, ChevronLeft, ChevronRight, Settings, User, Download, Trash2, Edit3, X, Check, MoreVertical, Loader2 } from 'lucide-react';
import { useI18n } from '../../i18n/index.jsx';
// 移除主题切换按钮导入
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator
} from '../ui/dropdown-menu';

/**
 * Conversation Manager Component
 * 
 * Top-level component that manages the conversation UI, including the drawer
 * and chat panel. Controls the state of the drawer (open/closed) and handles
 * responsive behavior.
 */
const ConversationManager = () => {
  const { t } = useI18n();
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [drawerCollapsed, setDrawerCollapsed] = useState(false);
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  const { 
    currentConversationId, 
    createConversation, 
    sendMessage,
    conversations,
    updateConversationTitle,
    deleteConversation
  } = useConversationStore();
  
  const [isExporting, setIsExporting] = useState(false);
  
  // Handle drawer toggle
  const toggleDrawer = () => {
    setIsDrawerOpen(!isDrawerOpen);
  };
  
  // Handle drawer collapse/expand
  const toggleDrawerCollapse = () => {
    setDrawerCollapsed(!drawerCollapsed);
  };
  
  // Close drawer on larger screens
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 768) {
        setIsDrawerOpen(false);
      }
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  
  // Create a new conversation
  const handleNewChat = async () => {
    await createConversation();
    // Close any open dialogs
    setShowClearConfirm(false);
  };
  
  // Handle sending a message
  const handleSendMessage = async (message) => {
    await sendMessage(message);
  };
  
  // Start title editing
  const handleStartTitleEdit = () => {
    if (currentConversation) {
      setNewTitle(currentConversation.title);
      setIsEditingTitle(true);
    }
  };
  
  // Save edited title
  const handleSaveTitle = async () => {
    if (currentConversationId && newTitle.trim()) {
      await updateConversationTitle(currentConversationId, newTitle.trim());
      setIsEditingTitle(false);
    }
  };
  
  // Clear/delete current conversation
  const handleClearConversation = async () => {
    if (currentConversationId) {
      await deleteConversation(currentConversationId);
      setShowClearConfirm(false);
    }
  };
  
  // Export conversation
  const handleExportConversation = async (format = 'json') => {
    if (!currentConversationId) return;
    
    setIsExporting(true);
    try {
      const result = await conversationService.exportConversation(currentConversationId, format);
      const { content, filename, content_type } = result.data;
      
      // Create blob and download
      const blob = new Blob([typeof content === 'object' ? JSON.stringify(content, null, 2) : content], {
        type: content_type
      });
      
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      console.log(`Conversation exported successfully as ${filename}`);
    } catch (error) {
      console.error('Error exporting conversation:', error);
      alert(t('common.error') || 'Failed to export conversation');
    } finally {
      setIsExporting(false);
    }
  };
  
  // Get current conversation
  const currentConversation = conversations.find(
    c => c.id === currentConversationId
  );
  
  return (
    <div className="flex h-full relative overflow-hidden">
      {/* Bottom account area */}
      {/* <div className="absolute bottom-0 left-0 right-0 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-2 flex justify-end items-center z-10 md:px-4">
        <Button
          variant="ghost"
          size="sm"
          className="h-8 w-8 p-0 rounded-full overflow-hidden border border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-700"
          title={t('common.account')}
        >
          <User size={18} />
        </Button>
      </div> */}
      {/* Mobile Drawer Toggle */}
      <Button
        variant="ghost"
        size="icon"
        className="absolute left-4 top-4 md:hidden z-50"
        onClick={toggleDrawer}
      >
        <Menu className="h-5 w-5" />
      </Button>
      
      {/* Conversation Drawer */}
      <div className="relative flex h-full">
        <ConversationDrawer 
          isOpen={isDrawerOpen} 
          onToggle={toggleDrawer} 
          isCollapsed={drawerCollapsed} 
        />
        
        {/* Collapse/Expand Toggle Button */}
        <Button
          variant="ghost"
          size="sm"
          className="absolute top-4 -right-3 h-6 w-6 p-0 rounded-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-sm z-50"
          onClick={toggleDrawerCollapse}
        >
          {drawerCollapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
        </Button>
      </div>
      
      {/* Chat Area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        {/* Header */}
        <div className="h-16 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between px-4 md:px-6">
          <div className="flex items-center ml-10 md:ml-0">
            {isEditingTitle ? (
              <div className="flex items-center">
                <input
                  type="text"
                  className="px-2 py-1 text-sm border rounded-2xl dark:bg-gray-800 dark:border-gray-700 mr-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') handleSaveTitle();
                    if (e.key === 'Escape') setIsEditingTitle(false);
                  }}
                  autoFocus
                />
                <div className="flex space-x-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-7 w-7 p-0 text-green-500 hover:text-green-600 hover:bg-green-50 dark:hover:bg-green-900/20 rounded-full shadow-sm"
                    onClick={handleSaveTitle}
                    title={t('common.save') || '确认'}
                  >
                    <Check size={14} />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-7 w-7 p-0 text-red-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-full shadow-sm"
                    onClick={() => setIsEditingTitle(false)}
                    title={t('common.cancel') || '取消'}
                  >
                    <X size={14} />
                  </Button>
                </div>
              </div>
            ) : (
              <div className="flex items-center group">
                <h1 className="font-medium text-lg group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                  {currentConversation?.title || t('conversation.newConversation')}
                </h1>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-6 w-6 p-0 ml-2 opacity-0 group-hover:opacity-100 transition-opacity"
                  onClick={handleStartTitleEdit}
                >
                  <Edit3 size={14} className="text-gray-500" />
                </Button>
                <div className="ml-2">
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-6 w-6 p-0 opacity-50 hover:opacity-100"
                      >
                        <MoreVertical size={14} />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="start" className="w-[160px]">
                      <DropdownMenuItem
                        className="cursor-pointer flex items-center text-gray-700 dark:text-gray-300"
                        onClick={() => handleExportConversation('json')}
                        disabled={isExporting}
                      >
                        {isExporting ? (
                          <Loader2 className="mr-2 h-4 w-4 flex-shrink-0 animate-spin" />
                        ) : (
                          <Download className="mr-2 h-4 w-4 flex-shrink-0" />
                        )}
                        <span>{t('common.export')} JSON</span>
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        className="cursor-pointer flex items-center text-gray-700 dark:text-gray-300"
                        onClick={() => handleExportConversation('txt')}
                        disabled={isExporting}
                      >
                        {isExporting ? (
                          <Loader2 className="mr-2 h-4 w-4 flex-shrink-0 animate-spin" />
                        ) : (
                          <Download className="mr-2 h-4 w-4 flex-shrink-0" />
                        )}
                        <span>{t('common.export')} TXT</span>
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        className="cursor-pointer flex items-center text-gray-700 dark:text-gray-300"
                        onClick={() => handleExportConversation('md')}
                        disabled={isExporting}
                      >
                        {isExporting ? (
                          <Loader2 className="mr-2 h-4 w-4 flex-shrink-0 animate-spin" />
                        ) : (
                          <Download className="mr-2 h-4 w-4 flex-shrink-0" />
                        )}
                        <span>{t('common.export')} MD</span>
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem
                        className="cursor-pointer flex items-center text-red-500 hover:text-red-700 focus:text-red-700"
                        onClick={() => setShowClearConfirm(true)}
                      >
                        <Trash2 className="mr-2 h-4 w-4 flex-shrink-0" />
                        <span>{t('common.delete')}</span>
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </div>
            )}
          </div>
          <div className="flex items-center space-x-2">
            {/* Download button moved to dropdown menu */}
            
            {/* Lightweight Clear Conversation Confirmation */}
            {showClearConfirm && (
              <div className="absolute top-16 right-4 bg-white dark:bg-gray-800 shadow-md rounded-2xl p-3 z-50 border border-gray-200 dark:border-gray-700 w-64 bg-opacity-95 dark:bg-opacity-95">
                <h3 className="text-sm font-medium mb-1">{t('conversation.confirmClear')}</h3>
                <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">
                  {t('conversation.clearWarning')}
                </p>
                <div className="flex justify-end space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="text-xs h-7 px-2 rounded-lg"
                    onClick={() => setShowClearConfirm(false)}
                  >
                    {t('common.cancel')}
                  </Button>
                  <Button
                    variant="destructive"
                    size="sm"
                    className="text-xs h-7 px-2 rounded-lg"
                    onClick={handleClearConversation}
                  >
                    {t('common.delete')}
                  </Button>
                </div>
              </div>
            )}
            <Button
              variant="outline"
              size="sm"
              className="flex items-center ml-2"
              onClick={handleNewChat}
            >
              <MessageSquarePlus className="mr-2 h-4 w-4" />
              {t('common.newChat')}
            </Button>
          </div>
        </div>
        
        {/* Chat Panel - 使用EnhancedChatPanel作为默认实现 */}
        <EnhancedChatPanel />
      </div>
    </div>
  );
};

export default ConversationManager;