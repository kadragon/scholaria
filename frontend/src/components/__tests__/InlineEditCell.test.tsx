import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { InlineEditCell } from "../InlineEditCell";

describe("InlineEditCell", () => {
  it("should render value in view mode by default", () => {
    render(<InlineEditCell value="Test Value" onSave={vi.fn()} />);

    expect(screen.getByText("Test Value")).toBeInTheDocument();
    expect(screen.queryByRole("textbox")).not.toBeInTheDocument();
  });

  it("should enter edit mode on double click", async () => {
    const user = userEvent.setup();
    render(<InlineEditCell value="Test Value" onSave={vi.fn()} />);

    await user.dblClick(screen.getByText("Test Value"));

    const input = screen.getByRole("textbox");
    expect(input).toBeInTheDocument();
    expect(input).toHaveValue("Test Value");
  });

  it("should save on Enter key", async () => {
    const user = userEvent.setup();
    const onSave = vi.fn();
    render(<InlineEditCell value="Old Value" onSave={onSave} />);

    await user.dblClick(screen.getByText("Old Value"));
    const input = screen.getByRole("textbox");
    await user.clear(input);
    await user.type(input, "New Value{Enter}");

    expect(onSave).toHaveBeenCalledWith("New Value");
    expect(screen.queryByRole("textbox")).not.toBeInTheDocument();
  });

  it("should cancel on Escape key", async () => {
    const user = userEvent.setup();
    const onSave = vi.fn();
    render(<InlineEditCell value="Original" onSave={onSave} />);

    await user.dblClick(screen.getByText("Original"));
    const input = screen.getByRole("textbox");
    await user.clear(input);
    await user.type(input, "Modified{Escape}");

    expect(onSave).not.toHaveBeenCalled();
    expect(screen.getByText("Original")).toBeInTheDocument();
    expect(screen.queryByRole("textbox")).not.toBeInTheDocument();
  });

  it("should save on blur", async () => {
    const user = userEvent.setup();
    const onSave = vi.fn();
    render(
      <div>
        <InlineEditCell value="Old Value" onSave={onSave} />
        <button>Outside</button>
      </div>,
    );

    await user.dblClick(screen.getByText("Old Value"));
    const input = screen.getByRole("textbox");
    await user.clear(input);
    await user.type(input, "New Value");
    await user.click(screen.getByRole("button", { name: "Outside" }));

    expect(onSave).toHaveBeenCalledWith("New Value");
  });

  it("should not save empty value", async () => {
    const user = userEvent.setup();
    const onSave = vi.fn();
    render(<InlineEditCell value="Original" onSave={onSave} />);

    await user.dblClick(screen.getByText("Original"));
    const input = screen.getByRole("textbox");
    await user.clear(input);
    await user.type(input, "{Enter}");

    expect(onSave).not.toHaveBeenCalled();
  });

  it("should not save whitespace-only value", async () => {
    const user = userEvent.setup();
    const onSave = vi.fn();
    render(<InlineEditCell value="Original" onSave={onSave} />);

    await user.dblClick(screen.getByText("Original"));
    const input = screen.getByRole("textbox");
    await user.clear(input);
    await user.type(input, "   {Enter}");

    expect(onSave).not.toHaveBeenCalled();
  });

  it("should not save if value unchanged", async () => {
    const user = userEvent.setup();
    const onSave = vi.fn();
    render(<InlineEditCell value="Same Value" onSave={onSave} />);

    await user.dblClick(screen.getByText("Same Value"));
    const input = screen.getByRole("textbox");
    await user.type(input, "{Enter}");

    expect(onSave).not.toHaveBeenCalled();
  });
});
