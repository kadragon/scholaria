import { useState } from "react";
import { TopicSelector } from "./components/TopicSelector";

export const ChatPage = () => {
  const [selectedTopicId, setSelectedTopicId] = useState<number | null>(null);

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
            <div className="flex-1 overflow-y-auto p-6">
              {selectedTopicId ? (
                <div className="text-center text-secondary-400 mt-20">
                  대화를 시작하세요
                </div>
              ) : (
                <div className="text-center text-secondary-400 mt-20">
                  토픽을 선택하여 대화를 시작하세요
                </div>
              )}
            </div>

            <div className="border-t bg-white p-4">
              <div className="max-w-3xl mx-auto">
                <textarea
                  className="w-full border rounded-lg p-3 resize-none focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="질문을 입력하세요..."
                  rows={3}
                  disabled={!selectedTopicId}
                />
                <div className="flex justify-end mt-2">
                  <button
                    className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    disabled={!selectedTopicId}
                  >
                    전송
                  </button>
                </div>
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
};
