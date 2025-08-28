import { useEffect } from 'react';
import { useAgentStore } from './store/agentStore';
import ChatPanel from './modules/chat/ChatPanel';
import Sidebar from './components/Sidebar';
import ThemeToggle from './components/ui/ThemeToggle';

function App() {
  const initializeStore = useAgentStore((state) => state.initialize);

  useEffect(() => {
    initializeStore();
  }, [initializeStore]);

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <aside className="w-60 hidden md:flex flex-col">
        <Sidebar />
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col">
        <div className="flex justify-end p-4">
          <ThemeToggle />
        </div>
        <ChatPanel />
      </main>
    </div>
  );
}

export default App;