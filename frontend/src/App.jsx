import { useState, useEffect } from 'react';
import { useAgentStore } from './store/agentStore';
import { motion, AnimatePresence } from 'framer-motion';
import EnhancedChatPanel from './components/chat/EnhancedChatPanel.jsx';
import ConversationSidebar from './components/chat/ConversationSidebar';
import ConversationManager from './components/chat/ConversationManager';
import SystemSettings from './components/ui/SystemSettings';
import { I18nProvider } from './i18n/index.jsx';

function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const initializeStore = useAgentStore((state) => state.initialize);
  const fetchAvailableTools = useAgentStore((state) => state.fetchAvailableTools);
  const fetchFilterStrategies = useAgentStore((state) => state.fetchFilterStrategies);
  
  // Sidebar state change callback
  const handleSidebarStateChange = (isOpen) => {
    setIsSidebarOpen(isOpen);
  };

  useEffect(() => {
    // Initialize stores
    initializeStore();
    
    // Fetch available tools and filter strategies
    fetchAvailableTools();
    fetchFilterStrategies();
  }, [initializeStore, fetchAvailableTools, fetchFilterStrategies]);

  return (
    <I18nProvider>
      <div className="flex h-screen overflow-hidden bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
        {/* Main content with two modes */}
        <div className="flex-1 flex flex-col max-h-full overflow-hidden">
          {/* 系统设置按钮已移至侧边栏底部 */}
          
          {/* Toggle between old and new UI */}
          <div className="flex-1 overflow-hidden">
            {/* New Conversation Manager UI */}
            <ConversationManager />
            
            {/* Old UI (commented out) */}
            {/* 
            <motion.main 
              className="flex-1 flex flex-col max-h-full"
              initial={{ marginLeft: 0 }}
              animate={{ 
                marginLeft: isSidebarOpen ? '10px' : 0,
                borderRadius: isSidebarOpen ? '12px 0 0 12px' : '0',
                boxShadow: isSidebarOpen ? '-4px 0 20px rgba(0, 0, 0, 0.05)' : 'none'
              }}
              transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            >
              <div className="flex-1 overflow-hidden">
                <EnhancedChatPanel />
              </div>
              <ConversationSidebar onStateChange={handleSidebarStateChange} />
            </motion.main>
            */}
          </div>
        </div>
      </div>
    </I18nProvider>
  );
}

export default App;