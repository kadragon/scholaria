import { describe, it, expect, beforeEach, vi } from "vitest";
import { server } from "../../__mocks__/msw/server";
import { http, HttpResponse } from "msw";
import { apiClient } from "../apiClient";

describe("apiClient", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  describe("request interceptor", () => {
    it("should attach Authorization header when token exists", async () => {
      localStorage.setItem("token", "test-token");
      let authHeader: string | null = null;
      server.use(
        http.get("*/test", ({ request }) => {
          authHeader = request.headers.get("Authorization");
          return new HttpResponse(null, { status: 200 });
        })
      );

      await apiClient.get("/test");
      expect(authHeader).toBe("Bearer test-token");
    });

    it("should not attach Authorization header when token is missing", async () => {
      let authHeader: string | null = "initial";
      server.use(
        http.get("*/test", ({ request }) => {
          authHeader = request.headers.get("Authorization");
          return new HttpResponse(null, { status: 200 });
        })
      );

      await apiClient.get("/test");
      expect(authHeader).toBeNull();
    });
  });

  describe("response interceptor", () => {
    it("should clear token and redirect on 401 error", async () => {
      localStorage.setItem("token", "expired-token");
      const mockLocationHref = vi.fn();
      Object.defineProperty(window, "location", {
        value: {
          pathname: "/admin/topics",
          set href(url: string) { mockLocationHref(url); }
        },
        writable: true,
        configurable: true,
      });
      server.use(http.get("*/protected", () => new HttpResponse(null, { status: 401 })));

      try {
        await apiClient.get("/protected");
      } catch (error) {
        void error;
      }

      expect(localStorage.getItem("token")).toBeNull();
      expect(mockLocationHref).toHaveBeenCalledWith("/admin/login");
    });

    it("should not redirect if already on login page", async () => {
      localStorage.setItem("token", "expired-token");
      const mockLocationHref = vi.fn();
      Object.defineProperty(window, "location", {
        value: {
          pathname: "/admin/login",
          set href(url: string) { mockLocationHref(url); }
        },
        writable: true,
        configurable: true,
      });
      server.use(http.get("*/protected", () => new HttpResponse(null, { status: 401 })));

      try {
        await apiClient.get("/protected");
      } catch (error) {
        void error;
      }

      expect(localStorage.getItem("token")).toBeNull();
      expect(mockLocationHref).not.toHaveBeenCalled();
    });

    it("should pass through non-401 errors", async () => {
      server.use(http.get("*/error", () => new HttpResponse(null, { status: 500 })));

      await expect(apiClient.get("/error")).rejects.toThrow();
    });
  });
});
