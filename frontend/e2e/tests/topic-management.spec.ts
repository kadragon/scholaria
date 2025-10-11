import { test, expect } from "@playwright/test";
import { TopicsPage } from "../pages/topics.page";

test.describe("Topic Management", () => {
  let topicsPage: TopicsPage;
  const testTopicName = `E2E Test Topic ${Date.now()}`;
  const testTopicSlug = `e2e-test-${Date.now()}`;

  test.beforeEach(async ({ page }) => {
    topicsPage = new TopicsPage(page);
    await topicsPage.goto();
  });

  test("should display topics list", async () => {
    await expect(topicsPage.table).toBeVisible();
    await expect(topicsPage.createButton).toBeVisible();
  });

  test("should create a new topic", async ({ page, request }) => {
    await topicsPage.gotoCreate();

    await topicsPage.createTopic({
      name: testTopicName,
      slug: testTopicSlug,
      description: "This is an E2E test topic",
      systemPrompt: "You are a helpful assistant for testing.",
    });

    await page.waitForURL("/admin/topics", { timeout: 10000 });
    await page.waitForLoadState("networkidle");

    const response = await request.get("http://localhost:8001/api/topics");
    expect(response.ok()).toBeTruthy();
    const topics = await response.json();
    const createdTopic = topics.find(
      (t: { name: string }) => t.name === testTopicName,
    );
    expect(createdTopic).toBeDefined();
    expect(createdTopic.slug).toBe(testTopicSlug);
  });

  test("should edit an existing topic", async ({ page }) => {
    await topicsPage.goto();

    const existingRow = topicsPage.table.locator("tr").nth(1);
    const topicName = await existingRow.locator("td").nth(1).textContent();

    if (!topicName) {
      test.skip();
    }

    await topicsPage.editTopic(topicName);

    const updatedName = `${topicName} (Updated)`;
    await topicsPage.nameInput.clear();
    await topicsPage.nameInput.fill(updatedName);

    await topicsPage.submitButton.click();

    await page.waitForURL("/admin/topics", { timeout: 10000 });

    await expect(topicsPage.getTopicRow(updatedName)).toBeVisible();
  });

  test("should delete a topic", async ({ page, request }) => {
    await topicsPage.gotoCreate();

    const tempTopicName = `Temp Topic ${Date.now()}`;
    await topicsPage.createTopic({
      name: tempTopicName,
      systemPrompt: "Temporary topic for deletion test",
    });

    await page.waitForURL("/admin/topics");
    await page.waitForLoadState("networkidle");

    let response = await request.get("http://localhost:8001/api/topics");
    let topics = await response.json();
    const createdTopic = topics.find(
      (t: { name: string }) => t.name === tempTopicName,
    );
    expect(createdTopic).toBeDefined();

    await topicsPage.goto();
    await topicsPage.searchTopic(tempTopicName);

    page.on("dialog", (dialog) => dialog.accept());

    const row = topicsPage.getTopicRow(tempTopicName);
    await expect(row).toBeVisible({ timeout: 15000 });

    await topicsPage.deleteTopic(tempTopicName);

    await expect(page.getByText(/성공|삭제/)).toBeVisible({
      timeout: 5000,
    });

    response = await request.get("http://localhost:8001/api/topics");
    topics = await response.json();
    const deletedTopic = topics.find(
      (t: { name: string }) => t.name === tempTopicName,
    );
    expect(deletedTopic).toBeUndefined();
  });

  test("should auto-generate slug from name", async ({ page, request }) => {
    await topicsPage.gotoCreate();

    const topicName = `Auto Slug Test ${Date.now()}`;
    await topicsPage.nameInput.fill(topicName);
    await topicsPage.systemPromptInput.fill("Test prompt");
    await topicsPage.submitButton.click();

    await page.waitForURL("/admin/topics", { timeout: 10000 });
    await page.waitForLoadState("networkidle");

    const response = await request.get("http://localhost:8001/api/topics");
    const topics = await response.json();
    const createdTopic = topics.find(
      (t: { name: string }) => t.name === topicName,
    );
    expect(createdTopic).toBeDefined();
    expect(createdTopic.slug).toMatch(/auto-slug-test/i);
  });

  test("should validate required fields", async ({ page }) => {
    await topicsPage.gotoCreate();

    await topicsPage.submitButton.click();

    await expect(page).toHaveURL(/\/create/, { timeout: 2000 });
  });
});
