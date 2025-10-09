import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, act, waitFor } from "@testing-library/react";
import { ThemeProvider } from "../ThemeProvider";
import { useTheme } from "../../hooks/useTheme";

describe("ThemeProvider", () => {
  let originalMatchMedia: typeof window.matchMedia;
  let matchMediaMock: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    localStorage.clear();
    originalMatchMedia = window.matchMedia;

    matchMediaMock = vi.fn((query: string) => ({
      matches: query === "(prefers-color-scheme: dark)",
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }));

    window.matchMedia = matchMediaMock as unknown as typeof window.matchMedia;
    document.documentElement.className = "";
  });

  afterEach(() => {
    window.matchMedia = originalMatchMedia;
  });

  it("initializes with light theme when localStorage has 'light'", () => {
    localStorage.setItem("theme", "light");

    const { result } = renderHook(() => useTheme(), {
      wrapper: ThemeProvider,
    });

    expect(result.current.theme).toBe("light");
    expect(document.documentElement.classList.contains("dark")).toBe(false);
  });

  it("initializes with dark theme when localStorage has 'dark'", () => {
    localStorage.setItem("theme", "dark");

    const { result } = renderHook(() => useTheme(), {
      wrapper: ThemeProvider,
    });

    expect(result.current.theme).toBe("dark");
    expect(document.documentElement.classList.contains("dark")).toBe(true);
  });

  it("initializes with system preference when no localStorage", () => {
    matchMediaMock.mockReturnValue({
      matches: true,
      media: "(prefers-color-scheme: dark)",
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    });

    const { result } = renderHook(() => useTheme(), {
      wrapper: ThemeProvider,
    });

    expect(result.current.theme).toBe("system");
    expect(document.documentElement.classList.contains("dark")).toBe(true);
  });

  it("updates localStorage and DOM when setTheme is called with 'dark'", async () => {
    localStorage.setItem("theme", "light");

    const { result } = renderHook(() => useTheme(), {
      wrapper: ThemeProvider,
    });

    act(() => {
      result.current.setTheme("dark");
    });

    await waitFor(() => {
      expect(localStorage.getItem("theme")).toBe("dark");
      expect(document.documentElement.classList.contains("dark")).toBe(true);
    });
  });

  it("updates localStorage and DOM when setTheme is called with 'light'", async () => {
    localStorage.setItem("theme", "dark");

    const { result } = renderHook(() => useTheme(), {
      wrapper: ThemeProvider,
    });

    act(() => {
      result.current.setTheme("light");
    });

    await waitFor(() => {
      expect(localStorage.getItem("theme")).toBe("light");
      expect(document.documentElement.classList.contains("dark")).toBe(false);
    });
  });

  it("listens to system preference changes when theme is 'system'", async () => {
    let listeners: ((event: MediaQueryListEvent) => void)[] = [];

    matchMediaMock.mockReturnValue({
      matches: false,
      media: "(prefers-color-scheme: dark)",
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn((event: string, listener: (event: MediaQueryListEvent) => void) => {
        if (event === "change") {
          listeners.push(listener);
        }
      }),
      removeEventListener: vi.fn((event: string, listener: (event: MediaQueryListEvent) => void) => {
        if (event === "change") {
          listeners = listeners.filter((l) => l !== listener);
        }
      }),
      dispatchEvent: vi.fn(),
    });

    const { result } = renderHook(() => useTheme(), {
      wrapper: ThemeProvider,
    });

    act(() => {
      result.current.setTheme("system");
    });

    await waitFor(() => {
      expect(document.documentElement.classList.contains("dark")).toBe(false);
    });

    act(() => {
      listeners.forEach((listener) => {
        listener({ matches: true } as MediaQueryListEvent);
      });
    });

    await waitFor(() => {
      expect(document.documentElement.classList.contains("dark")).toBe(true);
    });
  });

  it("removes system preference listener on unmount", () => {
    const removeEventListenerSpy = vi.fn();

    matchMediaMock.mockReturnValue({
      matches: false,
      media: "(prefers-color-scheme: dark)",
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: removeEventListenerSpy,
      dispatchEvent: vi.fn(),
    });

    const { unmount } = renderHook(() => useTheme(), {
      wrapper: ThemeProvider,
    });

    unmount();

    expect(removeEventListenerSpy).toHaveBeenCalled();
  });
});
