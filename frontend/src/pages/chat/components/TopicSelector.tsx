import { useEffect, useState } from "react";
import { useCustom } from "@refinedev/core";

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
  const { data, isLoading, isError } = useCustom<{ data: Topic[] }>({
    url: `${import.meta.env.VITE_API_URL}/api/topics`,
    method: "get",
  });

  const topics = data?.data?.data ?? [];

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
          className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
            selectedTopicId === topic.id
              ? "bg-primary-100 text-primary-700 font-medium"
              : "hover:bg-secondary-100 text-secondary-700"
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
