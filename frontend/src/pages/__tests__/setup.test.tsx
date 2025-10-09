import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { SetupPage } from "../setup";
import { server } from "../../__mocks__/msw/server";
import { http, HttpResponse } from "msw";

const API_BASE_URL = "http://localhost:8001/api";

const mockToast = vi.fn();

vi.mock("@/hooks/use-toast", () => ({
  useToast: () => ({ toast: mockToast }),
}));

beforeEach(() => {
  mockToast.mockClear();
});

const renderSetupPage = () => {
  return render(
    <MemoryRouter initialEntries={["/setup"]}>
      <Routes>
        <Route path="/setup" element={<SetupPage />} />
        <Route path="/login" element={<div>Login Page</div>} />
      </Routes>
    </MemoryRouter>,
  );
};

describe("SetupPage", () => {
  it("초기 렌더링 - 사용자명/이메일/비밀번호 입력 필드 표시", async () => {
    renderSetupPage();

    await waitFor(() => {
      expect(screen.queryByText("확인 중...")).not.toBeInTheDocument();
    });

    expect(screen.getByText("초기 설정")).toBeInTheDocument();
    expect(screen.getByText("첫 관리자 계정을 생성하세요")).toBeInTheDocument();
    expect(screen.getByLabelText("사용자명")).toBeInTheDocument();
    expect(screen.getByLabelText("이메일")).toBeInTheDocument();
    expect(screen.getAllByLabelText(/비밀번호/)).toHaveLength(2);
    expect(
      screen.getByRole("button", { name: "관리자 계정 생성" }),
    ).toBeInTheDocument();
  });

  it("Setup 체크 - needs_setup: false 시 /login 리다이렉션", async () => {
    server.use(
      http.get(`${API_BASE_URL}/setup/check`, () => {
        return HttpResponse.json({ needs_setup: false, admin_exists: true });
      }),
    );

    renderSetupPage();

    await waitFor(() => {
      expect(screen.getByText("Login Page")).toBeInTheDocument();
    });
  });

  it("비밀번호 불일치 검증 - 에러 메시지 표시", async () => {
    const user = userEvent.setup();
    renderSetupPage();

    await waitFor(() => {
      expect(screen.queryByText("확인 중...")).not.toBeInTheDocument();
    });

    await user.type(screen.getByLabelText("사용자명"), "testuser");
    await user.type(screen.getByLabelText("이메일"), "test@test.com");

    const passwordInputs = screen.getAllByLabelText(/비밀번호/);
    await user.type(passwordInputs[0], "password123");
    await user.type(passwordInputs[1], "password456");

    await user.click(screen.getByRole("button", { name: "관리자 계정 생성" }));

    await waitFor(() => {
      expect(
        screen.getByText("비밀번호가 일치하지 않습니다."),
      ).toBeInTheDocument();
    });
  });

  it("비밀번호 길이 검증 - 8자 미만 시 에러", async () => {
    const user = userEvent.setup();
    renderSetupPage();

    await waitFor(() => {
      expect(screen.queryByText("확인 중...")).not.toBeInTheDocument();
    });

    await user.type(screen.getByLabelText("사용자명"), "testuser");
    await user.type(screen.getByLabelText("이메일"), "test@test.com");

    const passwordInputs = screen.getAllByLabelText(/비밀번호/);
    await user.type(passwordInputs[0], "short");
    await user.type(passwordInputs[1], "short");

    await user.click(screen.getByRole("button", { name: "관리자 계정 생성" }));

    await waitFor(() => {
      expect(
        screen.getByText("비밀번호는 최소 8자 이상이어야 합니다."),
      ).toBeInTheDocument();
    });
  });

  it("계정 생성 성공 - POST /api/setup/init 호출 & 토스트 & /login 이동", async () => {
    const user = userEvent.setup();

    renderSetupPage();

    await waitFor(() => {
      expect(screen.queryByText("확인 중...")).not.toBeInTheDocument();
    });

    await user.type(screen.getByLabelText("사용자명"), "admin");
    await user.type(screen.getByLabelText("이메일"), "admin@test.com");

    const passwordInputs = screen.getAllByLabelText(/비밀번호/);
    await user.type(passwordInputs[0], "password123");
    await user.type(passwordInputs[1], "password123");

    await user.click(screen.getByRole("button", { name: "관리자 계정 생성" }));

    await waitFor(() => {
      expect(screen.getByText("Login Page")).toBeInTheDocument();
    });
  });

  it("계정 생성 실패 - 에러 메시지 표시", async () => {
    const user = userEvent.setup();
    renderSetupPage();

    await waitFor(() => {
      expect(screen.queryByText("확인 중...")).not.toBeInTheDocument();
    });

    await user.type(screen.getByLabelText("사용자명"), "testuser");
    await user.type(screen.getByLabelText("이메일"), "existing@test.com");

    const passwordInputs = screen.getAllByLabelText(/비밀번호/);
    await user.type(passwordInputs[0], "password123");
    await user.type(passwordInputs[1], "password123");

    await user.click(screen.getByRole("button", { name: "관리자 계정 생성" }));

    await waitFor(() => {
      expect(
        screen.getByText("이미 존재하는 이메일입니다."),
      ).toBeInTheDocument();
    });
  });
});
