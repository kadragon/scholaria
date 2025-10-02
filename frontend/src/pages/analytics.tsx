import { useEffect, useState } from "react"; // v2
import { useCustom } from "@refinedev/core";
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

const COLORS = {
  positive: "#10b981",
  neutral: "#6b7280",
  negative: "#ef4444",
  primary: "#3b82f6",
};

export const Analytics = () => {
  const [days, setDays] = useState(7);

  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8001/api/admin";

  const { data: summaryData, isLoading: summaryLoading } =
    useCustom<AnalyticsSummary>({
      url: `${API_URL}/admin/analytics/summary`,
      method: "get",
    });

  const { data: topicsData, isLoading: topicsLoading } = useCustom<
    TopicStats[]
  >({
    url: `${API_URL}/admin/analytics/topics`,
    method: "get",
  });

  const {
    data: trendData,
    isLoading: trendLoading,
    refetch: refetchTrend,
  } = useCustom<QuestionTrend[]>({
    url: `${API_URL}/admin/analytics/questions/trend`,
    method: "get",
    config: {
      query: { days },
    },
  });

  const { data: feedbackData, isLoading: feedbackLoading } =
    useCustom<FeedbackDistribution>({
      url: `${API_URL}/admin/analytics/feedback/distribution`,
      method: "get",
    });

  useEffect(() => {
    refetchTrend();
  }, [days, refetchTrend]);

  if (summaryLoading || topicsLoading || trendLoading || feedbackLoading) {
    return <div className="p-6">로딩 중...</div>;
  }

  const summary = summaryData?.data as AnalyticsSummary | undefined;
  const topics = (topicsData?.data as TopicStats[]) || [];
  const trend = (trendData?.data as QuestionTrend[]) || [];
  const feedback = feedbackData?.data as FeedbackDistribution | undefined;

  const feedbackPieData = feedback
    ? [
        { name: "긍정", value: feedback.positive },
        { name: "중립", value: feedback.neutral },
        { name: "부정", value: feedback.negative },
      ]
    : [];

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">분석 대시보드</h1>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 bg-white rounded-lg shadow">
          <h3 className="text-sm text-gray-500">총 질문 수</h3>
          <p className="text-2xl font-bold">{summary?.total_questions || 0}</p>
        </div>
        <div className="p-4 bg-white rounded-lg shadow">
          <h3 className="text-sm text-gray-500">피드백 수</h3>
          <p className="text-2xl font-bold">{summary?.total_feedback || 0}</p>
        </div>
        <div className="p-4 bg-white rounded-lg shadow">
          <h3 className="text-sm text-gray-500">활성 세션</h3>
          <p className="text-2xl font-bold">
            {summary?.active_sessions || 0}
          </p>
        </div>
        <div className="p-4 bg-white rounded-lg shadow">
          <h3 className="text-sm text-gray-500">평균 피드백 점수</h3>
          <p className="text-2xl font-bold">
            {summary?.average_feedback_score?.toFixed(2) || "0.00"}
          </p>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">질문 추세</h2>
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            className="border rounded px-3 py-1"
          >
            <option value={1}>1일</option>
            <option value={7}>7일</option>
            <option value={30}>30일</option>
            <option value={90}>90일</option>
          </select>
        </div>
        {trend.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
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
          <p className="text-gray-500 text-center py-12">
            선택한 기간에 데이터가 없습니다.
          </p>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-bold mb-4">토픽별 활동</h2>
          {topics.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={topics}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="topic_name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="question_count" fill={COLORS.primary} name="질문 수" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-500 text-center py-12">
              토픽 데이터가 없습니다.
            </p>
          )}
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
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
    </div>
  );
};
