import { describe, it, expect, beforeEach } from "vitest";
import { apiClient } from "../apiClient";

type RequestInterceptor = {
  fulfilled: (config: { headers: Record<string, string> }) => { headers: Record<string, string> };
};

type ResponseInterceptor = {
  rejected: (error: { response?: { status: number } }) => Promise<never>;
};

describe("apiClient", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  describe("request interceptor", () => {
    it("should attach Authorization header when token exists", () => {
      localStorage.setItem("token", "test-token");

      const mockConfig = { headers: {} };
      const interceptor = apiClient.interceptors.request.handlers[0] as RequestInterceptor;
      const result = interceptor.fulfilled(mockConfig);

      expect(result.headers.Authorization).toBe("Bearer test-token");
    });

    it("should not attach Authorization header when token is missing", () => {
      const mockConfig = { headers: {} };
      const interceptor = apiClient.interceptors.request.handlers[0] as RequestInterceptor;
      const result = interceptor.fulfilled(mockConfig);

      expect(result.headers.Authorization).toBeUndefined();
    });
  });

  describe("response interceptor", () => {
    it("should clear token and redirect on 401 error", async () => {
      localStorage.setItem("token", "expired-token");

      Object.defineProperty(window, "location", {
        value: { href: "/admin/topics", pathname: "/admin/topics" },
        writable: true,
      });

      const error = { response: { status: 401 } };
      const interceptor = apiClient.interceptors.response.handlers[0] as ResponseInterceptor;

      try {
        await interceptor.rejected(error);
      } catch {
      }

      expect(localStorage.getItem("token")).toBeNull();
      expect(window.location.href).toBe("/admin/login");
    });

    it("should not redirect if already on login page", async () => {
      localStorage.setItem("token", "expired-token");

      Object.defineProperty(window, "location", {
        value: { href: "/admin/login", pathname: "/admin/login" },
        writable: true,
      });

      const error = { response: { status: 401 } };
      const interceptor = apiClient.interceptors.response.handlers[0] as ResponseInterceptor;

      try {
        await interceptor.rejected(error);
      } catch {
      }

      expect(localStorage.getItem("token")).toBeNull();
      expect(window.location.href).toBe("/admin/login");
    });

    it("should pass through non-401 errors", async () => {
      const error = { response: { status: 500 } };
      const interceptor = apiClient.interceptors.response.handlers[0] as ResponseInterceptor;

      await expect(interceptor.rejected(error)).rejects.toEqual(error);
    });
  });
});
