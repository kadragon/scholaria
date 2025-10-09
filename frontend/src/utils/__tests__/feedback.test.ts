import { describe, expect, it } from "vitest";

import { getFeedbackMeta } from "../feedback";

describe("getFeedbackMeta", () => {
  it("returns positive metadata for positive scores", () => {
    const meta = getFeedbackMeta(1);
    expect(meta.label).toBe("좋아요");
    expect(meta.sentiment).toBe("positive");
    expect(meta.className).toContain("emerald");
  });

  it("returns neutral metadata for zero scores", () => {
    const meta = getFeedbackMeta(0);
    expect(meta.label).toBe("중립");
    expect(meta.sentiment).toBe("neutral");
    expect(meta.className).toContain("gray");
  });

  it("returns negative metadata for negative scores", () => {
    const meta = getFeedbackMeta(-1);
    expect(meta.label).toBe("싫어요");
    expect(meta.sentiment).toBe("negative");
    expect(meta.className).toContain("rose");
  });

  it("treats any positive value as positive sentiment", () => {
    const meta = getFeedbackMeta(5);
    expect(meta.sentiment).toBe("positive");
  });
});
