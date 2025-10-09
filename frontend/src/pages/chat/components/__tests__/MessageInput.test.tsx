import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MessageInput } from "../MessageInput";

describe("MessageInput", () => {
  it("should enable send button when text is entered", async () => {
    const user = userEvent.setup();
    const mockOnSend = vi.fn();

    render(<MessageInput onSend={mockOnSend} />);

    const textarea = screen.getByPlaceholderText(/질문을 입력하세요/);
    const sendButton = screen.getByRole("button", { name: /전송/ });

    expect(sendButton).toBeDisabled();

    await user.type(textarea, "Hello");

    expect(sendButton).not.toBeDisabled();
  });

  it("should send message on Enter key", async () => {
    const user = userEvent.setup();
    const mockOnSend = vi.fn();

    render(<MessageInput onSend={mockOnSend} />);

    const textarea = screen.getByPlaceholderText(/질문을 입력하세요/);

    await user.type(textarea, "Test message{Enter}");

    expect(mockOnSend).toHaveBeenCalledWith("Test message");
  });

  it("should insert newline on Shift+Enter", async () => {
    const user = userEvent.setup();
    const mockOnSend = vi.fn();

    render(<MessageInput onSend={mockOnSend} />);

    const textarea = screen.getByPlaceholderText(
      /질문을 입력하세요/,
    ) as HTMLTextAreaElement;

    await user.type(textarea, "Line 1{Shift>}{Enter}{/Shift}Line 2");

    expect(textarea.value).toContain("Line 1\nLine 2");
    expect(mockOnSend).not.toHaveBeenCalled();
  });

  it("should clear input after sending", async () => {
    const user = userEvent.setup();
    const mockOnSend = vi.fn();

    render(<MessageInput onSend={mockOnSend} />);

    const textarea = screen.getByPlaceholderText(
      /질문을 입력하세요/,
    ) as HTMLTextAreaElement;
    const sendButton = screen.getByRole("button", { name: /전송/ });

    await user.type(textarea, "Test message");
    await user.click(sendButton);

    expect(textarea.value).toBe("");
  });

  it("should disable send button when isStreaming is true", () => {
    const mockOnSend = vi.fn();

    render(<MessageInput onSend={mockOnSend} isStreaming={true} />);

    const sendButton = screen.getByRole("button", { name: /전송/ });

    expect(sendButton).toBeDisabled();
  });
});
