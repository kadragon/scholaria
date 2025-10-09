export const API_BASE_URL = import.meta.env.VITE_API_URL?.replace('/admin', '') || "http://localhost:8001/api";

export const getAuthHeaders = (): HeadersInit => {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
  };
  const token = localStorage.getItem("token");
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
};
