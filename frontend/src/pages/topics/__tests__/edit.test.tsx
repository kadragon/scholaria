import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TopicEdit } from "../edit";

const mockMutate = vi.fn();
const mockList = vi.fn();
const mockToast = vi.fn();
const mockUseOne = vi.fn();

vi.mock("react-router", () => ({
  useParams: vi.fn(() => ({ id: "1" })),
}));

vi.mock("@refinedev/core", () => ({
  useOne: () => mockUseOne(),
  useUpdate: vi.fn(() => ({ mutate: mockMutate, isLoading: false })),
  useNavigation: vi.fn(() => ({ list: mockList })),
  useList: vi.fn(() => ({
    data: {
      data: [
        { id: 1, name: "Context 1" },
        { id: 2, name: "Context 2" },
      ],
    },
  })),
}));

vi.mock("@/hooks/use-toast", () => ({
  useToast: vi.fn(() => ({ toast: mockToast })),
}));

describe("TopicEdit", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseOne.mockReturnValue({
      data: {
        data: {
          id: 1,
          name: "Test Topic",
          slug: "test-topic",
          description: "Test Description",
          system_prompt: "Test Prompt",
          context_ids: [1, 2],
        },
      },
      isLoading: false,
    });
  });

  it("should show loading state", () => {
    mockUseOne.mockReturnValue({
      data: null,
      isLoading: true,
    });

    render(<TopicEdit />);
    expect(screen.getByText(/로딩 중.../i)).toBeInTheDocument();
  });

  it("should pre-fill form with existing topic data", async () => {
    render(<TopicEdit />);

    await waitFor(() => {
      expect(screen.getByDisplayValue("Test Topic")).toBeInTheDocument();
      expect(screen.getByDisplayValue("test-topic")).toBeInTheDocument();
      expect(screen.getByDisplayValue("Test Description")).toBeInTheDocument();
      expect(screen.getByDisplayValue("Test Prompt")).toBeInTheDocument();
    });
  });

  it("should call mutate on form submission", async () => {
    const user = userEvent.setup();
    render(<TopicEdit />);

    await waitFor(() => {
      expect(screen.getByDisplayValue("Test Topic")).toBeInTheDocument();
    });

    const nameInput = screen.getByLabelText(/이름/i);
    await user.clear(nameInput);
    await user.type(nameInput, "Updated Topic");

    const submitButton = screen.getByRole("button", { name: /업데이트/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockMutate).toHaveBeenCalledWith(
        expect.objectContaining({
          resource: "topics",
          id: "1",
          values: expect.objectContaining({
            name: "Updated Topic",
          }),
        }),
        expect.any(Object),
      );
    });
  });

  it("should navigate to list on cancel", async () => {
    const user = userEvent.setup();
    render(<TopicEdit />);

    await waitFor(() => {
      expect(screen.getByDisplayValue("Test Topic")).toBeInTheDocument();
    });

    const cancelButton = screen.getByRole("button", { name: /취소/i });
    await user.click(cancelButton);

    expect(mockList).toHaveBeenCalledWith("topics");
  });

  it("should show success toast and redirect on successful update", async () => {
    const user = userEvent.setup();
    mockMutate.mockImplementation((_, options) => {
      options.onSuccess();
    });

    render(<TopicEdit />);

    await waitFor(() => {
      expect(screen.getByDisplayValue("Test Topic")).toBeInTheDocument();
    });

    const submitButton = screen.getByRole("button", { name: /업데이트/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith(
        expect.objectContaining({
          title: "업데이트 성공",
        }),
      );
      expect(mockList).toHaveBeenCalledWith("topics");
    });
  });
});
