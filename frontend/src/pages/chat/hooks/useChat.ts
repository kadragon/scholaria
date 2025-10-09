import { useState, useCallback, useRef } from "react";
import { API_BASE_URL, getAuthHeaders } from "../../../lib/apiConfig";
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
  historyId?: number;
  feedbackScore?: number;
  feedbackComment?: string | null;
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
  updateMessageFeedback: (historyId: number, score: number, comment: string | null) => void;
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

      const questionText = content.trim();
      const userMessage: Message = {
        id: `user-${Date.now()}`,
        role: "user",
        content: questionText,
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

      const updateAssistantMessage = (
        updater: (message: Message) => Message,
      ) => {
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMessageId ? updater(msg) : msg,
          ),
        );
      };

      const persistHistory = async (finalAnswer: string) => {
        if (!topicId) return;
        try {
          const response = await apiClient.post("/history", {
            topic_id: topicId,
            question: questionText,
            answer: finalAnswer,
            session_id: sessionId,
          });
          const record = response.data;
          updateAssistantMessage((msg) => ({
            ...msg,
            historyId: record.id,
            feedbackScore: record.feedback_score,
            feedbackComment: record.feedback_comment,
          }));
        } catch (error) {
          const err =
            error instanceof Error ? error : new Error(String(error));
          console.error("Failed to persist history:", err);
          onError?.(err);
        }
      };

      try {
        const response = await fetch(`${API_BASE_URL}/rag/stream`, {
          method: "POST",
          headers: getAuthHeaders(),
          body: JSON.stringify({
            topic_id: topicId,
            question: questionText,
            session_id: sessionId,
          }),
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        if (!response.body) {
          throw new Error("스트림을 읽을 수 없습니다");
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split("\n");

          for (const line of lines) {
            if (!line.startsWith("data: ")) continue;

            const data = line.slice(6).trim();
            if (!data) continue;

            let event;
            try {
              event = JSON.parse(data);
            } catch (parseError) {
              console.error("SSE 파싱 오류:", parseError);
              continue;
            }

            if (event.type === "answer_chunk") {
              currentAssistantMessageRef.current += event.content;
              updateAssistantMessage((msg) => ({
                ...msg,
                content: currentAssistantMessageRef.current,
              }));
            } else if (event.type === "citations") {
              currentCitationsRef.current = event.citations;
            } else if (event.type === "done") {
              updateAssistantMessage((msg) => ({
                ...msg,
                citations: currentCitationsRef.current,
              }));
              const finalAnswer = currentAssistantMessageRef.current;
              await persistHistory(finalAnswer);
              break;
            } else if (event.type === "error") {
              throw new Error(event.message || "스트리밍 중 오류 발생");
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

  const updateMessageFeedback = useCallback(
    (historyId: number, score: number, comment: string | null) => {
      setMessages((prev) =>
        prev.map((msg) =>
          msg.historyId === historyId
            ? { ...msg, feedbackScore: score, feedbackComment: comment }
            : msg,
        ),
      );
    },
    [],
  );

  return {
    messages,
    isStreaming,
    sendMessage,
    clearMessages,
    updateMessageFeedback,
  };
};
