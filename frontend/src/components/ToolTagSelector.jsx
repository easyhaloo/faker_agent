import React, { useEffect, useState } from 'react';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { useAgentStore } from '../store/agentStore';
import { X, Tag, Filter } from 'lucide-react';

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
    fetchAvailableTools();
  }, [fetchAvailableTools]);
  
  // 调试：打印 availableTools 的值和类型
  useEffect(() => {
    console.log('availableTools:', availableTools);
    console.log('availableTools type:', typeof availableTools);
    console.log('Is array:', Array.isArray(availableTools));
  }, [availableTools]);

  // 从可用工具中提取所有唯一标签
  const extractAllTags = () => {
    // 确保 availableTools 是数组
    const tools = Array.isArray(availableTools) ? availableTools : [];
    
    if (tools.length === 0) return [];
    
    const allTags = new Set();
    tools.forEach(tool => {
      if (tool && tool.tags && Array.isArray(tool.tags)) {
        tool.tags.forEach(tag => allTags.add(tag));
      }
    });
    
    return Array.from(allTags).sort();
  };

  // 所有可用的标签
  const allTags = extractAllTags();
  
  // 过滤后的标签（基于搜索查询）
  const filteredTags = searchQuery 
    ? allTags.filter(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
    : allTags;

  // 处理标签切换
  const toggleTag = (tag) => {
    if (toolTags.includes(tag)) {
      removeToolTag(tag);
    } else {
      addToolTag(tag);
    }
  };

  // 切换展开/折叠状态
  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
    if (!isExpanded) {
      setSearchQuery('');
    }
  };

  return (
    <div className="mb-4">
      <div className="flex justify-between items-center mb-2">
        <div className="flex items-center">
          <Filter size={16} className="mr-1 text-gray-500" />
          <h3 className="text-sm font-medium text-gray-700">工具过滤</h3>
        </div>
        <Button 
          variant="ghost" 
          size="sm" 
          onClick={toggleExpanded}
          disabled={isLoading}
          className="text-xs h-7 px-2"
        >
          {isExpanded ? '收起' : '展开'}
        </Button>
      </div>

      {/* 已选择的标签 */}
      <div className="flex flex-wrap gap-2 mb-2">
        {toolTags.length > 0 ? (
          <>
            {toolTags.map(tag => (
              <Badge 
                key={tag} 
                variant="secondary"
                className="flex items-center gap-1 py-1 px-2 cursor-pointer"
                onClick={() => removeToolTag(tag)}
                title="点击移除此标签"
              >
                <span>{tag}</span>
                <X size={12} className="text-gray-500" />
              </Badge>
            ))}
            <Button 
              variant="outline" 
              size="sm" 
              onClick={clearToolTags}
              disabled={isLoading || toolTags.length === 0}
              className="text-xs h-6 px-2"
            >
              清除全部
            </Button>
          </>
        ) : (
          <div className="text-xs text-gray-500 italic">
            未选择任何工具标签，将使用所有可用工具
          </div>
        )}
      </div>

      {/* 展开时显示搜索和标签选择 */}
      {isExpanded && (
        <div className="mt-3 p-3 border border-gray-200 rounded-md bg-gray-50">
          {/* 搜索输入框 */}
          <div className="mb-3">
            <input
              type="text"
              placeholder="搜索标签..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-3 py-1 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            />
          </div>
          
          {/* 标签列表 */}
          <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto">
            {filteredTags.length > 0 ? (
              filteredTags.map(tag => (
                <Badge 
                  key={tag} 
                  variant={toolTags.includes(tag) ? "default" : "outline"}
                  className="cursor-pointer"
                  onClick={() => toggleTag(tag)}
                  disabled={isLoading}
                >
                  <span className="flex items-center gap-1">
                    <Tag size={10} />
                    {tag}
                  </span>
                </Badge>
              ))
            ) : (
              <div className="text-xs text-gray-500 w-full text-center py-2">
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