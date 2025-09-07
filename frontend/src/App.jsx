import React from 'react';
import Sidebar from './components/Sidebar';
import ChatWindow from './components/ChatWindow';

export default function App() {
  return (
    <div className="flex h-screen dark:text-gray-100">
      {/* Sidebar - Fixed 260px width */}
      <aside className="w-[260px] bg-gray-50 dark:bg-[#0d1117] border-r border-gray-200 dark:border-gray-800 flex flex-col">
        <Sidebar />
      </aside>

      {/* Main content area */}
      <div className="flex-1 flex flex-col">
        <ChatWindow />
      </div>
    </div>
  );
}