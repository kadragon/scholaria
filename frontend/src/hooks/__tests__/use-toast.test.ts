import { describe, it, expect, beforeEach, vi, afterEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useToast, toast } from "../use-toast";

describe("use-toast", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.useRealTimers();
  });

  it("should start with empty toasts", () => {
    const { result } = renderHook(() => useToast());

    expect(result.current.toasts).toEqual([]);
  });

  it("should add toast when toast() is called", () => {
    const { result } = renderHook(() => useToast());

    act(() => {
      toast({ title: "Test Toast" });
    });

    expect(result.current.toasts).toHaveLength(1);
    expect(result.current.toasts[0].title).toBe("Test Toast");
    expect(result.current.toasts[0].open).toBe(true);
  });

  it("should respect TOAST_LIMIT of 1", () => {
    const { result } = renderHook(() => useToast());

    act(() => {
      toast({ title: "First Toast" });
      toast({ title: "Second Toast" });
    });

    expect(result.current.toasts).toHaveLength(1);
    expect(result.current.toasts[0].title).toBe("Second Toast");
  });

  it("should dismiss toast when dismiss is called", () => {
    const { result } = renderHook(() => useToast());

    act(() => {
      toast({ title: "Test Toast" });
    });

    const toastId = result.current.toasts[0].id;

    act(() => {
      result.current.dismiss(toastId);
    });

    expect(result.current.toasts[0].open).toBe(false);
  });

  it("should remove toast after TOAST_REMOVE_DELAY when dismissed", () => {
    const { result } = renderHook(() => useToast());

    act(() => {
      toast({ title: "Test Toast" });
    });

    const toastId = result.current.toasts[0].id;

    act(() => {
      result.current.dismiss(toastId);
    });

    expect(result.current.toasts).toHaveLength(1);

    act(() => {
      vi.advanceTimersByTime(1000000);
    });

    expect(result.current.toasts).toHaveLength(0);
  });

  it("should share state across multiple useToast calls", () => {
    const { result: result1 } = renderHook(() => useToast());
    const { result: result2 } = renderHook(() => useToast());

    act(() => {
      toast({ title: "Shared Toast" });
    });

    expect(result1.current.toasts).toHaveLength(1);
    expect(result2.current.toasts).toHaveLength(1);
    expect(result1.current.toasts[0].id).toBe(result2.current.toasts[0].id);
  });

  it("should return toast methods from toast()", () => {
    const toastInstance = toast({ title: "Test" });

    expect(toastInstance).toHaveProperty("id");
    expect(toastInstance).toHaveProperty("dismiss");
    expect(toastInstance).toHaveProperty("update");
    expect(typeof toastInstance.dismiss).toBe("function");
    expect(typeof toastInstance.update).toBe("function");
  });
});
