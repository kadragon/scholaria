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
];
