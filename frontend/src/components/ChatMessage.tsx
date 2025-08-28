import { motion } from 'framer-motion';
import { Bot, User } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface ChatMessageProps {
  sender: "user" | "ai";
  content: string;
  timestamp: string;
}

const ChatMessage = ({ sender, content, timestamp }: ChatMessageProps) => {
  return (
    <motion.div 
      className={`flex ${sender === "user" ? "justify-end" : "justify-start"} mb-3`}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className={`px-4 py-2 rounded-2xl text-sm shadow-sm max-w-[70%]
        ${sender === "user" ? "bg-primary text-primary-foreground" : "bg-muted text-foreground"}
      `}>
        <div className="flex items-start gap-2">
          <div className={`mt-0.5 ${sender === "user" ? "text-primary-foreground" : "text-muted-foreground"}`}>
            {sender === "user" ? <User size={16} /> : <Bot size={16} />}
          </div>
          <div className="flex-1">
            <div className="prose prose-sm dark:prose-invert max-w-none">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {content}
              </ReactMarkdown>
            </div>
            <div className={`text-xs mt-1 ${sender === "user" ? "text-primary-foreground/80" : "text-muted-foreground"}`}>
              {timestamp}
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default ChatMessage;