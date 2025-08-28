import { useState } from 'react';
import { useChatStore } from '../store/chatStore';
import { Plus, Trash2 } from 'lucide-react';

const Sidebar = () => {
  const { sessions, currentSessionId, addSession, deleteSession, setCurrentSession } = useChatStore();
  const [isCreating, setIsCreating] = useState(false);
  const [newSessionName, setNewSessionName] = useState('');

  const handleCreateSession = () => {
    if (newSessionName.trim()) {
      const sessionId = addSession(newSessionName.trim());
      setCurrentSession(sessionId);
      setNewSessionName('');
      setIsCreating(false);
    }
  };

  const handleDeleteSession = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    deleteSession(id);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleCreateSession();
    } else if (e.key === 'Escape') {
      setIsCreating(false);
      setNewSessionName('');
    }
  };

  return (
    <div className="flex flex-col h-full bg-background border-r border-border">
      <div className="p-4 border-b border-border">
        <h2 className="text-lg font-bold">会话</h2>
      </div>
      
      <div className="p-2">
        <button 
          className="w-full bg-primary hover:bg-primary/90 text-primary-foreground py-2 px-4 rounded-lg flex items-center justify-center gap-2 transition-colors"
          onClick={() => setIsCreating(true)}
        >
          <Plus size={16} />
          新建会话
        </button>
      </div>
      
      {isCreating && (
        <div className="px-2 pb-2">
          <input
            type="text"
            value={newSessionName}
            onChange={(e) => setNewSessionName(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="输入会话名称"
            className="w-full px-3 py-2 border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-primary bg-background text-foreground"
            autoFocus
          />
          <div className="flex gap-2 mt-2">
            <button
              onClick={handleCreateSession}
              className="flex-1 bg-primary hover:bg-primary/90 text-primary-foreground py-1 px-3 rounded text-sm transition-colors"
            >
              创建
            </button>
            <button
              onClick={() => {
                setIsCreating(false);
                setNewSessionName('');
              }}
              className="flex-1 bg-muted hover:bg-muted/90 text-muted-foreground py-1 px-3 rounded text-sm transition-colors"
            >
              取消
            </button>
          </div>
        </div>
      )}
      
      <div className="flex-1 overflow-y-auto p-2">
        <div className="space-y-1">
          {sessions.map((session) => (
            <div
              key={session.id}
              onClick={() => setCurrentSession(session.id)}
              className={`p-3 rounded-lg cursor-pointer transition-colors flex justify-between items-center ${
                currentSessionId === session.id
                  ? 'bg-primary/10 text-primary dark:bg-primary/20'
                  : 'hover:bg-muted'
              }`}
            >
              <div className="truncate flex-1">
                <div className="font-medium truncate">{session.name}</div>
                {session.messages.length > 0 && (
                  <div className="text-sm text-muted-foreground truncate">
                    {session.messages[session.messages.length - 1].content}
                  </div>
                )}
              </div>
              {sessions.length > 1 && (
                <button
                  onClick={(e) => handleDeleteSession(session.id, e)}
                  className="ml-2 text-muted-foreground hover:text-destructive p-1 rounded hover:bg-destructive/10"
                >
                  <Trash2 size={16} />
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Sidebar;