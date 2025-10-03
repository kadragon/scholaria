import { useState, useEffect } from "react";
import { v4 as uuidv4 } from "uuid";
import { TopicSelector } from "./components/TopicSelector";
import { MessageList } from "./components/MessageList";
import { MessageInput } from "./components/MessageInput";
import { useChat } from "./hooks/useChat";

export const ChatPage = () => {
  const [selectedTopicId, setSelectedTopicId] = useState<number | null>(null);
  const [sessionId] = useState(() => {
    const stored = sessionStorage.getItem("chat_session_id");
    if (stored) return stored;
    const newId = uuidv4();
    sessionStorage.setItem("chat_session_id", newId);
    return newId;
  });

  const { messages, isStreaming, sendMessage, clearMessages } = useChat({
    topicId: selectedTopicId,
    sessionId,
    onError: (error) => {
      console.error("Chat error:", error);
      alert(`오류: ${error.message}`);
    },
  });

  useEffect(() => {
    clearMessages();
  }, [selectedTopicId, clearMessages]);

  return (
    <div className="flex h-screen bg-secondary-50">
      <div className="flex-1 flex flex-col max-w-5xl mx-auto w-full">
        <header className="border-b bg-white px-6 py-4 shadow-sm">
          <h1 className="text-2xl font-bold text-primary-700">질문하기</h1>
          <p className="text-sm text-secondary-500 mt-1">
            토픽을 선택하고 질문하세요
          </p>
        </header>

        <div className="flex-1 flex overflow-hidden">
          <aside className="w-64 border-r bg-white p-4">
            <h2 className="text-sm font-semibold text-secondary-700 mb-3">
              토픽 선택
            </h2>
            <TopicSelector
              selectedTopicId={selectedTopicId}
              onSelectTopic={setSelectedTopicId}
            />
          </aside>

          <main className="flex-1 flex flex-col">
            {messages.length === 0 && !selectedTopicId ? (
              <div className="flex-1 flex items-center justify-center">
                <div className="text-center text-secondary-400">
                  토픽을 선택하여 대화를 시작하세요
                </div>
              </div>
            ) : messages.length === 0 ? (
              <div className="flex-1 flex items-center justify-center">
                <div className="text-center text-secondary-400">
                  대화를 시작하세요
                </div>
              </div>
            ) : (
              <MessageList messages={messages} isStreaming={isStreaming} />
            )}

            <MessageInput
              onSend={sendMessage}
              disabled={!selectedTopicId}
              isStreaming={isStreaming}
            />
          </main>
        </div>
      </div>
    </div>
  );
};
