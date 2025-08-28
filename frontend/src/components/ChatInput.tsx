import { useState, KeyboardEvent, useRef } from 'react';
import { Button } from '../components/ui/button';
import { Textarea } from '../components/ui/textarea';
import { Send } from 'lucide-react';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

const ChatInput = ({ onSend, disabled }: ChatInputProps) => {
  const [inputValue, setInputValue] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = () => {
    if (!inputValue.trim() || disabled) return;
    onSend(inputValue.trim());
    setInputValue('');
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="flex items-center gap-2 border-t p-3 bg-background">
      <div className="flex-1 relative">
        <Textarea
          ref={textareaRef}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message here..."
          className="pr-12 py-3 resize-none"
          disabled={disabled}
          rows={1}
        />
        <Button
          type="button"
          size="icon"
          className="absolute right-2 top-1/2 transform -translate-y-1/2 h-8 w-8 rounded-full"
          onClick={handleSubmit}
          disabled={!inputValue.trim() || disabled}
        >
          <Send size={16} />
          <span className="sr-only">Send</span>
        </Button>
      </div>
    </div>
  );
};

export default ChatInput;