import { useState, type KeyboardEvent } from "react";
import { Send } from "lucide-react";

interface MessageInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  isStreaming?: boolean;
}

export const MessageInput = ({
  onSend,
  disabled = false,
  isStreaming = false,
}: MessageInputProps) => {
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (!input.trim() || disabled || isStreaming) return;
    onSend(input);
    setInput("");
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t bg-white p-4">
      <div className="max-w-3xl mx-auto">
        <textarea
          className="w-full border rounded-lg p-3 resize-none focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:bg-secondary-50"
          placeholder={
            disabled
              ? "토픽을 선택하여 대화를 시작하세요"
              : "질문을 입력하세요... (Enter: 전송, Shift+Enter: 줄바꿈)"
          }
          rows={3}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled || isStreaming}
        />
        <div className="flex justify-between items-center mt-2">
          <span className="text-xs text-secondary-500">
            {input.length} / 2000자
          </span>
          <button
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            onClick={handleSend}
            disabled={disabled || !input.trim() || isStreaming}
          >
            <Send className="h-4 w-4" />
            전송
          </button>
        </div>
      </div>
    </div>
  );
};
