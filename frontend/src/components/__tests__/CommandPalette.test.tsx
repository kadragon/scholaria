import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { CommandPalette } from "../CommandPalette";
import { BrowserRouter } from "react-router-dom";

const mockNavigate = vi.fn();

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe("CommandPalette", () => {
  beforeEach(() => {
    mockNavigate.mockClear();
  });

  it("should not render when open is false", () => {
    render(
      <BrowserRouter>
        <CommandPalette open={false} onOpenChange={vi.fn()} />
      </BrowserRouter>,
    );

    expect(
      screen.queryByPlaceholderText("명령어 또는 페이지 검색..."),
    ).not.toBeInTheDocument();
  });

  it("should render when open is true", () => {
    render(
      <BrowserRouter>
        <CommandPalette open={true} onOpenChange={vi.fn()} />
      </BrowserRouter>,
    );

    expect(
      screen.getByPlaceholderText("명령어 또는 페이지 검색..."),
    ).toBeInTheDocument();
  });

  it("should navigate to topics page when topic command is selected", async () => {
    const user = userEvent.setup();
    const onOpenChange = vi.fn();

    render(
      <BrowserRouter>
        <CommandPalette open={true} onOpenChange={onOpenChange} />
      </BrowserRouter>,
    );

    await user.click(screen.getByText("토픽 관리"));

    expect(mockNavigate).toHaveBeenCalledWith("/admin/topics");
    expect(onOpenChange).toHaveBeenCalledWith(false);
  });

  it("should navigate to contexts page when context command is selected", async () => {
    const user = userEvent.setup();
    const onOpenChange = vi.fn();

    render(
      <BrowserRouter>
        <CommandPalette open={true} onOpenChange={onOpenChange} />
      </BrowserRouter>,
    );

    await user.click(screen.getByText("컨텍스트 관리"));

    expect(mockNavigate).toHaveBeenCalledWith("/admin/contexts");
    expect(onOpenChange).toHaveBeenCalledWith(false);
  });

  it("should navigate to analytics page", async () => {
    const user = userEvent.setup();

    render(
      <BrowserRouter>
        <CommandPalette open={true} onOpenChange={vi.fn()} />
      </BrowserRouter>,
    );

    await user.click(screen.getByText("분석 대시보드"));

    expect(mockNavigate).toHaveBeenCalledWith("/admin/analytics");
  });

  it("should navigate to chat page", async () => {
    const user = userEvent.setup();

    render(
      <BrowserRouter>
        <CommandPalette open={true} onOpenChange={vi.fn()} />
      </BrowserRouter>,
    );

    await user.click(screen.getByText("채팅"));

    expect(mockNavigate).toHaveBeenCalledWith("/chat");
  });

  it("should navigate to topic create page", async () => {
    const user = userEvent.setup();

    render(
      <BrowserRouter>
        <CommandPalette open={true} onOpenChange={vi.fn()} />
      </BrowserRouter>,
    );

    await user.click(screen.getByText("토픽 생성"));

    expect(mockNavigate).toHaveBeenCalledWith("/admin/topics/create");
  });

  it("should navigate to context create page", async () => {
    const user = userEvent.setup();

    render(
      <BrowserRouter>
        <CommandPalette open={true} onOpenChange={vi.fn()} />
      </BrowserRouter>,
    );

    await user.click(screen.getByText("컨텍스트 생성"));

    expect(mockNavigate).toHaveBeenCalledWith("/admin/contexts/create");
  });
});
