import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MessageList } from "../MessageList";
import type { Message } from "../../hooks/useChat";

const mockScrollIntoView = vi.fn();
Element.prototype.scrollIntoView = mockScrollIntoView;

describe("MessageList", () => {
  it("사용자/어시스턴트 메시지 렌더링", () => {
    const messages: Message[] = [
      {
        id: "1",
        role: "user",
        content: "Hello",
        timestamp: Date.now(),
      },
      {
        id: "2",
        role: "assistant",
        content: "Hi there!",
        timestamp: Date.now(),
      },
    ];

    render(<MessageList messages={messages} isStreaming={false} />);

    expect(screen.getByText("Hello")).toBeInTheDocument();
    expect(screen.getByText("Hi there!")).toBeInTheDocument();
  });

  it("Markdown 렌더링 (헤더, 리스트, 코드 블록)", () => {
    const messages: Message[] = [
      {
        id: "1",
        role: "assistant",
        content: "# Header\n\n- Item 1\n- Item 2\n\n`inline code`",
        timestamp: Date.now(),
      },
    ];

    render(<MessageList messages={messages} isStreaming={false} />);

    expect(screen.getByText("Header")).toBeInTheDocument();
    expect(screen.getByText("Item 1")).toBeInTheDocument();
    expect(screen.getByText("Item 2")).toBeInTheDocument();
    expect(screen.getByText("inline code")).toBeInTheDocument();
  });

  it("Citations 확장/축소 토글", async () => {
    const user = userEvent.setup();
    const messages: Message[] = [
      {
        id: "1",
        role: "assistant",
        content: "Answer",
        timestamp: Date.now(),
        citations: [
          {
            title: "Citation 1",
            content: "This is a long citation content that should be truncated",
            score: 0.95,
          },
        ],
      },
    ];

    render(<MessageList messages={messages} isStreaming={false} />);

    expect(screen.getByText("참고 자료 (1)")).toBeInTheDocument();

    // CollapsibleTrigger 클릭하여 citations 표시
    await user.click(screen.getByText("참고 자료 (1)"));

    expect(screen.getByText("Citation 1")).toBeInTheDocument();

    // Citation 클릭하여 확장
    await user.click(screen.getByText("Citation 1"));

    expect(screen.getByText("클릭하여 접기")).toBeInTheDocument();
  });

  it("FeedbackControls 통합 (historyId 있을 때)", () => {
    const mockOnFeedbackChange = vi.fn();
    const messages: Message[] = [
      {
        id: "1",
        role: "assistant",
        content: "Answer",
        timestamp: Date.now(),
        historyId: 123,
        feedbackScore: 1,
        feedbackComment: "",
      },
    ];

    render(
      <MessageList
        messages={messages}
        isStreaming={false}
        onFeedbackChange={mockOnFeedbackChange}
      />,
    );

    // FeedbackControls가 렌더링되었는지 확인 (좋아요 버튼 존재)
    expect(screen.getAllByRole("button").length).toBeGreaterThan(0);
  });

  it("스트리밍 중 로딩 인디케이터 표시", () => {
    render(<MessageList messages={[]} isStreaming={true} />);

    expect(screen.getByText("답변 생성 중...")).toBeInTheDocument();
  });

  it("자동 스크롤 (scrollIntoView 호출)", () => {
    const messages: Message[] = [
      {
        id: "1",
        role: "user",
        content: "Test",
        timestamp: Date.now(),
      },
    ];

    render(<MessageList messages={messages} isStreaming={false} />);

    expect(mockScrollIntoView).toHaveBeenCalled();
  });
});
