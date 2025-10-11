import { type Page, type Locator } from "@playwright/test";

export class AnalyticsPage {
  readonly page: Page;
  readonly statCards: Locator;
  readonly questionTrendsChart: Locator;
  readonly feedbackDistributionChart: Locator;
  readonly topicFilter: Locator;
  readonly dateRangeStart: Locator;
  readonly dateRangeEnd: Locator;
  readonly feedbackCommentsTab: Locator;
  readonly commentsTable: Locator;

  constructor(page: Page) {
    this.page = page;
    this.statCards = page.getByTestId("stat-card");
    this.questionTrendsChart = page.getByTestId("question-trends-chart");
    this.feedbackDistributionChart = page.getByTestId(
      "feedback-distribution-chart",
    );
    this.topicFilter = page.getByRole("combobox", { name: /토픽|topic/i });
    this.dateRangeStart = page.getByLabel(/시작.*날짜|start date/i);
    this.dateRangeEnd = page.getByLabel(/종료.*날짜|end date/i);
    this.feedbackCommentsTab = page.getByRole("tab", {
      name: /피드백|코멘트|feedback|comments/i,
    });
    this.commentsTable = page.getByRole("table");
  }

  async goto() {
    await this.page.goto("/admin/analytics");
  }

  async filterByTopic(topicName: string) {
    await this.topicFilter.click();
    await this.page.getByRole("option", { name: topicName }).click();
  }

  async filterByDateRange(startDate: string, endDate: string) {
    await this.dateRangeStart.fill(startDate);
    await this.dateRangeEnd.fill(endDate);
  }

  async viewFeedbackComments() {
    await this.feedbackCommentsTab.click();
  }

  getStatCard(index: number) {
    return this.statCards.nth(index);
  }
}
