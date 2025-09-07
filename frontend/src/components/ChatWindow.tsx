import React from 'react';
import MessageList from './MessageList';
import Composer from './Composer';

export default function ChatWindow() {
  return (
    <div className="flex-1 flex flex-col h-full bg-white dark:bg-gray-900">
      {/* Message List Area - Centered with max-width */}
      <main className="flex-1 flex justify-center overflow-y-auto">
        <div className="w-full max-w-[740px] px-4 py-6">
          <MessageList />
        </div>
      </main>

      {/* Input Area - Centered with max-width */}
      <footer className="border-t border-gray-200 dark:border-gray-800 p-4 flex justify-center bg-gray-50 dark:bg-[#0d1117]">
        <div className="w-full max-w-[740px]">
          <Composer />
        </div>
      </footer>
    </div>
  );
}