import { describe, it, expect, vi, afterEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";

import { FeedbackControls } from "../FeedbackControls";
import { apiClient } from "../../../../lib/apiClient";

vi.mock("../../../../hooks/use-toast", () => {
  const toast = vi.fn();
  return {
    useToast: () => ({ toast }),
  };
});

describe("FeedbackControls", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("submits feedback and notifies parent", async () => {
    const patchSpy = vi.spyOn(apiClient, "patch").mockResolvedValue(
      Promise.resolve({
        data: {
          id: 1,
          feedback_score: 1,
          feedback_comment: "정말 도움이 되었어요",
        },
      }) as unknown as ReturnType<typeof apiClient.patch>,
    );

    const onChange = vi.fn();

    render(
      <FeedbackControls
        historyId={1}
        initialScore={0}
        initialComment=""
        onChange={onChange}
      />,
    );

    fireEvent.click(screen.getByTestId("feedback-option-positive"));
    fireEvent.change(screen.getByPlaceholderText(/자유 서술 피드백/), {
      target: { value: "정말 도움이 되었어요" },
    });
    fireEvent.click(screen.getByRole("button", { name: /피드백 저장/ }));

    await waitFor(() => expect(patchSpy).toHaveBeenCalledTimes(1));
    expect(patchSpy).toHaveBeenCalledWith("/history/1/feedback", {
      feedback_score: 1,
      feedback_comment: "정말 도움이 되었어요",
    });

    expect(onChange).toHaveBeenCalledWith(1, "정말 도움이 되었어요");
  });
});
