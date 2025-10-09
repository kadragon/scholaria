import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { LoginPage } from "../login";
import { BrowserRouter } from "react-router-dom";
import { http, HttpResponse } from "msw";
import { server } from "../../__mocks__/msw/server";

const mockLogin = vi.fn();
const mockNavigate = vi.fn();
const mockToast = vi.fn();

vi.mock("@refinedev/core", () => ({
  useLogin: () => ({ mutate: mockLogin, isLoading: false }),
}));

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

vi.mock("@/hooks/use-toast", () => ({
  useToast: () => ({ toast: mockToast }),
}));

describe("LoginPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should render email and password fields", () => {
    server.use(
      http.get("http://localhost:8001/api/setup/check", () => {
        return HttpResponse.json({ needs_setup: false });
      }),
    );

    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>,
    );

    expect(
      screen.getByPlaceholderText("admin@example.com"),
    ).toBeInTheDocument();
    expect(screen.getByPlaceholderText("••••••••")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "로그인" })).toBeInTheDocument();
  });

  it("should redirect to setup when needs_setup is true", async () => {
    server.use(
      http.get("http://localhost:8001/api/setup/check", () => {
        return HttpResponse.json({ needs_setup: true });
      }),
    );

    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>,
    );

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith("/admin/setup");
    });
  });

  it("should call login on form submit", async () => {
    const user = userEvent.setup();

    server.use(
      http.get("http://localhost:8001/api/setup/check", () => {
        return HttpResponse.json({ needs_setup: false });
      }),
    );

    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>,
    );

    const emailInput = screen.getByPlaceholderText("admin@example.com");
    const passwordInput = screen.getByPlaceholderText("••••••••");
    const submitButton = screen.getByRole("button", { name: "로그인" });

    await user.type(emailInput, "test@example.com");
    await user.type(passwordInput, "password123");
    await user.click(submitButton);

    expect(mockLogin).toHaveBeenCalledWith(
      { email: "test@example.com", password: "password123" },
      expect.any(Object),
    );
  });

  it("should show error toast on login failure", async () => {
    const user = userEvent.setup();

    server.use(
      http.get("http://localhost:8001/api/setup/check", () => {
        return HttpResponse.json({ needs_setup: false });
      }),
    );

    mockLogin.mockImplementation((credentials, { onError }) => {
      onError();
    });

    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>,
    );

    const emailInput = screen.getByPlaceholderText("admin@example.com");
    const passwordInput = screen.getByPlaceholderText("••••••••");
    const submitButton = screen.getByRole("button", { name: "로그인" });

    await user.type(emailInput, "wrong@example.com");
    await user.type(passwordInput, "wrongpassword");
    await user.click(submitButton);

    expect(mockToast).toHaveBeenCalledWith({
      variant: "destructive",
      title: "로그인 실패",
      description: "이메일 또는 비밀번호가 올바르지 않습니다.",
    });
  });
});
