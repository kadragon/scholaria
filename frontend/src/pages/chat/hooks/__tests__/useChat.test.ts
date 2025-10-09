import { describe, it, expect, beforeEach, vi } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { useChat } from "../useChat";
import { server } from "../../../../__mocks__/msw/server";
import { http, HttpResponse } from "msw";

const API_URL = "http://localhost:8001/api";

function createSSEStream(
  events: Array<{
    type: string;
    content?: string;
    citations?: unknown;
    message?: string;
  }>,
) {
  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    start(controller) {
      for (const event of events) {
        const data = `data: ${JSON.stringify(event)}\n\n`;
        controller.enqueue(encoder.encode(data));
      }
      controller.close();
    },
  });
  return stream;
}

describe("useChat", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should initialize with empty messages", () => {
    const { result } = renderHook(() =>
      useChat({ topicId: 1, sessionId: "test-session", onError: vi.fn() }),
    );

    expect(result.current.messages).toEqual([]);
    expect(result.current.isStreaming).toBe(false);
  });

  it("should send message and stream response", async () => {
    server.use(
      http.post(`${API_URL}/rag/stream`, async () => {
        const stream = createSSEStream([
          { type: "answer_chunk", content: "Hello" },
          { type: "answer_chunk", content: " world" },
          {
            type: "citations",
            citations: [
              {
                context_item_id: 1,
                title: "Test",
                content: "Test content",
                score: 0.9,
                context_type: "markdown",
              },
            ],
          },
          { type: "done" },
        ]);

        return new HttpResponse(stream, {
          headers: { "Content-Type": "text/event-stream" },
        });
      }),
    );
    server.use(
      http.post(`${API_URL}/history`, async ({ request }) => {
        const body = await request.json();
        return HttpResponse.json({
          id: 42,
          topic_id: body.topic_id,
          question: body.question,
          answer: body.answer,
          session_id: body.session_id,
          feedback_score: 0,
          feedback_comment: null,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        });
      }),
    );

    const { result } = renderHook(() =>
      useChat({ topicId: 1, sessionId: "test-session", onError: vi.fn() }),
    );

    result.current.sendMessage("Test question");

    await waitFor(() => expect(result.current.messages.length).toBe(2));

    expect(result.current.messages[0].role).toBe("user");
    expect(result.current.messages[0].content).toBe("Test question");

    await waitFor(() => expect(result.current.isStreaming).toBe(false));

    expect(result.current.messages[1].role).toBe("assistant");
    expect(result.current.messages[1].content).toBe("Hello world");
    expect(result.current.messages[1].citations).toEqual([
      {
        context_item_id: 1,
        title: "Test",
        content: "Test content",
        score: 0.9,
        context_type: "markdown",
      },
    ]);
    expect(result.current.messages[1].historyId).toBe(42);
    expect(result.current.messages[1].feedbackScore).toBe(0);
    expect(result.current.messages[1].feedbackComment).toBeNull();
  });

  it("should handle error event from stream", async () => {
    const onError = vi.fn();

    server.use(
      http.post(`${API_URL}/rag/stream`, async () => {
        const stream = createSSEStream([
          { type: "error", message: "Stream error" },
        ]);

        return new HttpResponse(stream, {
          headers: { "Content-Type": "text/event-stream" },
        });
      }),
    );

    const { result } = renderHook(() =>
      useChat({ topicId: 1, sessionId: "test-session", onError }),
    );

    result.current.sendMessage("Test question");

    await waitFor(() => expect(onError).toHaveBeenCalled());
    expect(onError).toHaveBeenCalledWith(
      expect.objectContaining({ message: "Stream error" }),
    );
  });

  it("should handle network error", async () => {
    const onError = vi.fn();

    server.use(
      http.post(`${API_URL}/rag/stream`, () => {
        return HttpResponse.error();
      }),
    );

    const { result } = renderHook(() =>
      useChat({ topicId: 1, sessionId: "test-session", onError }),
    );

    result.current.sendMessage("Test question");

    await waitFor(() => expect(onError).toHaveBeenCalled());
    await waitFor(() => expect(result.current.isStreaming).toBe(false));
  });

  it("should clear messages", () => {
    const { result } = renderHook(() =>
      useChat({ topicId: 1, sessionId: "test-session", onError: vi.fn() }),
    );

    result.current.clearMessages();

    expect(result.current.messages).toEqual([]);
  });

  it("should not send message when topicId is null", async () => {
    const { result } = renderHook(() =>
      useChat({ topicId: null, sessionId: "test-session", onError: vi.fn() }),
    );

    result.current.sendMessage("Test question");

    await waitFor(() => expect(result.current.messages.length).toBe(0));
  });

  it("should not send empty message", async () => {
    const { result } = renderHook(() =>
      useChat({ topicId: 1, sessionId: "test-session", onError: vi.fn() }),
    );

    result.current.sendMessage("   ");

    await waitFor(() => expect(result.current.messages.length).toBe(0));
  });

  it("should not send message while streaming", async () => {
    let resolveStream: () => void;
    const streamPromise = new Promise<void>((resolve) => {
      resolveStream = resolve;
    });

    server.use(
      http.post(`${API_URL}/rag/stream`, async () => {
        await new Promise((resolve) => setTimeout(resolve, 50));

        const encoder = new TextEncoder();
        const stream = new ReadableStream({
          start(controller) {
            controller.enqueue(
              encoder.encode(
                `data: ${JSON.stringify({
                  type: "answer_chunk",
                  content: "Processing",
                })}\n\n`,
              ),
            );
            streamPromise.then(() => {
              controller.enqueue(
                encoder.encode(`data: ${JSON.stringify({ type: "done" })}\n\n`),
              );
              controller.close();
            });
          },
        });

        return new HttpResponse(stream, {
          headers: { "Content-Type": "text/event-stream" },
        });
      }),
    );

    const { result } = renderHook(() =>
      useChat({ topicId: 1, sessionId: "test-session", onError: vi.fn() }),
    );

    result.current.sendMessage("First message");

    await waitFor(() => expect(result.current.isStreaming).toBe(true), {
      timeout: 1000,
    });

    const messagesBefore = result.current.messages.length;
    result.current.sendMessage("Second message");

    expect(result.current.messages.length).toBe(messagesBefore);

    resolveStream!();
    await waitFor(() => expect(result.current.isStreaming).toBe(false));
  });
});
