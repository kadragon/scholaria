export type FeedbackSentiment = "positive" | "neutral" | "negative";

export interface FeedbackMeta {
  label: string;
  sentiment: FeedbackSentiment;
  className: string;
}

const FEEDBACK_META: Record<FeedbackSentiment, FeedbackMeta> = {
  positive: {
    label: "좋아요",
    sentiment: "positive",
    className:
      "inline-flex items-center rounded-full border border-emerald-200 bg-emerald-50 px-2 py-0.5 text-xs font-medium text-emerald-700",
  },
  neutral: {
    label: "중립",
    sentiment: "neutral",
    className:
      "inline-flex items-center rounded-full border border-gray-200 bg-gray-50 px-2 py-0.5 text-xs font-medium text-gray-600",
  },
  negative: {
    label: "싫어요",
    sentiment: "negative",
    className:
      "inline-flex items-center rounded-full border border-rose-200 bg-rose-50 px-2 py-0.5 text-xs font-medium text-rose-700",
  },
};

/**
 * Map numeric feedback score (-1, 0, 1) to localized label and styling metadata.
 */
export const getFeedbackMeta = (score: number): FeedbackMeta => {
  if (score > 0) {
    return FEEDBACK_META.positive;
  }
  if (score < 0) {
    return FEEDBACK_META.negative;
  }
  return FEEDBACK_META.neutral;
};
