import { useState, useEffect } from 'react';
import { useDisplayStore } from '../../store/displayStore';
import { Settings, Monitor, Palette, Layout, Sun, Moon, MonitorSmartphone, Cpu, HardDrive, Wifi } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const SystemSettings = () => {
  const [isOpen, setIsOpen] = useState(false);
  const displaySettings = useDisplayStore((state) => state.displaySettings);
  const updateDisplaySettings = useDisplayStore((state) => state.updateDisplaySettings);
  const resetDisplaySettings = useDisplayStore((state) => state.resetDisplaySettings);
  const applyAllDisplaySettings = useDisplayStore((state) => state.applyAllDisplaySettings);

  useEffect(() => {
    // 组件挂载时应用所有显示设置
    applyAllDisplaySettings();
  }, []);

  const toggleSettings = () => {
    setIsOpen(!isOpen);
  };

  const handleSettingChange = (key, value) => {
    const newSettings = {
      ...displaySettings,
      [key]: value
    };
    
    updateDisplaySettings({ [key]: value });
    
    // 应用设置到DOM
    setTimeout(() => {
      applyAllDisplaySettings();
    }, 0);
  };

  // 抽屉动画变体
  const drawerVariants = {
    closed: { x: "100%", opacity: 0 },
    open: { x: 0, opacity: 1 }
  };

  return (
    <div className="relative">
      <button
        onClick={toggleSettings}
        className="p-2 rounded-lg bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors flex items-center gap-2"
        aria-label="系统设置"
      >
        <Settings size={16} />
        <span className="hidden sm:inline text-sm">系统设置</span>
      </button>

      <AnimatePresence>
        {isOpen && (
          <>
            {/* 背景遮罩 */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="fixed inset-0 bg-black bg-opacity-50 z-40"
              onClick={toggleSettings}
            />
            
            {/* 从右侧滑入的抽屉 */}
            <motion.div
              initial="closed"
              animate="open"
              exit="closed"
              variants={drawerVariants}
              transition={{ 
                type: "spring", 
                damping: 25, 
                stiffness: 300,
                mass: 0.8
              }}
              className="fixed top-0 right-0 h-full w-80 bg-white dark:bg-gray-800 shadow-xl z-50 overflow-y-auto"
            >
              <div className="p-6">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-bold text-gray-800 dark:text-gray-200">系统设置</h2>
                  <button
                    onClick={toggleSettings}
                    className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500 dark:text-gray-400"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                  </button>
                </div>

                <div className="space-y-8">
                  {/* 外观设置 */}
                  <div>
                    <h3 className="font-semibold text-lg text-gray-800 dark:text-gray-200 mb-4 flex items-center gap-2">
                      <MonitorSmartphone size={18} />
                      外观主题
                    </h3>
                    
                    <div className="grid grid-cols-3 gap-2">
                      {[
                        { value: 'light', label: '浅色', icon: Sun },
                        { value: 'dark', label: '深色', icon: Moon },
                        { value: 'system', label: '系统', icon: Monitor }
                      ].map(({ value, label, icon: Icon }) => (
                        <button
                          key={value}
                          onClick={() => handleSettingChange('theme', value)}
                          className={`py-3 px-2 rounded-md text-sm transition-colors flex flex-col items-center gap-1 ${
                            displaySettings.theme === value
                              ? 'bg-blue-500 text-white'
                              : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600'
                          }`}
                        >
                          <Icon size={16} />
                          <span>{label}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                  
                  {/* 显示设置 */}
                  <div>
                    <h3 className="font-semibold text-lg text-gray-800 dark:text-gray-200 mb-4 flex items-center gap-2">
                      <Monitor size={18} />
                      显示设置
                    </h3>
                    
                    <div className="space-y-6">
                      {/* 字体大小设置 */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-2">
                          <Palette size={14} />
                          字体大小
                        </label>
                        <div className="grid grid-cols-3 gap-2">
                          {['small', 'medium', 'large'].map((size) => (
                            <button
                              key={size}
                              onClick={() => handleSettingChange('fontSize', size)}
                              className={`py-2 px-3 rounded-md text-sm transition-colors ${
                                displaySettings.fontSize === size
                                  ? 'bg-blue-500 text-white'
                                  : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600'
                              }`}
                            >
                              {size === 'small' ? '小' : size === 'medium' ? '中' : '大'}
                            </button>
                          ))}
                        </div>
                      </div>
                      
                      {/* 布局设置 */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-2">
                          <Layout size={14} />
                          布局模式
                        </label>
                        <div className="grid grid-cols-2 gap-2">
                          {['comfortable', 'compact'].map((layout) => (
                            <button
                              key={layout}
                              onClick={() => handleSettingChange('layout', layout)}
                              className={`py-2 px-3 rounded-md text-sm transition-colors ${
                                displaySettings.layout === layout
                                  ? 'bg-blue-500 text-white'
                                  : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600'
                              }`}
                            >
                              {layout === 'comfortable' ? '舒适' : '紧凑'}
                            </button>
                          ))}
                        </div>
                      </div>
                      
                      {/* 动画效果 */}
                      <div className="flex items-center justify-between">
                        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">动画效果</label>
                        <button
                          onClick={() => handleSettingChange('animation', !displaySettings.animation)}
                          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none ${
                            displaySettings.animation ? 'bg-blue-500' : 'bg-gray-300 dark:bg-gray-600'
                          }`}
                        >
                          <span
                            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                              displaySettings.animation ? 'translate-x-6' : 'translate-x-1'
                            }`}
                          />
                        </button>
                      </div>
                      
                      {/* 紧凑模式 */}
                      <div className="flex items-center justify-between">
                        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">紧凑模式</label>
                        <button
                          onClick={() => handleSettingChange('compactMode', !displaySettings.compactMode)}
                          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none ${
                            displaySettings.compactMode ? 'bg-blue-500' : 'bg-gray-300 dark:bg-gray-600'
                          }`}
                        >
                          <span
                            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                              displaySettings.compactMode ? 'translate-x-6' : 'translate-x-1'
                            }`}
                          />
                        </button>
                      </div>
                    </div>
                  </div>
                  
                  {/* 系统信息 */}
                  <div>
                    <h3 className="font-semibold text-lg text-gray-800 dark:text-gray-200 mb-4 flex items-center gap-2">
                      <Cpu size={18} />
                      系统信息
                    </h3>
                    
                    <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-300">版本</span>
                        <span className="font-medium">v1.0.0</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-300">环境</span>
                        <span className="font-medium">开发版</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-300">缓存</span>
                        <span className="font-medium">已清理</span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
                  <button
                    onClick={() => {
                      resetDisplaySettings();
                      setTimeout(() => {
                        applyAllDisplaySettings();
                      }, 0);
                    }}
                    className="w-full py-2 px-4 text-sm text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-gray-100 rounded-md bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                  >
                    恢复默认设置
                  </button>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};

export default SystemSettings;