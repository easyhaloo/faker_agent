import { useChatStore } from '../../store/chatStore';
import { sendMessage } from '../../services/chatService';
import MessageList from '../../components/MessageList';
import ChatInput from '../../components/ChatInput';

const ChatPanel = () => {
  const { sessions, currentSessionId, loading, addMessageToSession, setLoading } = useChatStore();
  
  // 获取当前会话的消息
  const currentSession = sessions.find(session => session.id === currentSessionId);
  const messages = currentSession?.messages || [];

  const handleSend = async (content: string) => {
    if (!currentSessionId) return;
    
    // 添加用户消息到当前会话
    const newUserMessage = {
      id: Date.now().toString(),
      sender: "user" as const,
      content,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    addMessageToSession(currentSessionId, newUserMessage);
    setLoading(true);

    try {
      // 调用实际的API服务
      const response = await sendMessage(content);
      
      const aiResponse = {
        id: `${Date.now()}-ai`,
        sender: "ai" as const,
        content: response.reply,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      
      addMessageToSession(currentSessionId, aiResponse);
    } catch (error) {
      const errorMessage = {
        id: `${Date.now()}-error`,
        sender: "ai" as const,
        content: "Sorry, I encountered an error processing your request.",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      
      addMessageToSession(currentSessionId, errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <MessageList messages={messages} loading={loading} />
      {loading && (
        <div className="px-4 pb-4">
          <div className="flex justify-start">
            <div className="bg-muted text-foreground rounded-2xl rounded-tl-none px-4 py-2">
              <div className="flex space-x-2">
                <div className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce"></div>
                <div className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce delay-75"></div>
                <div className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce delay-150"></div>
              </div>
            </div>
          </div>
        </div>
      )}
      <ChatInput onSend={handleSend} disabled={loading} />
    </div>
  );
};

export default ChatPanel;