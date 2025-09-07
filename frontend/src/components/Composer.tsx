import React, { useState, useEffect, useRef } from 'react';
import useChatStore from '../store/useChatStore';
import { Send } from 'lucide-react';
import { streamChat } from '../lib/stream';
import type { Message } from '../types/chat';

export default function Composer() {
  const selectedId = useChatStore((s) => s.selectedConversationId);
  const addMessage = useChatStore((s) => s.addMessage);
  const updateMessage = useChatStore((s) => s.updateMessage);
  const [text, setText] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  useEffect(() => {
    const draft = localStorage.getItem(`draft:${selectedId}`);
    setText(draft || '');
  }, [selectedId]);

  useEffect(() => {
    localStorage.setItem(`draft:${selectedId}`, text);
  }, [text, selectedId]);

  const handleSend = async () => {
    if (!text.trim() || !selectedId || isStreaming) return;
    
    const userMessage: Message = {
      id: typeof crypto !== 'undefined' && crypto.randomUUID ? crypto.randomUUID() : Date.now().toString(),
      role: 'user',
      content: text,
      createdAt: new Date().toISOString(),
    };
    
    addMessage(selectedId, userMessage);
    setText('');
    setIsStreaming(true);
    
    // Create temporary assistant message
    const assistantMessage: Message = {
      id: typeof crypto !== 'undefined' && crypto.randomUUID ? crypto.randomUUID() : (Date.now() + 1).toString(),
      role: 'assistant',
      content: '',
      createdAt: new Date().toISOString(),
    };
    
    addMessage(selectedId, assistantMessage);
    
    try {
      // Stream the response
      await streamChat('/api/chat', { 
        conversationId: selectedId, 
        message: text 
      }, (chunk) => {
        // Update the assistant message with the streamed content
        updateMessage(selectedId, assistantMessage.id, {
          content: assistantMessage.content + chunk
        });
        assistantMessage.content += chunk;
      });
    } catch (error) {
      console.error('Stream error:', error);
      updateMessage(selectedId, assistantMessage.id, {
        content: '抱歉，发生了错误。请稍后重试。'
      });
    } finally {
      setIsStreaming(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setText(e.target.value);
    
    // Auto-resize textarea
    const textarea = e.target;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
  };

  return (
    <div className="bg-gray-50 dark:bg-[#0d1117] rounded-2xl border border-gray-300 dark:border-gray-700">
      <div className="flex items-end gap-3 p-1">
        <textarea
          ref={textareaRef}
          value={text}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          disabled={isStreaming}
          className="flex-1 min-h-[44px] max-h-60 resize-none px-4 py-3 bg-white dark:bg-[#0d1117] rounded-2xl outline-none border-none focus:ring-2 focus:ring-sky-500 disabled:opacity-50 text-sm"
          placeholder={isStreaming ? "AI正在思考..." : "输入消息，按 Ctrl/Cmd+Enter 发送"}
          rows={1}
        />
        <button 
          onClick={handleSend} 
          disabled={!text.trim() || isStreaming}
          className="p-2 rounded-full bg-sky-600 text-white hover:bg-sky-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors mr-1 mb-1"
          aria-label="发送消息"
        >
          <Send size={16} />
        </button>
      </div>
    </div>
  );
}