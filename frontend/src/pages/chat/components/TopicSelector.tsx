
import { useState, useEffect } from "react";

interface Topic {
  id: number;
  name: string;
  description: string;
}

interface TopicSelectorProps {
  selectedTopicId: number | null;
  onSelectTopic: (topicId: number) => void;
}

export const TopicSelector = ({
  selectedTopicId,
  onSelectTopic,
}: TopicSelectorProps) => {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isError, setIsError] = useState(false);

  useEffect(() => {
    const fetchTopics = async () => {
      try {
        setIsLoading(true);
        const response = await fetch("/api/topics");
        if (!response.ok) throw new Error("Failed to fetch topics");
        const data = await response.json();
        setTopics(Array.isArray(data) ? data : data.data || []);
        setIsError(false);
      } catch (error) {
        console.error("Error fetching topics:", error);
        setIsError(true);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTopics();
  }, []);

  if (isLoading) {
    return (
      <div className="text-sm text-secondary-500">토픽 목록 로딩 중...</div>
    );
  }

  if (isError || topics.length === 0) {
    return (
      <div className="text-sm text-red-500">
        토픽을 불러올 수 없습니다.
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {topics.map((topic) => (
        <button
          key={topic.id}
          onClick={() => onSelectTopic(topic.id)}
          className={`w-full text-left px-3 py-2 rounded-lg transition-colors border-2 ${
            selectedTopicId === topic.id
              ? "bg-primary-600 text-white font-semibold border-primary-600 shadow-md"
              : "hover:bg-primary-50 text-secondary-700 border-transparent hover:border-primary-200"
          }`}
        >
          <div className="text-sm font-medium">{topic.name}</div>
          {topic.description && (
            <div className="text-xs text-secondary-500 mt-1 line-clamp-2">
              {topic.description}
            </div>
          )}
        </button>
      ))}
    </div>
  );
};
