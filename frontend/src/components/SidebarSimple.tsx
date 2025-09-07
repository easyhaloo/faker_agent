import React from 'react';
import useChatStore from '../store/useChatStore';
import { Plus } from 'lucide-react';
import clsx from 'clsx';

export default function Sidebar() {
  const conversations = useChatStore((s) => s.conversations) || [];
  const selectedId = useChatStore((s) => s.selectedConversationId);
  const selectConversation = useChatStore((s) => s.selectConversation);
  const addConversation = useChatStore((s) => s.addConversation);

  const handleNewConversation = () => {
    addConversation();
  };

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 flex items-center justify-between">
        <div className="text-lg font-bold">对话列表</div>
        <button 
          onClick={handleNewConversation}
          className="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-[#03121a]"
          aria-label="新建对话"
        >
          <Plus size={18} />
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
          <div className="space-y-1 px-2">
            {conversations.map((conv) => {
              const active = selectedId === conv.id;
              return (
                <div
                  key={conv.id}
                  onClick={() => selectConversation(conv.id)}
                  className={clsx(
                    'px-3 py-3 cursor-pointer flex items-center gap-3 rounded-lg',
                    active ? 'bg-sky-600/10 font-semibold' : 'hover:bg-gray-100 dark:hover:bg-[#06101a]'
                  )}
                >
                  <div className="w-9 h-9 rounded-md bg-sky-100 dark:bg-sky-900 flex items-center justify-center text-sky-600">
                    C
                  </div>
                  <div className="flex-1 truncate">
                    <div className="truncate font-medium">{conv.title}</div>
                    <div className="text-xs text-gray-500 dark:text-gray-400 truncate">{conv.snippet || '新对话'}</div>
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