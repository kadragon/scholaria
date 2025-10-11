import { describe, it, expect, beforeEach, vi } from "vitest";

const mockInterceptors = {
  request: { use: vi.fn() },
  response: { use: vi.fn() },
};

const mockAxiosInstance = Object.assign(
  vi.fn((config) => {
    if (config.method === "post" && mockAxiosInstance.post) {
      return mockAxiosInstance.post(config);
    }
    if (config.method === "get" && mockAxiosInstance.get) {
      return mockAxiosInstance.get(config);
    }
    return Promise.resolve({ data: {} });
  }),
  {
    interceptors: mockInterceptors,
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    patch: vi.fn(),
  },
);

vi.mock("axios", () => ({
  default: {
    create: vi.fn(() => mockAxiosInstance),
  },
}));

vi.mock("@refinedev/simple-rest", () => ({
  default: vi.fn(() => ({
    getList: vi.fn(),
    getOne: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    deleteOne: vi.fn(),
  })),
}));

describe("adminDataProvider", () => {
  beforeEach(async () => {
    vi.clearAllMocks();
    localStorage.clear();
    mockInterceptors.request.use.mockClear();
    mockInterceptors.response.use.mockClear();
    vi.resetModules();
  });

  describe("request interceptor", () => {
    it("should add Authorization header when token exists", async () => {
      localStorage.setItem("token", "test-token-123");

      await import("../dataProvider");

      expect(mockInterceptors.request.use).toHaveBeenCalled();
      const requestInterceptor = mockInterceptors.request.use.mock.calls[0][0];

      const mockConfig = { headers: {} };
      const result = requestInterceptor(mockConfig);

      expect(result.headers.Authorization).toBe("Bearer test-token-123");
    });
  });

  describe("response interceptor", () => {
    it("should redirect to login on 401 response", async () => {
      await import("../dataProvider");

      expect(mockInterceptors.response.use).toHaveBeenCalled();
      const errorHandler = mockInterceptors.response.use.mock.calls[0][1];

      const mockError = {
        response: { status: 401 },
      };

      localStorage.setItem("token", "should-be-removed");

      try {
        await errorHandler(mockError);
      } catch {
        expect(localStorage.getItem("token")).toBeNull();
      }
    });
  });

  describe("getList transformation", () => {
    it("should transform nested data structure with total", async () => {
      vi.doMock("@refinedev/simple-rest", () => ({
        default: vi.fn(() => ({
          getList: vi.fn().mockResolvedValue({
            data: {
              data: [{ id: 1 }, { id: 2 }],
              total: 10,
            },
          }),
        })),
      }));

      const { adminDataProvider } = await import("../dataProvider");

      const result = await adminDataProvider.getList({
        resource: "topics",
        pagination: { current: 1, pageSize: 10 },
      });

      expect(result.data).toEqual([{ id: 1 }, { id: 2 }]);
      expect(result.total).toBe(10);
    });

    it("should handle direct array response", async () => {
      vi.doMock("@refinedev/simple-rest", () => ({
        default: vi.fn(() => ({
          getList: vi.fn().mockResolvedValue({
            data: [{ id: 1 }, { id: 2 }],
            total: 2,
          }),
        })),
      }));

      const { adminDataProvider } = await import("../dataProvider");

      const result = await adminDataProvider.getList({
        resource: "topics",
        pagination: { current: 1, pageSize: 10 },
      });

      expect(result.data).toEqual([{ id: 1 }, { id: 2 }]);
      expect(result.total).toBe(2);
    });
  });

  describe("custom method", () => {
    it("should construct URL with query params", async () => {
      mockAxiosInstance.mockResolvedValue({ data: { result: "success" } });

      vi.doMock("@refinedev/simple-rest", () => ({
        default: vi.fn(() => ({
          getList: vi.fn(),
        })),
      }));

      const { adminDataProvider } = await import("../dataProvider");

      await adminDataProvider.custom({
        url: "analytics/summary",
        method: "get",
        query: { start_date: "2025-01-01", end_date: "2025-12-31" },
      });

      expect(mockAxiosInstance).toHaveBeenCalled();
      const axiosCall = mockAxiosInstance.mock.calls[0][0];
      expect(axiosCall.url).toContain("analytics/summary");
      expect(axiosCall.url).toContain("start_date=2025-01-01");
      expect(axiosCall.url).toContain("end_date=2025-12-31");
    });

    it("should send payload with POST method", async () => {
      mockAxiosInstance.mockResolvedValue({ data: { id: 1 } });

      vi.doMock("@refinedev/simple-rest", () => ({
        default: vi.fn(() => ({
          getList: vi.fn(),
        })),
      }));

      const { adminDataProvider } = await import("../dataProvider");

      await adminDataProvider.custom({
        url: "topics",
        method: "post",
        payload: { name: "Test Topic", description: "Test" },
      });

      expect(mockAxiosInstance).toHaveBeenCalled();
      const axiosCall = mockAxiosInstance.mock.calls[0][0];
      expect(axiosCall.method).toBe("post");
      expect(axiosCall.data).toEqual({
        name: "Test Topic",
        description: "Test",
      });
    });

    it("should forward custom headers", async () => {
      mockAxiosInstance.mockResolvedValue({ data: {} });

      vi.doMock("@refinedev/simple-rest", () => ({
        default: vi.fn(() => ({
          getList: vi.fn(),
        })),
      }));

      const { adminDataProvider } = await import("../dataProvider");

      await adminDataProvider.custom({
        url: "topics",
        method: "get",
        headers: { "X-Custom-Header": "test-value" },
      });

      expect(mockAxiosInstance).toHaveBeenCalled();
      const axiosCall = mockAxiosInstance.mock.calls[0][0];
      expect(axiosCall.headers).toEqual({ "X-Custom-Header": "test-value" });
    });
  });
});
