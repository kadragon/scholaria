import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TopicList } from "../list";

const mockTableQueryResult = {
  data: {
    data: [
      {
        id: 1,
        name: "Test Topic 1",
        slug: "test-topic-1",
        system_prompt: "Test prompt 1",
        contexts_count: 3,
      },
      {
        id: 2,
        name: "Test Topic 2",
        slug: "test-topic-2",
        system_prompt: "Test prompt 2",
        contexts_count: 0,
      },
    ],
    total: 2,
  },
  isLoading: false,
  refetch: vi.fn(),
};

const mockNavigate = vi.fn();
const mockDelete = vi.fn();
const mockUpdate = vi.fn();
const mockToast = vi.fn();

vi.mock("@refinedev/core", () => ({
  useTable: vi.fn(() => ({ tableQueryResult: mockTableQueryResult })),
  useNavigation: vi.fn(() => ({
    edit: mockNavigate,
    create: mockNavigate,
  })),
  useDelete: vi.fn(() => ({ mutate: mockDelete })),
  useUpdate: vi.fn(() => ({ mutate: mockUpdate })),
}));

vi.mock("@/hooks/use-toast", () => ({
  useToast: vi.fn(() => ({ toast: mockToast })),
}));

describe("TopicList", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders table with topic data", async () => {
    render(<TopicList />);

    await waitFor(() => {
      expect(screen.getByText("토픽 관리")).toBeInTheDocument();
      expect(screen.getByText("Test Topic 1")).toBeInTheDocument();
      expect(screen.getByText("Test Topic 2")).toBeInTheDocument();
      expect(screen.getByText("test-topic-1")).toBeInTheDocument();
      expect(screen.getByText("test-topic-2")).toBeInTheDocument();
    });
  });

  it("filters topics by search query", async () => {
    const user = userEvent.setup();
    render(<TopicList />);

    const searchInput = screen.getByPlaceholderText("토픽 검색...");
    await user.type(searchInput, "Topic 1");

    await waitFor(() => {
      expect(screen.getByText("Test Topic 1")).toBeInTheDocument();
      expect(screen.queryByText("Test Topic 2")).not.toBeInTheDocument();
    });
  });

  it("calls delete mutation when delete button clicked", async () => {
    const user = userEvent.setup();
    vi.spyOn(window, "confirm").mockReturnValue(true);

    render(<TopicList />);

    const deleteButtons = screen.getAllByText("삭제");
    await user.click(deleteButtons[0]);

    await waitFor(() => {
      expect(mockDelete).toHaveBeenCalledWith(
        {
          resource: "topics",
          id: 1,
        },
        expect.objectContaining({
          onSuccess: expect.any(Function),
        }),
      );
    });
  });

  it("shows loading skeleton when data is loading", async () => {
    const { useTable } = await import("@refinedev/core");
    const loadingQueryResult = {
      ...mockTableQueryResult,
      isLoading: true,
    };

    vi.mocked(useTable).mockReturnValueOnce({
      tableQueryResult: loadingQueryResult,
    });

    render(<TopicList />);

    expect(screen.getByRole("table")).toBeInTheDocument();
  });

  it("navigates to create page when create button clicked", async () => {
    const user = userEvent.setup();
    render(<TopicList />);

    const createButton = screen.getByText("토픽 생성");
    await user.click(createButton);

    expect(mockNavigate).toHaveBeenCalledWith("topics");
  });

  it("navigates to edit page when edit button clicked", async () => {
    const user = userEvent.setup();
    render(<TopicList />);

    const editButtons = screen.getAllByText("편집");
    await user.click(editButtons[0]);

    expect(mockNavigate).toHaveBeenCalledWith("topics", 1);
  });
});
