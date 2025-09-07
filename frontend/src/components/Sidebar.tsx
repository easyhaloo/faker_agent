import React from 'react';
import { List } from 'react-window';
import useChatStore from '../store/useChatStore';
import { Plus } from 'lucide-react';
import clsx from 'clsx';

function ConversationItem({ index, style, data }: any) {
  const { conversations, selectConversation, selectedId } = data;
  
  // Safety check
  if (!conversations || !Array.isArray(conversations) || index >= conversations.length) {
    return <div style={style} />;
  }
  
  const conv = conversations[index];
  if (!conv) return <div style={style} />;

  const active = selectedId === conv.id;

  return (
    <div
      style={style}
      onClick={() => selectConversation(conv.id)}
      className={clsx(
        'px-4 py-3 cursor-pointer flex items-center gap-3',
        active ? 'bg-sky-600/10 font-semibold' : 'hover:bg-gray-100 dark:hover:bg-[#06101a]'
      )}
    >
      <div className="w-9 h-9 rounded-md bg-sky-100 dark:bg-sky-900 flex items-center justify-center text-sky-600">
        C
      </div>
      <div className="flex-1 truncate">
        <div className="truncate">{conv.title}</div>
        <div className="text-xs text-gray-500 dark:text-gray-400 truncate">{conv.snippet}</div>
      </div>
    </div>
  );
}

export default function Sidebar() {
  const conversations = useChatStore((s) => s.conversations) || [];
  const selectedId = useChatStore((s) => s.selectedConversationId);
  const selectConversation = useChatStore((s) => s.selectConversation);
  const addConversation = useChatStore((s) => s.addConversation);

  const handleNewConversation = () => {
    addConversation();
  };

  return (
    <div className="h-full flex flex-col p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="text-lg font-bold text-gray-800 dark:text-gray-200">对话列表</div>
        <button 
          onClick={handleNewConversation}
          className="p-2 rounded-md hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
          aria-label="新建对话"
        >
          <Plus size={18} className="text-gray-600 dark:text-gray-400" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto">
        {conversations.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">
            <div className="text-center">
              <div className="mb-2">暂无对话</div>
              <div className="text-sm">点击 + 按钮创建新对话</div>
            </div>
          </div>
        ) : (
          <div className="space-y-1">
            {conversations.map((conv) => {
              const active = selectedId === conv.id;
              return (
                <div
                  key={conv.id}
                  onClick={() => selectConversation(conv.id)}
                  className={clsx(
                    'px-3 py-3 cursor-pointer flex items-center gap-3 rounded-lg transition-colors',
                    active ? 'bg-gray-200 dark:bg-gray-700 font-medium' : 'hover:bg-gray-100 dark:hover:bg-gray-800'
                  )}
                >
                  <div className="w-9 h-9 rounded-md bg-gray-200 dark:bg-gray-700 flex items-center justify-center text-gray-600 dark:text-gray-300 font-medium">
                    {conv.title.charAt(0).toUpperCase() || 'C'}
                  </div>
                  <div className="flex-1 truncate">
                    <div className="truncate text-sm font-medium text-gray-800 dark:text-gray-200">{conv.title}</div>
                    <div className="text-xs text-gray-500 dark:text-gray-400 truncate mt-1">{conv.snippet || '新对话'}</div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}