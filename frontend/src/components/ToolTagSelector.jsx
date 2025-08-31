import React, { useEffect, useState } from 'react';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { useAgentStore } from '../store/agentStore';
import { X, Tag, Filter } from 'lucide-react';
import { cn } from '../utils/cn';

/**
 * 工具标签选择器组件
 * 允许用户选择和过滤要使用的工具
 */
const ToolTagSelector = () => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  
  const toolTags = useAgentStore((state) => state.toolTags);
  const availableTools = useAgentStore((state) => state.availableTools);
  const addToolTag = useAgentStore((state) => state.addToolTag);
  const removeToolTag = useAgentStore((state) => state.removeToolTag);
  const clearToolTags = useAgentStore((state) => state.clearToolTags);
  const fetchAvailableTools = useAgentStore((state) => state.fetchAvailableTools);
  const isLoading = useAgentStore((state) => state.isLoading);

  // 获取可用工具列表
  useEffect(() => {
    console.log('[DEBUG] Fetching available tools...');
    fetchAvailableTools();
    
    // 每30秒自动刷新一次工具列表
    const interval = setInterval(() => {
      console.log('[DEBUG] Auto-refreshing tools list...');
      fetchAvailableTools();
    }, 30000);
    
    return () => clearInterval(interval);
  }, [fetchAvailableTools]);
  
  // 调试：打印 availableTools 的值和类型
  useEffect(() => {
    console.log('availableTools:', availableTools);
    console.log('availableTools type:', typeof availableTools);
    console.log('Is array:', Array.isArray(availableTools));
    console.log('Length:', availableTools ? availableTools.length : 0);
    if (Array.isArray(availableTools) && availableTools.length > 0) {
      console.log('Sample tool:', availableTools[0]);
    }
  }, [availableTools]);

  // 从可用工具中提取所有唯一标签
  const extractAllTags = () => {
    // 更健壮的处理，确保 availableTools 是数组
    console.log('[DEBUG] Extracting tags from:', availableTools);
    
    // Handle various edge cases
    if (!availableTools) return [];
    if (availableTools.response) return []; // Handle error case
    
    const tools = Array.isArray(availableTools) ? availableTools : [];
    if (tools.length === 0) return [];
    
    const allTags = new Set();
    tools.forEach(tool => {
      if (tool && tool.tags && Array.isArray(tool.tags)) {
        tool.tags.forEach(tag => allTags.add(tag));
      }
    });
    
    const sortedTags = Array.from(allTags).sort();
    console.log('[DEBUG] Extracted tags:', sortedTags);
    return sortedTags;
  };

  // 所有可用的标签
  const allTags = extractAllTags();
  
  // 过滤后的标签（基于搜索查询）
  const filteredTags = searchQuery 
    ? allTags.filter(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
    : allTags;

  // 处理标签切换
  const toggleTag = (tag) => {
    console.log(`[DEBUG] Toggling tag: ${tag}`);
    if (toolTags.includes(tag)) {
      console.log(`[DEBUG] Removing tag: ${tag}`);
      removeToolTag(tag);
    } else {
      console.log(`[DEBUG] Adding tag: ${tag}`);
      addToolTag(tag);
    }
  };
  
  // 标签是否已选中
  const isTagSelected = (tag) => {
    return toolTags.includes(tag);
  };

  // 切换展开/折叠状态
  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
    if (!isExpanded) {
      setSearchQuery('');
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-2">
        <label className="text-sm text-gray-700 dark:text-gray-300 mb-1">工具标签过滤:</label>
        <Button 
          variant={isExpanded ? "secondary" : "outline"}
          size="sm" 
          onClick={toggleExpanded}
          disabled={isLoading}
          className={`text-xs h-7 px-2 flex items-center gap-1`}
        >
          {isExpanded 
            ? <>
                <span>收起</span>
                <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m18 15-6-6-6 6"/></svg>
              </>
            : <>
                <span>选择标签</span>
                <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m6 9 6 6 6-6"/></svg>
              </>
          }
        </Button>
      </div>

      {/* 已选择的标签 */}
      <div className="border border-gray-200 dark:border-gray-700 rounded-md p-2 bg-gray-50 dark:bg-gray-800 mb-2">
        <div className="flex flex-wrap gap-1.5">
          {toolTags.length > 0 ? (
            <>
              {toolTags.map(tag => (
                <Badge 
                  key={tag} 
                  variant="secondary"
                  className={cn(
                    "flex items-center gap-1 py-1 px-2 text-xs cursor-pointer transition-colors",
                    "bg-blue-100 text-blue-800 hover:bg-blue-200 dark:bg-blue-900 dark:text-blue-100 dark:hover:bg-blue-800"
                  )}
                  onClick={() => removeToolTag(tag)}
                  title="点击移除此标签"
                >
                  <span>{tag}</span>
                  <X size={12} className="text-blue-500 dark:text-blue-300" />
                </Badge>
              ))}
              <Button 
                variant="outline" 
                size="sm" 
                onClick={clearToolTags}
                disabled={isLoading || toolTags.length === 0}
                className={cn(
                  "text-xs h-6 px-2 ml-1",
                  "text-red-500 hover:text-red-600 hover:bg-red-50 border-red-200",
                  "dark:text-red-400 dark:border-red-900 dark:hover:bg-red-950"
                )}
              >
                清除
              </Button>
            </>
          ) : (
            <div className="text-xs text-gray-500 dark:text-gray-400 py-1 italic">
              未选择标签，将使用所有工具
            </div>
          )}
        </div>
      </div>

      {/* 展开时显示搜索和标签选择 */}
      {isExpanded && (
        <div className="mt-2 p-3 border border-gray-200 dark:border-gray-700 rounded-md bg-gray-50 dark:bg-gray-800 shadow-sm">
          {/* 搜索输入框 */}
          <div className="mb-2">
            <input
              type="text"
              placeholder="搜索标签..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className={cn(
                "w-full px-3 py-1.5 text-sm rounded-md",
                "border border-gray-300 focus:outline-none focus:ring-1 focus:ring-blue-500",
                "dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:focus:ring-blue-400"
              )}
              disabled={isLoading}
            />
          </div>
          
          {/* 标签列表 */}
          <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto p-2 border border-gray-200 dark:border-gray-700 rounded-md bg-white dark:bg-gray-900">
            {filteredTags.length > 0 ? (
              filteredTags.map(tag => (
                <Badge 
                  key={tag} 
                  variant={isTagSelected(tag) ? "default" : "outline"}
                  className={`cursor-pointer transition-colors py-1 px-2 text-xs ${isTagSelected(tag) 
                    ? 'bg-blue-500 hover:bg-blue-600 text-white dark:bg-blue-600 dark:hover:bg-blue-700' 
                    : 'bg-white hover:bg-gray-100 border-gray-300 dark:bg-gray-800 dark:border-gray-600 dark:hover:bg-gray-700 dark:text-gray-200'}`}
                  onClick={() => toggleTag(tag)}
                  disabled={isLoading}
                >
                  <span className="flex items-center gap-1.5">
                    {isTagSelected(tag) 
                      ? <span className="inline-block w-2 h-2 bg-white dark:bg-blue-200 rounded-full"></span>
                      : <Tag size={10} />}
                    {tag}
                  </span>
                </Badge>
              ))
            ) : (
              <div className="text-xs text-gray-500 dark:text-gray-400 w-full text-center py-3">
                {searchQuery ? "没有找到匹配的标签" : "没有可用的工具标签"}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ToolTagSelector;