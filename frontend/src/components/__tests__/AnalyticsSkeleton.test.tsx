import { describe, it, expect } from "vitest";
import { render } from "@testing-library/react";
import { AnalyticsSkeleton } from "../AnalyticsSkeleton";

describe("AnalyticsSkeleton", () => {
  it("스켈레톤 렌더링 검증", () => {
    const { container } = render(<AnalyticsSkeleton />);

    // Skeleton 컴포넌트들이 렌더링되었는지 확인
    const skeletons = container.querySelectorAll('[class*="animate-pulse"]');
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("카드 레이아웃 구조 검증", () => {
    const { container } = render(<AnalyticsSkeleton />);

    // grid 레이아웃 확인
    const grids = container.querySelectorAll('[class*="grid"]');
    expect(grids.length).toBeGreaterThan(0);

    // card 구조 확인 (bg-white rounded-lg shadow-md)
    const cards = container.querySelectorAll('[class*="bg-white"]');
    expect(cards.length).toBeGreaterThan(5); // 여러 개의 카드가 있어야 함
  });
});
