import { useEffect } from 'react';
import { useAgentStore } from './store/agentStore';
import EnhancedChatPanel from './components/chat/EnhancedChatPanel.jsx';
import Sidebar from './components/Sidebar';
import ThemeToggle from './components/ui/ThemeToggle';

function App() {
  const initializeStore = useAgentStore((state) => state.initialize);
  const fetchAvailableTools = useAgentStore((state) => state.fetchAvailableTools);
  const fetchFilterStrategies = useAgentStore((state) => state.fetchFilterStrategies);

  useEffect(() => {
    // 初始化Store
    initializeStore();
    
    // 获取可用工具和过滤策略
    fetchAvailableTools();
    fetchFilterStrategies();
  }, [initializeStore, fetchAvailableTools, fetchFilterStrategies]);

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
        <EnhancedChatPanel />
      </main>
    </div>
  );
}

export default App;