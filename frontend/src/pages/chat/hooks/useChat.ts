import { useState, useCallback, useRef } from "react";
import { apiClient } from "../../../lib/apiClient";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: Array<{
    context_item_id: number;
    title: string;
    content: string;
    score: number;
    context_type: string;
  }>;
  timestamp: Date;
}

interface UseChatOptions {
  topicId: number | null;
  sessionId: string;
  onError?: (error: Error) => void;
}

interface UseChatReturn {
  messages: Message[];
  isStreaming: boolean;
  sendMessage: (content: string) => Promise<void>;
  clearMessages: () => void;
}

export const useChat = ({
  topicId,
  sessionId,
  onError,
}: UseChatOptions): UseChatReturn => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const currentAssistantMessageRef = useRef<string>("");
  const currentCitationsRef = useRef<Message["citations"]>();

  const sendMessage = useCallback(
    async (content: string) => {
      if (!topicId || !content.trim() || isStreaming) return;

      const userMessage: Message = {
        id: `user-${Date.now()}`,
        role: "user",
        content: content.trim(),
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsStreaming(true);

      currentAssistantMessageRef.current = "";
      currentCitationsRef.current = undefined;

      const assistantMessageId = `assistant-${Date.now()}`;
      setMessages((prev) => [
        ...prev,
        {
          id: assistantMessageId,
          role: "assistant",
          content: "",
          timestamp: new Date(),
        },
      ]);

      try {
        const response = await apiClient.post("/rag/stream", {
          topic_id: topicId,
          question: content.trim(),
          session_id: sessionId,
        }, {
          responseType: "stream",
        });

        const reader = response.data?.getReader();
        const decoder = new TextDecoder();

        if (!reader) {
          throw new Error("스트림을 읽을 수 없습니다");
        }

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split("\n");

          for (const line of lines) {
            if (!line.startsWith("data: ")) continue;

            const data = line.slice(6).trim();
            if (!data) continue;

            try {
              const event = JSON.parse(data);

              if (event.type === "answer_chunk") {
                currentAssistantMessageRef.current += event.content;
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === assistantMessageId
                      ? {
                          ...msg,
                          content: currentAssistantMessageRef.current,
                        }
                      : msg
                  )
                );
              } else if (event.type === "citations") {
                currentCitationsRef.current = event.citations;
              } else if (event.type === "done") {
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === assistantMessageId
                      ? {
                          ...msg,
                          citations: currentCitationsRef.current,
                        }
                      : msg
                  )
                );
                break;
              } else if (event.type === "error") {
                throw new Error(event.message || "스트리밍 중 오류 발생");
              }
            } catch (parseError) {
              console.error("SSE 파싱 오류:", parseError);
            }
          }
        }
      } catch (error) {
        const err = error instanceof Error ? error : new Error(String(error));
        onError?.(err);
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMessageId
              ? {
                  ...msg,
                  content:
                    currentAssistantMessageRef.current ||
                    "답변 생성 중 오류가 발생했습니다",
                }
              : msg
          )
        );
      } finally {
        setIsStreaming(false);
      }
    },
    [topicId, sessionId, isStreaming, onError]
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return {
    messages,
    isStreaming,
    sendMessage,
    clearMessages,
  };
};
