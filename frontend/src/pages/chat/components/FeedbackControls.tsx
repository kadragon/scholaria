import { useState } from "react";
import { apiClient } from "../../../lib/apiClient";
import { useToast } from "../../../hooks/use-toast";

interface FeedbackControlsProps {
  historyId: number;
  initialScore: number;
  initialComment: string;
  disabled?: boolean;
  onChange?: (score: number, comment: string | null) => void;
}

const FEEDBACK_OPTIONS = [
  { value: 1, label: "좋아요", emoji: "👍" },
  { value: 0, label: "중립", emoji: "😐" },
  { value: -1, label: "싫어요", emoji: "👎" },
] as const;

export const FeedbackControls = ({
  historyId,
  initialScore,
  initialComment,
  disabled = false,
  onChange,
}: FeedbackControlsProps) => {
  const { toast } = useToast();
  const [score, setScore] = useState<number>(initialScore ?? 0);
  const [comment, setComment] = useState<string>(initialComment ?? "");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (disabled || isSubmitting) {
      return;
    }

    setIsSubmitting(true);
    const trimmed = comment.trim();

    try {
      const response = await apiClient.patch(`/history/${historyId}/feedback`, {
        feedback_score: score,
        feedback_comment: trimmed.length > 0 ? trimmed : null,
      });

      const data = response.data;
      setScore(data.feedback_score);
      setComment(data.feedback_comment ?? "");
      onChange?.(data.feedback_score, data.feedback_comment ?? null);

      toast({
        title: "피드백이 저장되었습니다.",
        description: data.feedback_comment
          ? "자유 서술 코멘트와 평점이 전송됐습니다."
          : "평점이 업데이트되었습니다.",
      });
    } catch (error) {
      console.error("Failed to submit feedback:", error);
      toast({
        title: "피드백 전송 실패",
        description: "다시 시도해주세요.",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleOptionSelect = (value: number) => {
    if (disabled || isSubmitting) {
      return;
    }
    setScore(value);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div className="flex flex-wrap gap-2">
        {FEEDBACK_OPTIONS.map((option) => {
          const isActive = option.value === score;
          return (
            <button
              key={option.value}
              type="button"
              onClick={() => handleOptionSelect(option.value)}
              className={`flex items-center gap-2 rounded-full border px-3 py-1 text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-primary-300 focus:ring-offset-2 ${
                isActive
                  ? "border-primary-500 bg-primary-50 text-primary-700"
                  : "border-secondary-200 bg-white text-secondary-600 hover:border-primary-300 hover:text-primary-600"
              } ${disabled ? "opacity-60 cursor-not-allowed" : ""}`}
              disabled={disabled || isSubmitting}
            >
              <span>{option.emoji}</span>
              <span>{option.label}</span>
            </button>
          );
        })}
      </div>

      <textarea
        value={comment}
        onChange={(event) => setComment(event.target.value)}
        placeholder="자유 서술 피드백을 남겨주세요 (선택 사항)"
        className="w-full rounded-lg border border-secondary-200 bg-secondary-50 px-3 py-2 text-sm text-secondary-700 focus:border-primary-400 focus:outline-none focus:ring-2 focus:ring-primary-200 disabled:opacity-60"
        rows={3}
        disabled={disabled || isSubmitting}
      />

      <div className="flex items-center gap-2">
        <button
          type="submit"
          className="rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-300 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
          disabled={disabled || isSubmitting}
        >
          {isSubmitting ? "저장 중..." : "피드백 저장"}
        </button>
        <button
          type="button"
          onClick={() => setComment("")}
          className="rounded-md border border-secondary-200 px-3 py-2 text-sm text-secondary-600 hover:bg-secondary-100 focus:outline-none focus:ring-2 focus:ring-secondary-200 disabled:cursor-not-allowed disabled:opacity-60"
          disabled={disabled || isSubmitting || comment.length === 0}
        >
          코멘트 지우기
        </button>
      </div>
    </form>
  );
};
