import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { v4 as uuidv4 } from "uuid";
import { TopicSelector } from "./components/TopicSelector";
import { MessageList } from "./components/MessageList";
import { MessageInput } from "./components/MessageInput";
import { useChat } from "./hooks/useChat";
import { useToast } from "../../hooks/use-toast";

export const ChatPage = () => {
  const { topicId: topicIdParam } = useParams<{ topicId?: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
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
      toast({
        title: "오류",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  useEffect(() => {
    document.title = "Scholaria - AI 질문답변";
  }, []);

  useEffect(() => {
    if (topicIdParam) {
      const topicId = parseInt(topicIdParam, 10);
      if (!isNaN(topicId)) {
        setSelectedTopicId(topicId);
      } else {
        setSelectedTopicId(null);
      }
    } else {
      setSelectedTopicId(null);
    }
  }, [topicIdParam]);

  useEffect(() => {
    clearMessages();
  }, [selectedTopicId, clearMessages]);

  const handleTopicSelect = (topicId: number) => {
    setSelectedTopicId(topicId);
    navigate(`/chat/${topicId}`, { replace: true });
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-secondary-50 to-secondary-100">
      <div className="flex-1 flex flex-col max-w-7xl mx-auto w-full shadow-2xl bg-white">
        <header className="border-b-2 border-primary-100 bg-gradient-to-r from-primary-600 to-primary-700 px-8 py-6 shadow-lg">
          <h1 className="text-3xl font-bold text-white">AI 질문 답변</h1>
          <p className="text-sm text-primary-100 mt-2">
            토픽을 선택하고 궁금한 점을 질문하세요
          </p>
        </header>

        <div className="flex-1 flex overflow-hidden">
          <aside className="w-72 border-r-2 border-secondary-200 bg-gradient-to-b from-white to-secondary-50 p-6 shadow-inner">
            <h2 className="text-sm font-bold text-secondary-800 mb-4 uppercase tracking-wider">
              토픽 선택
            </h2>
            <TopicSelector
              selectedTopicId={selectedTopicId}
              onSelectTopic={handleTopicSelect}
            />
          </aside>

          <main className="flex-1 flex flex-col bg-white">
            {messages.length === 0 && !selectedTopicId ? (
              <div className="flex-1 flex items-center justify-center bg-gradient-to-b from-secondary-50 to-white">
                <div className="text-center max-w-md p-8">
                  <div className="mb-4 text-6xl">💬</div>
                  <h3 className="text-xl font-bold text-secondary-700 mb-2">
                    대화를 시작해보세요
                  </h3>
                  <p className="text-secondary-500">
                    왼쪽에서 토픽을 선택하면 해당 주제에 대해 질문할 수 있습니다
                  </p>
                </div>
              </div>
            ) : messages.length === 0 ? (
              <div className="flex-1 flex items-center justify-center bg-gradient-to-b from-secondary-50 to-white">
                <div className="text-center max-w-md p-8">
                  <div className="mb-4 text-6xl">✨</div>
                  <h3 className="text-xl font-bold text-secondary-700 mb-2">
                    질문을 입력하세요
                  </h3>
                  <p className="text-secondary-500">
                    아래 입력창에 궁금한 점을 자유롭게 질문해주세요
                  </p>
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
