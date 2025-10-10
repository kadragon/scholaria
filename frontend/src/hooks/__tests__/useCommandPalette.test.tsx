import { describe, it, expect } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useCommandPalette } from "../useCommandPalette";
import { MemoryRouter } from "react-router";

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <MemoryRouter>{children}</MemoryRouter>
);

describe("useCommandPalette", () => {
  it("초기 open 상태는 false", () => {
    const { result } = renderHook(() => useCommandPalette(), { wrapper });

    expect(result.current.open).toBe(false);
  });

  it("Cmd+K (Mac) 키 이벤트로 팔레트 토글", () => {
    const { result } = renderHook(() => useCommandPalette(), { wrapper });

    expect(result.current.open).toBe(false);

    // Cmd+K press
    act(() => {
      const event = new KeyboardEvent("keydown", {
        key: "k",
        metaKey: true,
      });
      document.dispatchEvent(event);
    });

    expect(result.current.open).toBe(true);

    // Cmd+K press again to close
    act(() => {
      const event = new KeyboardEvent("keydown", {
        key: "k",
        metaKey: true,
      });
      document.dispatchEvent(event);
    });

    expect(result.current.open).toBe(false);
  });

  it("Ctrl+K (Windows) 키 이벤트로 팔레트 토글", () => {
    const { result } = renderHook(() => useCommandPalette(), { wrapper });

    expect(result.current.open).toBe(false);

    // Ctrl+K press
    act(() => {
      const event = new KeyboardEvent("keydown", {
        key: "k",
        ctrlKey: true,
      });
      document.dispatchEvent(event);
    });

    expect(result.current.open).toBe(true);
  });
});
