import React, { useState } from 'react';
import clsx from 'clsx';
import { Copy, Edit2 } from 'lucide-react';
import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import type { Message } from '../types/chat';

type Props = {
  isUser?: boolean;
  message: Message;
  onCopy?: (text: string) => void;
  onEdit?: (id: string, newContent: string) => void;
};

export default function MessageBubble({ isUser, message, onCopy, onEdit }: Props) {
  const [editing, setEditing] = useState(false);
  const [value, setValue] = useState(message.content);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      onCopy?.(message.content);
    } catch (err) {
      console.error('Failed to copy text:', err);
    }
  };

  const handleSave = () => {
    setEditing(false);
    onEdit?.(message.id, value);
  };

  const handleCancel = () => {
    setEditing(false);
    setValue(message.content);
  };

  // ChatGPT-style message bubble classes
  const containerCls = clsx(
    'w-full flex',
    isUser ? 'justify-end' : 'justify-start'
  );

  const bubbleCls = clsx(
    'max-w-[85%] rounded-2xl text-sm leading-relaxed break-words relative group',
    isUser 
      ? 'bg-sky-100 dark:bg-sky-900 text-gray-800 dark:text-gray-200 py-2 px-3' 
      : 'text-gray-800 dark:text-gray-200 py-2 px-3'
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      className={containerCls}
    >
      {!isUser && (
        <div className="w-8 h-8 rounded-md bg-gray-200 dark:bg-gray-700 mr-3 flex items-center justify-center text-gray-600 dark:text-gray-300 text-sm font-medium flex-shrink-0">
          AI
        </div>
      )}

      <div className={bubbleCls}>
        {!editing ? (
          <>
            <div className="prose prose-sm max-w-full dark:prose-invert">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>

            {/* Hover actions - ChatGPT style */}
            <div className="absolute -top-2 right-0 opacity-0 group-hover:opacity-100 transition-opacity">
              <div className="flex gap-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-md shadow-sm p-1">
                <button 
                  onClick={handleCopy} 
                  aria-label="复制"
                  className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                >
                  <Copy size={14} className="text-gray-600 dark:text-gray-400" />
                </button>
                <button 
                  onClick={() => setEditing(true)} 
                  aria-label="编辑"
                  className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                >
                  <Edit2 size={14} className="text-gray-600 dark:text-gray-400" />
                </button>
              </div>
            </div>
          </>
        ) : (
          <div className="w-full">
            <textarea
              className="w-full bg-transparent outline-none resize-none"
              rows={4}
              value={value}
              onChange={(e) => setValue(e.target.value)}
              autoFocus
            />
            <div className="flex gap-2 justify-end mt-2">
              <button 
                className="px-3 py-1 rounded-md bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-500 text-sm transition-colors" 
                onClick={handleCancel}
              >
                取消
              </button>
              <button 
                className="px-3 py-1 rounded-md bg-sky-600 text-white hover:bg-sky-700 text-sm transition-colors" 
                onClick={handleSave}
              >
                保存
              </button>
            </div>
          </div>
        )}
      </div>

      {isUser && <div className="w-8 flex-shrink-0" />}
    </motion.div>
  );
}