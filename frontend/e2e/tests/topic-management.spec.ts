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

  test("should create a new topic", async ({ page }) => {
    await topicsPage.gotoCreate();

    await topicsPage.createTopic({
      name: testTopicName,
      slug: testTopicSlug,
      description: "This is an E2E test topic",
      systemPrompt: "You are a helpful assistant for testing.",
    });

    await page.waitForURL("/admin/topics", { timeout: 10000 });

    const row = topicsPage.getTopicRow(testTopicName);
    await expect(row).toBeVisible();
    await expect(row).toContainText(testTopicSlug);
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

  test("should delete a topic", async ({ page }) => {
    await topicsPage.gotoCreate();

    const tempTopicName = `Temp Topic ${Date.now()}`;
    await topicsPage.createTopic({
      name: tempTopicName,
      systemPrompt: "Temporary topic for deletion test",
    });

    await page.waitForURL("/admin/topics");

    await topicsPage.deleteTopic(tempTopicName);

    await page.getByRole("button", { name: /confirm|delete|yes/i }).click();

    await expect(topicsPage.getTopicRow(tempTopicName)).not.toBeVisible();
  });

  test("should auto-generate slug from name", async ({ page }) => {
    await topicsPage.gotoCreate();

    const topicName = "Auto Slug Test Topic";
    await topicsPage.nameInput.fill(topicName);

    await topicsPage.nameInput.blur();
    await page.waitForTimeout(500);

    const slugValue = await topicsPage.slugInput.inputValue();
    expect(slugValue).toBe("auto-slug-test-topic");
  });

  test("should validate required fields", async ({ page }) => {
    await topicsPage.gotoCreate();

    await topicsPage.submitButton.click();

    await expect(
      page.getByText(/required|cannot be empty/i).first(),
    ).toBeVisible();
  });
});
