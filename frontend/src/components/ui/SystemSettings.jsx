import { useState, useEffect } from 'react';
import { useDisplayStore } from '../../store/displayStore';
import { useAgentStore } from '../../store/agentStore';
import { Settings, Monitor, Palette, Layout, Sun, Moon, MonitorSmartphone, Cpu, Bot, Network, Radio, Wifi, Tag, X, Globe } from 'lucide-react';
import ProtocolSelector from '../ProtocolSelector';
import ToolTagSelector from '../ToolTagSelector';
import { cn } from '../../utils/cn';
import { useI18n, LANGUAGES } from '../../i18n/index.jsx';
// Import motion for animations
import { motion } from 'framer-motion';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../ui/tabs';

/**
 * 系统设置组件
 * 根据要求重新设计为模态窗口风格，类似 ChatGPT 设置界面
 */
const SystemSettings = () => {
  const { t, language, changeLanguage } = useI18n();
  const [isOpen, setIsOpen] = useState(false);
  const displaySettings = useDisplayStore((state) => state.displaySettings);
  const updateDisplaySettings = useDisplayStore((state) => state.updateDisplaySettings);
  const resetDisplaySettings = useDisplayStore((state) => state.resetDisplaySettings);
  const applyAllDisplaySettings = useDisplayStore((state) => state.applyAllDisplaySettings);

  useEffect(() => {
    // 组件挂载时应用所有显示设置
    applyAllDisplaySettings();
  }, [applyAllDisplaySettings]);

  const handleSettingChange = (key, value) => {
    updateDisplaySettings({ [key]: value });
    
    // 应用设置到DOM
    setTimeout(() => {
      applyAllDisplaySettings();
    }, 0);
  };

  return (
    <div>
      {/* Settings Entry Button - 文字和图标一起显示 */}
      <button
        onClick={() => setIsOpen(true)}
        className="w-full py-3 px-4 text-left hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors flex items-center"
        aria-label={t('settings.systemSettings')}
      >
        <Settings size={20} className="text-gray-600 dark:text-gray-300 mr-3" />
        <span className="text-gray-700 dark:text-gray-300">{t('settings.systemSettings')}</span>
      </button>
      
      {/* Settings Panel - 集成在左侧对话列表下方 */}
      {isOpen && (
        <>
          {/* Overlay */}
          <div 
            className="fixed inset-0 bg-black/50 z-40"
            onClick={() => setIsOpen(false)}
          />
          
          {/* Modal dialog */}
          <motion.div 
            className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 w-[480px] max-h-[85vh] bg-white dark:bg-gray-900 rounded-2xl shadow-lg overflow-y-auto"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
          >
          <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
            <h2 className="font-medium text-lg">{t('settings.systemSettings')}</h2>
            <button 
              onClick={() => setIsOpen(false)}
              className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              <X size={18} />
            </button>
          </div>
          
          <div className="p-4">
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">{t('settings.manageSystemSettings')}</p>
        
        <Tabs defaultValue="appearance" className="mt-6">
          <TabsList className="mb-6">
            <TabsTrigger value="appearance" className="flex items-center gap-2">
              <MonitorSmartphone size={16} />
              {t('settings.appearance')}
            </TabsTrigger>
            <TabsTrigger value="display" className="flex items-center gap-2">
              <Monitor size={16} />
              {t('settings.displaySettings')}
            </TabsTrigger>
            <TabsTrigger value="agent" className="flex items-center gap-2">
              <Bot size={16} />
              {t('settings.agentCommunication')}
            </TabsTrigger>
            <TabsTrigger value="system" className="flex items-center gap-2">
              <Cpu size={16} />
              {t('settings.systemInfo')}
            </TabsTrigger>
          </TabsList>
          
          {/* 外观设置 */}
          <TabsContent value="appearance" className="space-y-6">
            <div>
              <h3 className="font-semibold text-lg text-gray-800 dark:text-gray-200 mb-4 flex items-center gap-2">
                <Palette size={18} />
                {t('settings.theme')}
              </h3>
              
              <div className="grid grid-cols-3 gap-3">
                {[
                  { value: 'light', label: t('settings.light'), icon: Sun },
                  { value: 'dark', label: t('settings.dark'), icon: Moon },
                  { value: 'system', label: t('settings.system'), icon: Monitor }
                ].map(({ value, label, icon: Icon }) => (
                  <button
                    key={value}
                    onClick={() => handleSettingChange('theme', value)}
                    className={cn(
                      "py-4 px-3 rounded-2xl text-sm transition-colors flex flex-col items-center gap-2",
                      displaySettings.theme === value
                        ? "bg-blue-500 text-white"
                        : "bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-700"
                    )}
                  >
                    <Icon size={20} />
                    <span>{label}</span>
                  </button>
                ))}
              </div>
            </div>
            
            {/* 语言设置 */}
            <div className="pt-6 border-t border-gray-200 dark:border-gray-700">
              <h3 className="font-semibold text-lg text-gray-800 dark:text-gray-200 mb-4 flex items-center gap-2">
                <Globe size={18} />
                {t('settings.language')}
              </h3>
              
              <div className="grid grid-cols-2 gap-3">
                {[
                  { value: LANGUAGES.EN, label: 'English' },
                  { value: LANGUAGES.ZH, label: '中文' }
                ].map(({ value, label }) => (
                  <button
                    key={value}
                    onClick={() => changeLanguage(value)}
                    className={cn(
                      "py-3 px-4 rounded-2xl text-sm transition-colors flex items-center justify-center",
                      language === value
                        ? "bg-blue-500 text-white"
                        : "bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-700"
                    )}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>
          </TabsContent>
          
          {/* 显示设置 */}
          <TabsContent value="display" className="space-y-6">
            <div>
              <h3 className="font-semibold text-lg text-gray-800 dark:text-gray-200 mb-4">
                {t('settings.fontSize')}
              </h3>
              
              <div className="grid grid-cols-3 gap-3">
                {['small', 'medium', 'large'].map((size) => (
                  <button
                    key={size}
                    onClick={() => handleSettingChange('fontSize', size)}
                    className={cn(
                      "py-3 px-4 rounded-2xl text-sm transition-colors",
                      displaySettings.fontSize === size
                        ? "bg-blue-500 text-white"
                        : "bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-700"
                    )}
                  >
                    {size === 'small' ? t('settings.small') : size === 'medium' ? t('settings.medium') : t('settings.large')}
                  </button>
                ))}
              </div>
            </div>
            
            <div className="pt-6 border-t border-gray-200 dark:border-gray-700">
              <h3 className="font-semibold text-lg text-gray-800 dark:text-gray-200 mb-4">
                {t('settings.layoutMode')}
              </h3>
              <div className="grid grid-cols-2 gap-3">
                {['comfortable', 'compact'].map((layout) => (
                  <button
                    key={layout}
                    onClick={() => handleSettingChange('layout', layout)}
                    className={cn(
                      "py-3 px-4 rounded-2xl text-sm transition-colors",
                      displaySettings.layout === layout
                        ? "bg-blue-500 text-white"
                        : "bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-700"
                    )}
                  >
                    {layout === 'comfortable' ? t('settings.comfortable') : t('settings.compact')}
                  </button>
                ))}
              </div>
            </div>
            
            {/* 切换功能 */}
            <div className="pt-6 border-t border-gray-200 dark:border-gray-700 space-y-4">
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">{t('settings.animation')}</label>
                <button
                  onClick={() => handleSettingChange('animation', !displaySettings.animation)}
                  className={cn(
                    "relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none",
                    displaySettings.animation ? "bg-blue-500" : "bg-gray-300 dark:bg-gray-600"
                  )}
                >
                  <span
                    className={cn(
                      "inline-block h-4 w-4 transform rounded-full bg-white transition-transform",
                      displaySettings.animation ? "translate-x-6" : "translate-x-1"
                    )}
                  />
                </button>
              </div>
              
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">{t('settings.compactMode')}</label>
                <button
                  onClick={() => handleSettingChange('compactMode', !displaySettings.compactMode)}
                  className={cn(
                    "relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none",
                    displaySettings.compactMode ? "bg-blue-500" : "bg-gray-300 dark:bg-gray-600"
                  )}
                >
                  <span
                    className={cn(
                      "inline-block h-4 w-4 transform rounded-full bg-white transition-transform",
                      displaySettings.compactMode ? "translate-x-6" : "translate-x-1"
                    )}
                  />
                </button>
              </div>
            </div>
          </TabsContent>
          
          {/* 智能体通信设置 */}
          <TabsContent value="agent">
            <div className="space-y-6">
              <div>
                <h3 className="font-semibold text-lg text-gray-800 dark:text-gray-200 mb-4 flex items-center gap-2">
                  <Network size={18} />
                  {t('settings.communicationProtocol')}
                </h3>
                <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                  <ProtocolSelector />
                </div>
              </div>
              
              <div className="pt-6 border-t border-gray-200 dark:border-gray-700">
                <h3 className="font-semibold text-lg text-gray-800 dark:text-gray-200 mb-4 flex items-center gap-2">
                  <Tag size={18} />
                  {t('settings.toolFiltering')}
                </h3>
                <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                  <ToolTagSelector />
                </div>
              </div>
            </div>
          </TabsContent>
          
          {/* 系统信息 */}
          <TabsContent value="system">
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-6 space-y-4">
              <div className="flex justify-between items-center pb-3 border-b border-gray-200 dark:border-gray-700">
                <span className="text-gray-600 dark:text-gray-300">{t('settings.version')}</span>
                <span className="font-medium">v1.0.0</span>
              </div>
              <div className="flex justify-between items-center py-3 border-b border-gray-200 dark:border-gray-700">
                <span className="text-gray-600 dark:text-gray-300">{t('settings.environment')}</span>
                <span className="font-medium">{t('settings.development')}</span>
              </div>
              <div className="flex justify-between items-center py-3">
                <span className="text-gray-600 dark:text-gray-300">{t('settings.cache')}</span>
                <span className="font-medium">{t('settings.cleared')}</span>
              </div>
              
              <button
                onClick={() => {
                  resetDisplaySettings();
                  setTimeout(() => {
                    applyAllDisplaySettings();
                  }, 0);
                }}
                className="mt-6 w-full py-2 px-4 text-sm text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-gray-100 rounded-md bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
              >
                {t('settings.restoreDefaults')}
              </button>
            </div>
          </TabsContent>
        </Tabs>
          </div>
        </motion.div>
        </>
      )}
    </div>
  );
};

export default SystemSettings;