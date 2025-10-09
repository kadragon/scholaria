import { useEffect, useMemo, useState } from "react";
import { useCustom } from "@refinedev/core";
import { AnalyticsSkeleton } from "@/components/AnalyticsSkeleton";
import { Skeleton } from "@/components/ui/skeleton";
import { getFeedbackMeta } from "@/utils/feedback";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

interface AnalyticsSummary {
  total_questions: number;
  total_feedback: number;
  active_sessions: number;
  average_feedback_score: number;
}

interface TopicStats {
  topic_id: number;
  topic_name: string;
  question_count: number;
  average_feedback_score: number;
}

interface QuestionTrend {
  date: string;
  question_count: number;
}

interface FeedbackDistribution {
  positive: number;
  neutral: number;
  negative: number;
}

interface FeedbackComment {
  history_id: number;
  topic_id: number;
  topic_name: string;
  feedback_score: number;
  feedback_comment: string;
  created_at: string;
}

const COLORS = {
  positive: "#10b981",
  neutral: "#6b7280",
  negative: "#ef4444",
  primary: "#3b82f6",
};

export const Analytics = () => {
  const [days, setDays] = useState(7);
  const [selectedTopicId, setSelectedTopicId] = useState<"all" | number>("all");

  const { data: summaryData, isLoading: summaryLoading } =
    useCustom<AnalyticsSummary>({
      url: "analytics/summary",
      method: "get",
    });

  const { data: topicsData, isLoading: topicsLoading } = useCustom<
    TopicStats[]
  >({
    url: "analytics/topics",
    method: "get",
  });

  const {
    data: trendData,
    isLoading: trendLoading,
    refetch: refetchTrend,
  } = useCustom<QuestionTrend[]>({
    url: "analytics/questions/trend",
    method: "get",
    config: {
      query: { days },
    },
  });

  const { data: feedbackData, isLoading: feedbackLoading } =
    useCustom<FeedbackDistribution>({
      url: "analytics/feedback/distribution",
      method: "get",
    });

  const commentsQuery = useMemo(() => {
    if (selectedTopicId === "all") {
      return {};
    }
    return { topic_id: selectedTopicId };
  }, [selectedTopicId]);

  const {
    data: commentsData,
    isFetching: commentsFetching,
    refetch: refetchComments,
  } = useCustom<FeedbackComment[]>({
    url: "analytics/feedback/comments",
    method: "get",
    config: {
      query: commentsQuery,
    },
    queryOptions: {
      enabled: false,
      keepPreviousData: true,
    },
  });

  useEffect(() => {
    refetchTrend();
  }, [days, refetchTrend]);

  useEffect(() => {
    void refetchComments();
  }, [commentsQuery, refetchComments]);

  const isInitialLoading =
    summaryLoading ||
    topicsLoading ||
    trendLoading ||
    feedbackLoading ||
    (!commentsData && commentsFetching);

  const summary = summaryData?.data;
  const topics = useMemo(
    () => (Array.isArray(topicsData?.data) ? topicsData.data : []),
    [topicsData?.data],
  );
  const trend = Array.isArray(trendData?.data) ? trendData.data : [];
  const feedback = feedbackData?.data;
  const comments = useMemo(
    () => (Array.isArray(commentsData?.data) ? commentsData.data : []),
    [commentsData?.data],
  );

  const topicOptions = useMemo(() => {
    const map = new Map<number, string>();
    topics.forEach((topic) => map.set(topic.topic_id, topic.topic_name));
    comments.forEach((comment) =>
      map.set(comment.topic_id, comment.topic_name),
    );
    return Array.from(map.entries()).sort((a, b) =>
      a[1].localeCompare(b[1], "ko"),
    );
  }, [topics, comments]);

  const dateFormatter = useMemo(
    () =>
      new Intl.DateTimeFormat("ko-KR", {
        dateStyle: "medium",
        timeStyle: "short",
      }),
    [],
  );

  if (isInitialLoading) {
    return <AnalyticsSkeleton />;
  }

  const feedbackPieData = feedback
    ? [
        { name: "긍정", value: feedback.positive },
        { name: "중립", value: feedback.neutral },
        { name: "부정", value: feedback.negative },
      ]
    : [];

  return (
    <div className="p-8 space-y-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-secondary-900 mb-2">
          분석 대시보드
        </h1>
        <p className="text-secondary-600">
          시스템 사용 현황과 통계를 확인합니다
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-6 gap-4 auto-rows-fr">
        <div className="md:col-span-2 p-6 bg-gradient-to-br from-white to-primary-50 rounded-lg shadow-md border border-primary-100 hover:scale-[1.02] hover:shadow-lg transition-all duration-200">
          <h3 className="text-sm text-gray-500 mb-1">총 질문 수</h3>
          <p className="text-3xl font-bold text-primary-700">
            {summary?.total_questions || 0}
          </p>
        </div>
        <div className="md:col-span-2 p-6 bg-gradient-to-br from-white to-green-50 rounded-lg shadow-md border border-green-100 hover:scale-[1.02] hover:shadow-lg transition-all duration-200">
          <h3 className="text-sm text-gray-500 mb-1">피드백 수</h3>
          <p className="text-3xl font-bold text-green-700">
            {summary?.total_feedback || 0}
          </p>
        </div>
        <div className="md:col-span-2 md:row-span-2 p-6 bg-white rounded-lg shadow-md border border-gray-200 hover:shadow-xl transition-all duration-200">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-bold">질문 추세</h2>
            <select
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              className="border rounded px-3 py-1 text-sm"
            >
              <option value={1}>1일</option>
              <option value={7}>7일</option>
              <option value={30}>30일</option>
              <option value={90}>90일</option>
            </select>
          </div>
          {trend.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={trend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="question_count"
                  stroke={COLORS.primary}
                  name="질문 수"
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-500 text-center py-12 text-sm">
              선택한 기간에 데이터가 없습니다.
            </p>
          )}
        </div>
        <div className="md:col-span-2 p-6 bg-gradient-to-br from-white to-purple-50 rounded-lg shadow-md border border-purple-100 hover:scale-[1.02] hover:shadow-lg transition-all duration-200">
          <h3 className="text-sm text-gray-500 mb-1">활성 세션</h3>
          <p className="text-3xl font-bold text-purple-700">
            {summary?.active_sessions || 0}
          </p>
        </div>
        <div className="md:col-span-2 p-6 bg-gradient-to-br from-white to-orange-50 rounded-lg shadow-md border border-orange-100 hover:scale-[1.02] hover:shadow-lg transition-all duration-200">
          <h3 className="text-sm text-gray-500 mb-1">평균 피드백 점수</h3>
          <p className="text-3xl font-bold text-orange-700">
            {summary?.average_feedback_score?.toFixed(2) || "0.00"}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-xl transition-all duration-200 border border-gray-100">
          <h2 className="text-xl font-bold mb-4">토픽별 활동</h2>
          {topics.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={topics}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="topic_name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar
                  dataKey="question_count"
                  fill={COLORS.primary}
                  name="질문 수"
                />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-500 text-center py-12">
              토픽 데이터가 없습니다.
            </p>
          )}
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-xl transition-all duration-200 border border-gray-100">
          <h2 className="text-xl font-bold mb-4">피드백 분포</h2>
          {feedbackPieData.length > 0 &&
          feedbackPieData.some((d) => d.value > 0) ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={feedbackPieData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => `${entry.name}: ${entry.value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  <Cell key="positive" fill={COLORS.positive} />
                  <Cell key="neutral" fill={COLORS.neutral} />
                  <Cell key="negative" fill={COLORS.negative} />
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-500 text-center py-12">
              피드백 데이터가 없습니다.
            </p>
          )}
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-xl transition-all duration-200 border border-gray-100">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold text-secondary-900">
              최근 피드백 코멘트
            </h2>
            <p className="text-sm text-secondary-500">
              사용자들이 남긴 자유 서술 피드백을 모아 확인합니다.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <label
              htmlFor="feedback-topic-filter"
              className="text-sm text-secondary-600"
            >
              토픽 필터
            </label>
            <select
              id="feedback-topic-filter"
              value={
                selectedTopicId === "all" ? "all" : selectedTopicId.toString()
              }
              onChange={(event) => {
                const value = event.target.value;
                setSelectedTopicId(value === "all" ? "all" : Number(value));
              }}
              className="border border-gray-200 rounded-md px-3 py-1 text-sm"
            >
              <option value="all">전체</option>
              {topicOptions.map(([id, name]) => (
                <option key={id} value={id.toString()}>
                  {name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {commentsFetching && !comments.length ? (
          <div className="space-y-3">
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-20 w-full" />
          </div>
        ) : comments.length > 0 ? (
          <div className="space-y-4">
            {commentsFetching && (
              <p className="text-xs text-secondary-500">
                최신 데이터를 불러오는 중...
              </p>
            )}
            <ul className="space-y-4">
              {comments.map((comment) => {
                const meta = getFeedbackMeta(comment.feedback_score);
                const createdAt = dateFormatter.format(
                  new Date(comment.created_at),
                );
                return (
                  <li
                    key={comment.history_id}
                    className="border border-gray-200 rounded-lg p-4 bg-secondary-50/40"
                  >
                    <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                      <div>
                        <p className="text-sm font-semibold text-secondary-900">
                          {comment.topic_name}
                        </p>
                        <p className="text-xs text-secondary-500">
                          {createdAt}
                        </p>
                      </div>
                      <span className={meta.className}>{meta.label}</span>
                    </div>
                    <p className="mt-3 text-sm leading-relaxed text-secondary-700 whitespace-pre-line">
                      {comment.feedback_comment}
                    </p>
                  </li>
                );
              })}
            </ul>
          </div>
        ) : (
          <p className="text-gray-500 text-center py-12 text-sm">
            표시할 피드백 코멘트가 없습니다.
          </p>
        )}
      </div>
    </div>
  );
};
