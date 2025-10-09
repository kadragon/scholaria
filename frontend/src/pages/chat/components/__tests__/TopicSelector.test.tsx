import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TopicSelector } from "../TopicSelector";
import { server } from "../../../../__mocks__/msw/server";
import { http, HttpResponse } from "msw";

describe("TopicSelector", () => {
  it("토픽 목록 렌더링", async () => {
    const mockOnSelectTopic = vi.fn();

    render(
      <TopicSelector
        selectedTopicId={null}
        onSelectTopic={mockOnSelectTopic}
      />,
    );

    expect(screen.getByText("토픽 목록 로딩 중...")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("테스트 토픽")).toBeInTheDocument();
    });

    expect(screen.getByText("테스트용 토픽입니다")).toBeInTheDocument();
    expect(screen.getByText("두번째 토픽")).toBeInTheDocument();
    expect(screen.getByText("두번째 테스트 토픽")).toBeInTheDocument();
  });

  it("토픽 선택 시 onSelectTopic 콜백 호출", async () => {
    const mockOnSelectTopic = vi.fn();
    const user = userEvent.setup();

    render(
      <TopicSelector
        selectedTopicId={null}
        onSelectTopic={mockOnSelectTopic}
      />,
    );

    await waitFor(() => {
      expect(screen.getByText("테스트 토픽")).toBeInTheDocument();
    });

    await user.click(screen.getByText("테스트 토픽"));

    expect(mockOnSelectTopic).toHaveBeenCalledWith({
      id: 1,
      name: "테스트 토픽",
      slug: "test-topic",
      description: "테스트용 토픽입니다",
    });
  });

  it("에러 발생 시 에러 메시지 표시", async () => {
    server.use(
      http.get("/api/topics", () => {
        return HttpResponse.error();
      }),
    );

    const mockOnSelectTopic = vi.fn();

    render(
      <TopicSelector
        selectedTopicId={null}
        onSelectTopic={mockOnSelectTopic}
      />,
    );

    await waitFor(() => {
      expect(
        screen.getByText("토픽을 불러올 수 없습니다."),
      ).toBeInTheDocument();
    });
  });
});
