import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TopicCreate } from "../create";

const mockMutate = vi.fn();
const mockList = vi.fn();
const mockToast = vi.fn();

vi.mock("@refinedev/core", () => ({
  useCreate: vi.fn(() => ({ mutate: mockMutate, isLoading: false })),
  useNavigation: vi.fn(() => ({ list: mockList })),
}));

vi.mock("@/hooks/use-toast", () => ({
  useToast: vi.fn(() => ({ toast: mockToast })),
}));

describe("TopicCreate", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should render form fields", () => {
    render(<TopicCreate />);

    expect(screen.getByLabelText(/이름/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/슬러그/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/설명/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/시스템 프롬프트/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /생성/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /취소/i })).toBeInTheDocument();
  });

  it("should call mutate on form submission", async () => {
    const user = userEvent.setup();
    render(<TopicCreate />);

    const nameInput = screen.getByLabelText(/이름/i);
    const descInput = screen.getByLabelText(/설명/i);
    const promptInput = screen.getByLabelText(/시스템 프롬프트/i);
    const submitButton = screen.getByRole("button", { name: /생성/i });

    await user.type(nameInput, "Test Topic");
    await user.type(descInput, "Test Description");
    await user.type(promptInput, "Test System Prompt");
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockMutate).toHaveBeenCalledWith(
        expect.objectContaining({
          resource: "topics",
          values: expect.objectContaining({
            name: "Test Topic",
            description: "Test Description",
            system_prompt: "Test System Prompt",
          }),
        }),
        expect.any(Object),
      );
    });
  });

  it("should handle required field validation", async () => {
    const user = userEvent.setup();
    render(<TopicCreate />);

    const submitButton = screen.getByRole("button", { name: /생성/i });
    await user.click(submitButton);

    expect(mockMutate).not.toHaveBeenCalled();
  });

  it("should navigate to list on cancel", async () => {
    const user = userEvent.setup();
    render(<TopicCreate />);

    const cancelButton = screen.getByRole("button", { name: /취소/i });
    await user.click(cancelButton);

    expect(mockList).toHaveBeenCalledWith("topics");
  });

  it("should show success toast and redirect on successful creation", async () => {
    const user = userEvent.setup();
    mockMutate.mockImplementation((_, options) => {
      options.onSuccess();
    });

    render(<TopicCreate />);

    const nameInput = screen.getByLabelText(/이름/i);
    const promptInput = screen.getByLabelText(/시스템 프롬프트/i);
    const submitButton = screen.getByRole("button", { name: /생성/i });

    await user.type(nameInput, "Test Topic");
    await user.type(promptInput, "Test Prompt");
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith(
        expect.objectContaining({
          title: "생성 성공",
        }),
      );
      expect(mockList).toHaveBeenCalledWith("topics");
    });
  });
});
