import React, { useEffect, useRef } from 'react';
import MessageBubble from './MessageBubble';
import useChatStore from '../store/useChatStore';

export default function MessageList() {
  const conv = useChatStore((s) => s.conversations.find(c => c.id === s.selectedConversationId));
  const updateMessage = useChatStore((s) => s.updateMessage);
  const listRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: 'smooth' });
  }, [conv?.messages.length]);

  if (!conv) return (
    <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">
      <div className="text-center">
        <div className="text-lg mb-2">请选择一个会话</div>
        <div className="text-sm">从左侧对话列表中选择一个会话开始聊天</div>
      </div>
    </div>
  );

  return (
    <div ref={listRef} className="space-y-3">
      {conv.messages.length === 0 ? (
        <div className="flex items-center justify-center h-[60vh] text-gray-500 dark:text-gray-400">
          <div className="text-center">
            <div className="text-lg mb-2">开始对话</div>
            <div className="text-sm">在下方输入框中输入消息开始对话</div>
          </div>
        </div>
      ) : (
        conv.messages.map((m) => (
          <MessageBubble
            key={m.id}
            message={m}
            isUser={m.role === 'user'}
            onEdit={(id, content) => updateMessage(conv.id, id, { content })}
          />
        ))
      )}
    </div>
  );
}