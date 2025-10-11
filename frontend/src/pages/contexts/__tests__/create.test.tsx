import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ContextCreate } from "../create";

const mockList = vi.fn();
const mockToast = vi.fn();

vi.mock("@refinedev/core", () => ({
  useNavigation: vi.fn(() => ({ list: mockList })),
}));

vi.mock("@/hooks/use-toast", () => ({
  useToast: vi.fn(() => ({ toast: mockToast })),
}));

vi.mock("@/lib/apiClient", () => ({
  apiClient: {
    post: vi.fn(),
    get: vi.fn(),
  },
}));

describe("ContextCreate", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should render form fields", () => {
    render(<ContextCreate />);

    expect(screen.getByLabelText(/이름/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/설명/i)).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /markdown/i })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /pdf/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /생성/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /취소/i })).toBeInTheDocument();
  });

  it("should show validation error when MARKDOWN content is missing", async () => {
    const user = userEvent.setup();
    render(<ContextCreate />);

    const nameInput = screen.getByLabelText(/이름/i);
    await user.type(nameInput, "Test Context");

    const submitButton = screen.getByRole("button", { name: /생성/i });
    await user.click(submitButton);

    expect(mockToast).toHaveBeenCalledWith(
      expect.objectContaining({
        title: "내용 필요",
        variant: "destructive",
      }),
    );
  });

  it("should navigate to list on cancel", async () => {
    const user = userEvent.setup();
    render(<ContextCreate />);

    const cancelButton = screen.getByRole("button", { name: /취소/i });
    await user.click(cancelButton);

    expect(mockList).toHaveBeenCalledWith("contexts");
  });

  it("should switch tabs", async () => {
    const user = userEvent.setup();
    render(<ContextCreate />);

    const pdfTab = screen.getByRole("tab", { name: /pdf/i });
    await user.click(pdfTab);

    expect(screen.getByLabelText(/pdf 파일/i)).toBeInTheDocument();
  });
});
