import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Sidebar } from "../Sidebar";
import { BrowserRouter } from "react-router";

const mockLogout = vi.fn();

vi.mock("@refinedev/core", () => ({
  useLogout: () => ({ mutate: mockLogout }),
}));

describe("Sidebar", () => {
  beforeEach(() => {
    mockLogout.mockClear();
  });

  it("should render all menu items", () => {
    render(
      <BrowserRouter>
        <Sidebar />
      </BrowserRouter>,
    );

    expect(screen.getByText("토픽 관리")).toBeInTheDocument();
    expect(screen.getByText("컨텍스트 관리")).toBeInTheDocument();
    expect(screen.getByText("분석 대시보드")).toBeInTheDocument();
  });

  it("should apply active style to current route", () => {
    window.history.pushState({}, "", "/admin/topics");

    render(
      <BrowserRouter>
        <Sidebar />
      </BrowserRouter>,
    );

    const topicLink = screen.getByText("토픽 관리").closest("a");
    expect(topicLink).toHaveAttribute("aria-current", "page");
  });

  it("should call logout when logout button is clicked", async () => {
    const user = userEvent.setup();

    render(
      <BrowserRouter>
        <Sidebar />
      </BrowserRouter>,
    );

    const logoutButton = screen.getByText("로그아웃");
    await user.click(logoutButton);

    expect(mockLogout).toHaveBeenCalledOnce();
  });
});
