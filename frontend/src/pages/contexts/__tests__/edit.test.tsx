import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ContextEdit } from "../edit";

const mockMutate = vi.fn();
const mockList = vi.fn();
const mockToast = vi.fn();
const mockUseOne = vi.fn();

vi.mock("react-router", () => ({
  useParams: vi.fn(() => ({ id: "1" })),
}));

vi.mock("@refinedev/core", () => ({
  useOne: () => mockUseOne(),
  useUpdate: vi.fn(() => ({ mutate: mockMutate })),
  useNavigation: vi.fn(() => ({ list: mockList })),
  useList: vi.fn(() => ({
    data: {
      data: [
        { id: 1, name: "Topic 1", slug: "topic-1" },
        { id: 2, name: "Topic 2", slug: "topic-2" },
      ],
    },
  })),
}));

vi.mock("@/hooks/use-toast", () => ({
  useToast: vi.fn(() => ({ toast: mockToast })),
}));

describe("ContextEdit", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseOne.mockReturnValue({
      data: {
        data: {
          id: 1,
          name: "Test Context",
          description: "Test Description",
          original_content: "Test Content",
          context_type: "MARKDOWN",
          topics: [{ id: 1, name: "Topic 1" }],
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

    render(<ContextEdit />);
    expect(screen.getByText(/로딩 중.../i)).toBeInTheDocument();
  });

  it("should pre-fill form with existing context data", async () => {
    render(<ContextEdit />);

    await waitFor(() => {
      expect(screen.getByDisplayValue("Test Context")).toBeInTheDocument();
      expect(screen.getByDisplayValue("Test Description")).toBeInTheDocument();
      expect(screen.getByDisplayValue("Test Content")).toBeInTheDocument();
    });
  });

  it("should call mutate on form submission", async () => {
    const user = userEvent.setup();
    render(<ContextEdit />);

    await waitFor(() => {
      expect(screen.getByDisplayValue("Test Context")).toBeInTheDocument();
    });

    const nameInput = screen.getByLabelText(/이름/i);
    await user.clear(nameInput);
    await user.type(nameInput, "Updated Context");

    const submitButton = screen.getByRole("button", { name: /저장/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockMutate).toHaveBeenCalledWith(
        expect.objectContaining({
          resource: "contexts",
          id: "1",
          values: expect.objectContaining({
            name: "Updated Context",
          }),
        }),
        expect.any(Object),
      );
    });
  });

  it("should navigate to list on cancel", async () => {
    const user = userEvent.setup();
    render(<ContextEdit />);

    await waitFor(() => {
      expect(screen.getByDisplayValue("Test Context")).toBeInTheDocument();
    });

    const cancelButton = screen.getByRole("button", { name: /취소/i });
    await user.click(cancelButton);

    expect(mockList).toHaveBeenCalledWith("contexts");
  });

  it("should show success toast and redirect on successful update", async () => {
    const user = userEvent.setup();
    mockMutate.mockImplementation((_, options) => {
      options.onSuccess();
    });

    render(<ContextEdit />);

    await waitFor(() => {
      expect(screen.getByDisplayValue("Test Context")).toBeInTheDocument();
    });

    const submitButton = screen.getByRole("button", { name: /저장/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith(
        expect.objectContaining({
          title: "업데이트 성공",
        }),
      );
      expect(mockList).toHaveBeenCalledWith("contexts");
    });
  });
});
