import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { userEvent } from "@testing-library/user-event";
import { ThemeToggle } from "../ThemeToggle";
import { ThemeProvider } from "../../providers/ThemeProvider";

describe("ThemeToggle", () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.className = "";

    window.matchMedia = vi.fn((query: string) => ({
      matches: query === "(prefers-color-scheme: dark)",
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })) as unknown as typeof window.matchMedia;
  });
  it("renders sun icon when theme is 'light'", () => {
    localStorage.setItem("theme", "light");

    render(
      <ThemeProvider>
        <ThemeToggle />
      </ThemeProvider>
    );

    const button = screen.getByRole("button", { name: /테마 전환/i });
    expect(button.textContent).toContain("☀️");
  });

  it("renders moon icon when theme is 'dark'", () => {
    localStorage.setItem("theme", "dark");

    render(
      <ThemeProvider>
        <ThemeToggle />
      </ThemeProvider>
    );

    const button = screen.getByRole("button", { name: /테마 전환/i });
    expect(button.textContent).toContain("🌙");
  });

  it("renders monitor icon when theme is 'system'", () => {
    localStorage.setItem("theme", "system");

    render(
      <ThemeProvider>
        <ThemeToggle />
      </ThemeProvider>
    );

    const button = screen.getByRole("button", { name: /테마 전환/i });
    expect(button.textContent).toContain("🖥️");
  });

  it("cycles through light → dark → system → light on click", async () => {
    const user = userEvent.setup();
    localStorage.setItem("theme", "light");

    render(
      <ThemeProvider>
        <ThemeToggle />
      </ThemeProvider>
    );

    const button = screen.getByRole("button", { name: /테마 전환/i });

    expect(button).toHaveTextContent("☀️");

    await user.click(button);
    expect(localStorage.getItem("theme")).toBe("dark");
    expect(button).toHaveTextContent("🌙");

    await user.click(button);
    expect(localStorage.getItem("theme")).toBe("system");
    expect(button).toHaveTextContent("🖥️");

    await user.click(button);
    expect(localStorage.getItem("theme")).toBe("light");
    expect(button).toHaveTextContent("☀️");
  });

  it("responds to keyboard Enter key", async () => {
    const user = userEvent.setup();
    localStorage.setItem("theme", "light");

    render(
      <ThemeProvider>
        <ThemeToggle />
      </ThemeProvider>
    );

    const button = screen.getByRole("button", { name: /테마 전환/i });
    button.focus();
    await user.keyboard("{Enter}");

    expect(localStorage.getItem("theme")).toBe("dark");
  });

  it("responds to keyboard Space key", async () => {
    const user = userEvent.setup();
    localStorage.setItem("theme", "light");

    render(
      <ThemeProvider>
        <ThemeToggle />
      </ThemeProvider>
    );

    const button = screen.getByRole("button", { name: /테마 전환/i });
    button.focus();
    await user.keyboard(" ");

    expect(localStorage.getItem("theme")).toBe("dark");
  });
});
