import { useEffect, useRef } from "react";
import type { Message } from "../hooks/useChat";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "../../../components/ui/collapsible";
import { ChevronDown } from "lucide-react";

interface MessageListProps {
  messages: Message[];
  isStreaming: boolean;
}

export const MessageList = ({ messages, isStreaming }: MessageListProps) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isStreaming]);

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-4">
      {messages.map((message) => (
        <div
          key={message.id}
          className={`flex ${
            message.role === "user" ? "justify-end" : "justify-start"
          }`}
        >
          <div
            className={`max-w-[70%] rounded-lg p-4 ${
              message.role === "user"
                ? "bg-primary-600 text-white"
                : "bg-white border border-secondary-200"
            }`}
          >
            <div className="whitespace-pre-wrap break-words">
              {message.content}
            </div>

            {message.role === "assistant" && message.citations && (
              <Collapsible className="mt-3">
                <CollapsibleTrigger className="flex items-center gap-2 text-sm text-secondary-600 hover:text-secondary-800">
                  <ChevronDown className="h-4 w-4" />
                  인용 출처 ({message.citations.length})
                </CollapsibleTrigger>
                <CollapsibleContent className="mt-2 space-y-2">
                  {message.citations.map((citation, idx) => (
                    <div
                      key={idx}
                      className="text-sm bg-secondary-50 p-2 rounded border border-secondary-200"
                    >
                      <div className="font-semibold text-secondary-700">
                        {citation.context_title} (청크 {citation.chunk_index})
                      </div>
                      <div className="text-secondary-600 text-xs mt-1 line-clamp-2">
                        {citation.content}
                      </div>
                      <div className="text-secondary-500 text-xs mt-1">
                        유사도: {(citation.score * 100).toFixed(1)}%
                      </div>
                    </div>
                  ))}
                </CollapsibleContent>
              </Collapsible>
            )}
          </div>
        </div>
      ))}

      {isStreaming && (
        <div className="flex justify-start">
          <div className="bg-white border border-secondary-200 rounded-lg p-4">
            <div className="flex items-center gap-2">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-secondary-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                <div className="w-2 h-2 bg-secondary-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                <div className="w-2 h-2 bg-secondary-400 rounded-full animate-bounce"></div>
              </div>
              <span className="text-sm text-secondary-600">답변 생성 중...</span>
            </div>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
};
