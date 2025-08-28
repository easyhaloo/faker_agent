import { useEffect, useRef } from 'react';
import ChatMessage from './ChatMessage';
import MessageSkeleton from './MessageSkeleton';

interface ChatMessageProps {
  sender: "user" | "ai";
  content: string;
  timestamp: string;
}

interface MessageListProps {
  messages: ChatMessageProps[];
  loading?: boolean;
}

const MessageList = ({ messages, loading }: MessageListProps) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto p-4">
      {messages.map((message, index) => (
        <ChatMessage
          key={index}
          sender={message.sender}
          content={message.content}
          timestamp={message.timestamp}
        />
      ))}
      {loading && <MessageSkeleton />}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageList;