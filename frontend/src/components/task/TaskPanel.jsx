import { useAgentStore } from '../../store/agentStore';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Bot, Clock, CheckCircle, AlertCircle, Loader } from 'lucide-react';

const TaskPanel = () => {
  const tasks = useAgentStore((state) => state.tasks);
  const currentTaskId = useAgentStore((state) => state.currentTaskId);
  
  // 获取当前任务
  const currentTask = currentTaskId ? tasks[currentTaskId] : null;
  
  // 获取所有任务并按时间排序
  const allTasks = Object.values(tasks).sort((a, b) => 
    new Date(b.createdAt) - new Date(a.createdAt)
  );
  
  // 格式化时间
  const formatTime = (dateString) => {
    return new Date(dateString).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };
  
  // 获取任务状态标签
  const getStatusLabel = (status) => {
    switch (status) {
      case 'pending': return 'Pending';
      case 'processing': return 'Processing';
      case 'completed': return 'Completed';
      case 'failed': return 'Failed';
      default: return status;
    }
  };
  
  // 获取任务状态颜色
  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200';
      case 'processing': return 'bg-blue-100 text-blue-800 hover:bg-blue-200';
      case 'completed': return 'bg-green-100 text-green-800 hover:bg-green-200';
      case 'failed': return 'bg-red-100 text-red-800 hover:bg-red-200';
      default: return 'bg-gray-100 text-gray-800 hover:bg-gray-200';
    }
  };
  
  // 获取任务状态图标
  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending': return <Clock size={14} />;
      case 'processing': return <Loader size={14} className="animate-spin" />;
      case 'completed': return <CheckCircle size={14} />;
      case 'failed': return <AlertCircle size={14} />;
      default: return null;
    }
  };
  
  return (
    <div className="flex flex-col h-[calc(100vh-200px)]">
      <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* 当前任务详情 */}
        {currentTask ? (
          <Card className="border border-gray-200 shadow-sm">
            <CardHeader className="pb-3">
              <div className="flex justify-between items-start">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Bot className="h-5 w-5 text-blue-600" />
                  Current Task
                </CardTitle>
                <Badge className={`flex items-center gap-1 ${getStatusColor(currentTask.status)}`}>
                  {getStatusIcon(currentTask.status)}
                  {getStatusLabel(currentTask.status)}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium text-gray-500 mb-1">Query</h4>
                  <p className="text-gray-800 bg-gray-50 p-3 rounded-lg">{currentTask.query}</p>
                </div>
                
                {currentTask.result && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-500 mb-1">Result</h4>
                    <div className="text-gray-800 bg-gray-50 p-3 rounded-lg">
                      {typeof currentTask.result === 'string' 
                        ? currentTask.result 
                        : JSON.stringify(currentTask.result, null, 2)}
                    </div>
                  </div>
                )}
                
                <div className="text-xs text-gray-500 flex justify-between">
                  <span>Created: {formatTime(currentTask.createdAt)}</span>
                  <span>Updated: {formatTime(currentTask.updatedAt)}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        ) : (
          <Card className="border border-gray-200 shadow-sm text-center py-8">
            <div className="text-gray-400 mb-2 flex justify-center">
              <ClipboardIcon />
            </div>
            <h3 className="font-medium text-gray-600 mb-1">No Active Task</h3>
            <p className="text-sm text-gray-500 px-4">Tasks will appear here when you send a message</p>
          </Card>
        )}
        
        {/* 任务历史 */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-gray-800">Task History</h3>
            <Badge variant="secondary">{allTasks.length} tasks</Badge>
          </div>
          
          {allTasks.length === 0 ? (
            <Card className="border border-gray-200 shadow-sm text-center py-8">
              <div className="text-gray-400 mb-2 flex justify-center">
                <FileTextIcon />
              </div>
              <p className="text-gray-500">No tasks yet</p>
            </Card>
          ) : (
            <div className="space-y-3">
              {allTasks.map((task) => (
                <Card 
                  key={task.id} 
                  className="border border-gray-200 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
                >
                  <CardContent className="p-3">
                    <div className="flex justify-between items-start">
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium text-gray-800 truncate">
                          {task.query}
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          {formatTime(task.createdAt)}
                        </div>
                      </div>
                      <Badge className={`ml-2 flex items-center gap-1 ${getStatusColor(task.status)}`}>
                        {getStatusIcon(task.status)}
                        {getStatusLabel(task.status)}
                      </Badge>
                    </div>
                    
                    {task.result && (
                      <div className="mt-2 text-xs text-gray-600 truncate">
                        Result: {typeof task.result === 'string' 
                          ? task.result.substring(0, 100) + (task.result.length > 100 ? '...' : '')
                          : JSON.stringify(task.result).substring(0, 100)}
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </CardContent>
    </div>
  );
};

// Clipboard icon component
const ClipboardIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
  </svg>
);

// File text icon component
const FileTextIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
  </svg>
);

export default TaskPanel;