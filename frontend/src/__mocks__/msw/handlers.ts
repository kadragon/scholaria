import { http, HttpResponse } from "msw";

const API_BASE_URL = "http://localhost:8001/api";

export const handlers = [
  http.post(`${API_BASE_URL}/auth/login`, () => {
    return HttpResponse.json({ access_token: "mock-token" });
  }),

  http.get(`${API_BASE_URL}/auth/me`, () => {
    return HttpResponse.json({ id: 1, email: "admin@test.com" });
  }),

  http.get(`${API_BASE_URL}/topics`, () => {
    return HttpResponse.json({ data: [], total: 0 });
  }),

  http.get(`${API_BASE_URL}/contexts`, () => {
    return HttpResponse.json({ data: [], total: 0 });
  }),

  http.post(`${API_BASE_URL}/history`, async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({
      id: 1,
      topic_id: body.topic_id ?? 1,
      question: body.question ?? "",
      answer: body.answer ?? "",
      session_id: body.session_id ?? "session",
      feedback_score: 0,
      feedback_comment: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    });
  }),

  http.patch(`${API_BASE_URL}/history/:historyId/feedback`, async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({
      id: 1,
      feedback_score: body.feedback_score ?? 0,
      feedback_comment: body.feedback_comment ?? null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      question: "",
      answer: "",
      session_id: "session",
      topic_id: 1,
    });
  }),
];
