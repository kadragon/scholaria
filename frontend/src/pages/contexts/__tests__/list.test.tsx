import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ContextList } from "../list";

const mockTableQueryResult = {
  data: {
    data: [
      {
        id: 1,
        name: "Test Context 1",
        context_type: "PDF",
        processing_status: "COMPLETED",
        description: "Test description 1",
        topics: [{ id: 1, name: "Topic 1" }],
      },
      {
        id: 2,
        name: "Test Context 2",
        context_type: "FAQ",
        processing_status: "PENDING",
        description: "Test description 2",
        topics: [],
      },
    ],
    total: 2,
  },
  isLoading: false,
  refetch: vi.fn(),
};

const mockTopicsData = {
  data: [
    { id: 1, name: "Topic 1", slug: "topic-1" },
    { id: 2, name: "Topic 2", slug: "topic-2" },
  ],
};

const mockNavigate = vi.fn();
const mockDelete = vi.fn();
const mockUpdate = vi.fn();
const mockToast = vi.fn();

vi.mock("@refinedev/core", () => ({
  useTable: vi.fn(() => ({ tableQueryResult: mockTableQueryResult })),
  useList: vi.fn(() => ({ data: mockTopicsData })),
  useNavigation: vi.fn(() => ({
    edit: mockNavigate,
    create: mockNavigate,
    show: mockNavigate,
  })),
  useDelete: vi.fn(() => ({ mutate: mockDelete })),
  useUpdate: vi.fn(() => ({ mutate: mockUpdate })),
}));

vi.mock("@/hooks/use-toast", () => ({
  useToast: vi.fn(() => ({ toast: mockToast })),
}));

describe("ContextList", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders table with context data", async () => {
    render(<ContextList />);

    await waitFor(() => {
      expect(screen.getByText("컨텍스트 관리")).toBeInTheDocument();
      expect(screen.getByText("Test Context 1")).toBeInTheDocument();
      expect(screen.getByText("Test Context 2")).toBeInTheDocument();
    });
  });

  it("renders type filter button", async () => {
    render(<ContextList />);

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /타입/i })).toBeInTheDocument();
    });
  });

  it("renders status filter button", async () => {
    render(<ContextList />);

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /상태/i })).toBeInTheDocument();
    });
  });

  it("calls delete mutation when delete button clicked", async () => {
    const user = userEvent.setup();
    vi.spyOn(window, "confirm").mockReturnValue(true);

    render(<ContextList />);

    const deleteButtons = screen.getAllByText("삭제");
    await user.click(deleteButtons[0]);

    await waitFor(() => {
      expect(mockDelete).toHaveBeenCalled();
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

    render(<ContextList />);

    expect(screen.getByRole("table")).toBeInTheDocument();
  });

  it("navigates to edit page when edit button clicked", async () => {
    const user = userEvent.setup();
    render(<ContextList />);

    const editButtons = screen.getAllByText("편집");
    await user.click(editButtons[0]);

    expect(mockNavigate).toHaveBeenCalledWith("contexts", 1);
  });
});
