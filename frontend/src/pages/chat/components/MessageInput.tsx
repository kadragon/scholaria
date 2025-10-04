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
    <div className="border-t-2 border-secondary-200 bg-white p-6 shadow-lg">
      <div className="max-w-4xl mx-auto">
        <div className="relative">
          <textarea
            className="w-full border-2 border-secondary-300 rounded-xl p-4 pr-24 resize-none focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:bg-secondary-50 disabled:text-secondary-400 transition-all shadow-sm"
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
          <button
            className="absolute bottom-3 right-3 flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-lg hover:from-primary-700 hover:to-primary-800 disabled:from-secondary-400 disabled:to-secondary-500 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg active:scale-95"
            onClick={handleSend}
            disabled={disabled || !input.trim() || isStreaming}
          >
            <Send className="h-4 w-4" />
            <span className="font-medium">전송</span>
          </button>
        </div>
        <div className="flex justify-between items-center mt-3 px-1">
          <span className="text-xs text-secondary-500 font-medium">
            {input.length} / 2000자
          </span>
          <span className="text-xs text-secondary-400">
            Shift + Enter로 줄바꿈
          </span>
        </div>
      </div>
    </div>
  );
};
