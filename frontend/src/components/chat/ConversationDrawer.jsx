import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useConversationStore } from '../../store/conversationStore';
import { 
  MessageSquare, 
  PlusCircle, 
  Trash2, 
  Edit3,
  Check,
  X,
  Calendar,
  MoreVertical,
  Clock,
  Search,
  ThumbsUp,
  ThumbsDown,
  Settings
} from 'lucide-react';
import { 
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter
} from '../ui/dialog';
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator
} from '../ui/dropdown-menu';
import { Button } from '../ui/button';
import { formatDistanceToNow } from 'date-fns';
import { useI18n } from '../../i18n/index.jsx';
import SystemSettings from '../ui/SystemSettings';

/**
 * Conversation Drawer Component
 * 
 * Displays a list of conversations with options to create, select, edit, and delete.
 * Supports collapsed mode for minimized view and search functionality.
 */
const ConversationDrawer = ({ isOpen, onToggle, isCollapsed = false }) => {
  const { t } = useI18n();
  const {
    conversations,
    currentConversationId,
    createConversation,
    setCurrentConversation,
    updateConversationTitle,
    deleteConversation,
    initialize,
    isLoading
  } = useConversationStore();
  
  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState('');
  const [confirmDeleteId, setConfirmDeleteId] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const editInputRef = useRef(null);
  const searchInputRef = useRef(null);
  
  // Initialize conversations on component mount
  useEffect(() => {
    initialize();
  }, [initialize]);
  
  // Focus the edit input when editing starts
  useEffect(() => {
    if (editingId && editInputRef.current) {
      editInputRef.current.focus();
    }
  }, [editingId]);
  
  // Focus the search input when searching starts
  useEffect(() => {
    if (isSearching && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [isSearching]);
  
  // Start editing a conversation title
  const handleStartEdit = (conversation) => {
    setEditingId(conversation.id);
    setEditTitle(conversation.title);
  };
  
  // Save edited conversation title
  const handleSaveEdit = async () => {
    if (editingId && editTitle.trim()) {
      await updateConversationTitle(editingId, editTitle.trim());
      setEditingId(null);
      setEditTitle('');
    } else if (editingId) {
      // If title is empty, just cancel editing
      handleCancelEdit();
    }
  };
  
  // Cancel editing
  const handleCancelEdit = () => {
    setEditingId(null);
    setEditTitle('');
  };
  
  // Create a new conversation
  const handleNewConversation = async () => {
    await createConversation();
  };
  
  // Select a conversation
  const handleSelectConversation = (conversationId) => {
    if (editingId) return; // Don't select while editing
    setCurrentConversation(conversationId);
    if (window.innerWidth < 768) {
      onToggle(); // Close drawer on mobile after selection
    }
  };
  
  // Confirm and delete a conversation
  const handleDeleteConversation = async (id) => {
    setConfirmDeleteId(null);
    await deleteConversation(id);
  };
  
  // Format the date for display
  const formatDate = (dateString) => {
    try {
      return formatDistanceToNow(new Date(dateString), { addSuffix: true });
    } catch (error) {
      return 'Unknown date';
    }
  };
  
  // Toggle search mode
  const toggleSearch = () => {
    setIsSearching(!isSearching);
    if (!isSearching) {
      setSearchQuery('');
    }
  };
  
  // Filter conversations based on search query
  const filteredConversations = searchQuery
    ? conversations.filter(conversation => 
        conversation.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (conversation.last_message && 
         conversation.last_message.toLowerCase().includes(searchQuery.toLowerCase()))
      )
    : conversations;
  
  return (
    <div className={`
      fixed inset-y-0 left-0 z-40
      ${isCollapsed ? 'w-16' : 'w-72'} bg-white dark:bg-gray-900
      border-r border-gray-200 dark:border-gray-800
      transform transition-all duration-300 ease-in-out
      ${isOpen ? 'translate-x-0' : '-translate-x-full'}
      md:relative md:translate-x-0
      pb-12 md:pb-0
    `}>
      {/* Header */}
      <div className="h-16 px-4 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between">
        <h2 className="font-semibold flex items-center">
          <MessageSquare className={`${isCollapsed ? 'mx-auto' : 'mr-2'} h-5 w-5 text-blue-500`} />
          {!isCollapsed && t('conversation.title')}
        </h2>
        {!isCollapsed && (
          <div className="flex items-center">
            <Button 
              variant="ghost" 
              size="sm" 
              className="h-8 w-8 p-0"
              onClick={toggleSearch}
              title={t('common.search')}
            >
              <Search className="h-4 w-4" />
            </Button>
            <Button 
              variant="ghost" 
              size="sm" 
              className="md:hidden ml-1"
              onClick={onToggle}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        )}
      </div>
      
      {/* Search Bar */}
      {!isCollapsed && isSearching && (
        <div className="p-2 border-b border-gray-200 dark:border-gray-800">
          <div className="relative">
            <Search className="h-4 w-4 absolute left-2 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              ref={searchInputRef}
              type="text"
              className="w-full pl-8 pr-8 py-1.5 text-sm border rounded dark:bg-gray-800 dark:border-gray-700"
              placeholder={t('common.searchConversations')}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            {searchQuery && (
              <button
                className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                onClick={() => setSearchQuery('')}
              >
                <X className="h-3.5 w-3.5" />
              </button>
            )}
          </div>
        </div>
      )}
      
      {/* New Conversation Button */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-800">
        <Button 
          className={`w-full flex items-center justify-center ${isCollapsed ? 'p-0 h-8 w-8 mx-auto' : ''}`}
          onClick={handleNewConversation}
          disabled={isLoading}
        >
          <PlusCircle className={`${isCollapsed ? '' : 'mr-2'} h-4 w-4`} />
          {!isCollapsed && t('conversation.newConversation')}
        </Button>
      </div>
      
      {/* Conversations List */}
      <div className={`overflow-y-auto h-[calc(100%-8rem)] ${isSearching ? 'h-[calc(100%-12rem)]' : ''} ${isCollapsed ? 'hidden' : 'block'}`}>
        {filteredConversations.length === 0 ? (
          <div className="p-8 text-center text-gray-500 dark:text-gray-400">
            <MessageSquare className="mx-auto h-8 w-8 mb-2 opacity-50" />
            {searchQuery ? (
              <p className="text-sm">{t('common.noSearchResults')}</p>
            ) : (
              <>
                <p className="text-sm">{t('common.noConversationsYet')}</p>
                <p className="text-xs mt-1">{t('common.startNewConversation')}</p>
              </>
            )}
          </div>
        ) : (
          <ul className="divide-y divide-gray-200 dark:divide-gray-800">
            {filteredConversations.map(conversation => (
              <li 
                key={conversation.id}
                className={`
                  relative group
                  ${currentConversationId === conversation.id 
                    ? 'bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-500' 
                    : 'hover:bg-gray-50 dark:hover:bg-gray-800/50'}
                `}
              >
                {/* Conversation Item */}
                <div 
                  className={`
                    p-3 cursor-pointer
                    ${editingId === conversation.id ? 'pointer-events-none' : ''}
                    ${currentConversationId === conversation.id ? 'pl-2' : 'pl-3'}
                  `}
                  onClick={() => handleSelectConversation(conversation.id)}
                >
                  {/* Edit Mode */}
                  {editingId === conversation.id ? (
                    <div className="flex items-center gap-2 p-1">
                      <input
                        ref={editInputRef}
                        type="text"
                        className="flex-1 px-2 py-1 text-sm border rounded dark:bg-gray-800 dark:border-gray-700"
                        value={editTitle}
                        onChange={(e) => setEditTitle(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') handleSaveEdit();
                          if (e.key === 'Escape') handleCancelEdit();
                        }}
                        autoFocus
                      />
                      <button 
                        className="h-7 w-7 p-0 flex items-center justify-center hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
                        onClick={handleSaveEdit}
                      >
                        <Check className="h-4 w-4 text-green-500" />
                      </button>
                      <button 
                        className="h-7 w-7 p-0 flex items-center justify-center hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
                        onClick={handleCancelEdit}
                      >
                        <X className="h-4 w-4 text-red-500" />
                      </button>
                    </div>
                  ) : (
                    <>
                      {/* View Mode */}
                      <div className="flex justify-between items-start">
                        <div className="flex-1 min-w-0">
                          <h3 className="text-sm font-medium truncate">{conversation.title}</h3>
                          
                          {/* Preview of last message or message count */}
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 truncate">
                            {conversation.last_message || 
                              `${conversation.message_count || 0} messages`}
                          </p>
                          
                          {/* Timestamp */}
                          <div className="flex items-center mt-1.5 text-xs text-gray-400 dark:text-gray-500">
                            <Clock className="h-3 w-3 mr-1" />
                            {formatDate(conversation.updated_at)}
                          </div>
                        </div>
                        
                        {/* Actions Menu - Only visible on hover for desktop, always visible on mobile */}
                        <div className="relative shrink-0 ml-2 opacity-0 group-hover:opacity-100 transition-opacity md:opacity-100 md:visible">
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button
                                variant="ghost"
                                size="sm"
                                className="h-7 w-7 p-0 opacity-75 hover:opacity-100"
                                onClick={(e) => e.stopPropagation()}
                              >
                                <MoreVertical className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end" className="w-[160px]">
                              <DropdownMenuItem
                                className="cursor-pointer flex items-center text-gray-700 dark:text-gray-300"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleStartEdit(conversation);
                                }}
                              >
                                <Edit3 className="mr-2 h-4 w-4 flex-shrink-0" />
                                <span>{t('conversation.renameConversation') || '重命名'}</span>
                              </DropdownMenuItem>
                              <DropdownMenuSeparator />
                              <DropdownMenuItem
                                className="cursor-pointer flex items-center text-red-500 hover:text-red-700 focus:text-red-700"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setConfirmDeleteId(conversation.id);
                                }}
                              >
                                <Trash2 className="mr-2 h-4 w-4 flex-shrink-0" />
                                <span>{t('conversation.deleteConversation') || '删除'}</span>
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </div>
                      </div>
                    </>
                  )}
                </div>
                
                {/* Lightweight Confirmation Popover for Delete */}
                {confirmDeleteId === conversation.id && (
                  <div className="absolute right-0 bottom-0 transform translate-y-full z-50">
                    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-3 m-2 max-w-[250px] bg-opacity-95 dark:bg-opacity-95">
                      <p className="text-sm font-medium mb-2">
                        {t('conversation.deleteConfirmation')}
                      </p>
                      <div className="flex justify-end space-x-2 mt-3">
                        <Button 
                          variant="outline" 
                          size="sm"
                          className="text-xs h-7 px-2"
                          onClick={() => setConfirmDeleteId(null)}
                        >
                          {t('common.cancel')}
                        </Button>
                        <Button 
                          variant="destructive"
                          size="sm"
                          className="text-xs h-7 px-2"
                          onClick={() => handleDeleteConversation(conversation.id)}
                        >
                          {t('common.delete')}
                        </Button>
                      </div>
                    </div>
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
      
      {/* 系统设置按钮（左下角） */}
      <div className="absolute bottom-0 left-0 right-0 border-t border-gray-200 dark:border-gray-800 p-3 bg-white dark:bg-gray-900 flex justify-center">
        <SystemSettings />
      </div>
    </div>
  );
};

export default ConversationDrawer;