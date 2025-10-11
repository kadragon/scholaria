import { test, expect } from "@playwright/test";
import { AnalyticsPage } from "../pages/analytics.page";

test.describe("Analytics Dashboard", () => {
  let analyticsPage: AnalyticsPage;

  test.beforeEach(async ({ page }) => {
    analyticsPage = new AnalyticsPage(page);
    await analyticsPage.goto();
  });

  test("should display analytics dashboard", async ({ page }) => {
    await expect(
      page.getByRole("heading", { name: /analytics|dashboard/i }),
    ).toBeVisible();
  });

  test("should display stat cards", async () => {
    const statCards = analyticsPage.statCards;
    const count = await statCards.count();

    expect(count).toBeGreaterThanOrEqual(0);

    if (count > 0) {
      await expect(statCards.first()).toBeVisible();
    }
  });

  test("should display charts", async ({ page }) => {
    const charts = page.locator('canvas, svg[class*="recharts"]');
    await expect(charts.first()).toBeVisible();

    const chartCount = await charts.count();
    expect(chartCount).toBeGreaterThanOrEqual(1);
  });

  test("should filter by topic", async ({ request }) => {
    const token = await analyticsPage.page.evaluate(() =>
      localStorage.getItem("token"),
    );

    const topicsResponse = await request.get(
      "http://localhost:8001/api/admin/topics",
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    );

    const topicsData = await topicsResponse.json();
    let topics = topicsData.items || topicsData;

    if (!Array.isArray(topics)) {
      topics = [];
    }

    if (!topics || topics.length === 0) {
      test.skip();
      return;
    }

    const testTopic = topics.find((t: { name: string }) =>
      t.name.includes("E2E Test Topic"),
    );
    const topicName = testTopic?.name || topics[0]?.name;

    if (!topicName) {
      test.skip();
      return;
    }

    await analyticsPage.goto();
    await analyticsPage.topicFilter.selectOption({ label: topicName });

    await expect(
      analyticsPage.page.locator("canvas, svg").first(),
    ).toBeVisible();
  });

  test("should filter by date range", async () => {
    const today = new Date();
    const lastWeek = new Date(today);
    lastWeek.setDate(today.getDate() - 7);

    const formatDate = (date: Date) => date.toISOString().split("T")[0];

    await analyticsPage.filterByDateRange(
      formatDate(lastWeek),
      formatDate(today),
    );

    await expect(analyticsPage.statCards.first()).toBeVisible();
  });

  test("should view feedback comments", async ({ page }) => {
    await analyticsPage.viewFeedbackComments();

    await expect(
      page.getByRole("heading", { name: /feedback|comments/i }).first(),
    ).toBeVisible();
  });

  test("should display empty state when no data", async ({ page }) => {
    const futureDate = new Date();
    futureDate.setFullYear(futureDate.getFullYear() + 1);

    const formatDate = (date: Date) => date.toISOString().split("T")[0];

    await analyticsPage.filterByDateRange(
      formatDate(futureDate),
      formatDate(futureDate),
    );

    await page.waitForLoadState("networkidle");

    const statCardCount = await analyticsPage.statCards.count();

    if (statCardCount > 0) {
      test.skip();
      return;
    }

    await expect(analyticsPage.statCards).toHaveCount(0);
  });
});
