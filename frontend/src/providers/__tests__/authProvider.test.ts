import { describe, it, expect, beforeEach, vi } from "vitest";
import { authProvider } from "../authProvider";
import { server } from "../../__mocks__/msw/server";
import { http, HttpResponse } from "msw";

const API_URL = "http://localhost:8001/api";

describe("authProvider", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  describe("login", () => {
    it("should store token and return success on valid credentials", async () => {
      const result = await authProvider.login({
        email: "admin@test.com",
        password: "password",
      });

      expect(result.success).toBe(true);
      expect(result.redirectTo).toBe("/admin");
      expect(localStorage.getItem("token")).toBe("mock-token");
    });

    it("should return error on invalid credentials", async () => {
      server.use(
        http.post(`${API_URL}/auth/login`, () => {
          return new HttpResponse(null, { status: 401 });
        }),
      );

      const result = await authProvider.login({
        email: "wrong@test.com",
        password: "wrong",
      });

      expect(result.success).toBe(false);
      expect(result.error?.name).toBe("LoginError");
      expect(result.error?.message).toBe("Invalid credentials");
      expect(localStorage.getItem("token")).toBeNull();
    });
  });

  describe("logout", () => {
    it("should clear token and redirect to login", async () => {
      localStorage.setItem("token", "test-token");

      const result = await authProvider.logout({});

      expect(result.success).toBe(true);
      expect(result.redirectTo).toBe("/admin/login");
      expect(localStorage.getItem("token")).toBeNull();
    });
  });

  describe("check", () => {
    it("should return authenticated when token exists", async () => {
      localStorage.setItem("token", "test-token");

      const result = await authProvider.check();

      expect(result.authenticated).toBe(true);
      expect(result.redirectTo).toBeUndefined();
    });

    it("should return unauthenticated when token is missing", async () => {
      const result = await authProvider.check();

      expect(result.authenticated).toBe(false);
      expect(result.redirectTo).toBe("/admin/login");
    });
  });

  describe("getIdentity", () => {
    it("should return user data when token is valid", async () => {
      localStorage.setItem("token", "test-token");

      const identity = await authProvider.getIdentity();

      expect(identity).toEqual({ id: 1, email: "admin@test.com" });
    });

    it("should return null when token is missing", async () => {
      const identity = await authProvider.getIdentity();

      expect(identity).toBeNull();
    });

    it("should return null when API call fails", async () => {
      localStorage.setItem("token", "invalid-token");

      server.use(
        http.get(`${API_URL}/auth/me`, () => {
          return new HttpResponse(null, { status: 401 });
        }),
      );

      const identity = await authProvider.getIdentity();

      expect(identity).toBeNull();
    });
  });

  describe("onError", () => {
    it("should trigger logout on 401 error", async () => {
      const error = { status: 401 };

      const result = await authProvider.onError(error);

      expect(result.logout).toBe(true);
      expect(result.redirectTo).toBe("/admin/login");
      expect(result.error).toEqual(error);
    });

    it("should trigger logout on 403 error", async () => {
      const error = { status: 403 };

      const result = await authProvider.onError(error);

      expect(result.logout).toBe(true);
      expect(result.redirectTo).toBe("/admin/login");
      expect(result.error).toEqual(error);
    });

    it("should pass through other errors without logout", async () => {
      const error = { status: 500 };

      const result = await authProvider.onError(error);

      expect(result.logout).toBeUndefined();
      expect(result.redirectTo).toBeUndefined();
      expect(result.error).toEqual(error);
    });
  });
});
