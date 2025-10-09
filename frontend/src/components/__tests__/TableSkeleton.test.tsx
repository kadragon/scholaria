import { describe, it, expect } from "vitest";
import { render } from "@testing-library/react";
import { TableSkeleton } from "../TableSkeleton";

describe("TableSkeleton", () => {
  it("should render with default props (8 rows, 5 columns)", () => {
    const { container } = render(<TableSkeleton />);

    const headerCells = container.querySelectorAll("thead tr th");
    expect(headerCells).toHaveLength(5);

    const bodyRows = container.querySelectorAll("tbody tr");
    expect(bodyRows).toHaveLength(8);

    bodyRows.forEach((row) => {
      const cells = row.querySelectorAll("td");
      expect(cells).toHaveLength(5);
    });
  });

  it("should render with custom rows", () => {
    const { container } = render(<TableSkeleton rows={3} />);

    const bodyRows = container.querySelectorAll("tbody tr");
    expect(bodyRows).toHaveLength(3);
  });

  it("should render with custom columns", () => {
    const { container } = render(<TableSkeleton columns={7} />);

    const headerCells = container.querySelectorAll("thead tr th");
    expect(headerCells).toHaveLength(7);

    const firstBodyRow = container.querySelector("tbody tr");
    const cells = firstBodyRow?.querySelectorAll("td");
    expect(cells).toHaveLength(7);
  });

  it("should render with custom rows and columns", () => {
    const { container } = render(<TableSkeleton rows={10} columns={3} />);

    const headerCells = container.querySelectorAll("thead tr th");
    expect(headerCells).toHaveLength(3);

    const bodyRows = container.querySelectorAll("tbody tr");
    expect(bodyRows).toHaveLength(10);
  });

  it("should contain Skeleton components", () => {
    const { container } = render(<TableSkeleton rows={1} columns={1} />);

    const skeletons = container.querySelectorAll('[class*="animate-pulse"]');
    expect(skeletons.length).toBeGreaterThan(0);
  });
});
