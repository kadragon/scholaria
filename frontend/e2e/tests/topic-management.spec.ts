import { test, expect } from "@playwright/test";
import { TopicsPage } from "../pages/topics.page";
import { getApiUrl } from "../helpers/api";

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

    const response = await request.get(getApiUrl("/api/topics"));
    expect(response.ok()).toBeTruthy();
    const topics = await response.json();
    const createdTopic = topics.find(
      (t: { name: string }) => t.name === testTopicName,
    );
    expect(createdTopic).toBeDefined();
    expect(createdTopic.slug).toBe(testTopicSlug);
  });

  test("should edit an existing topic", async ({ page, request }) => {
    const token = await page.evaluate(() => localStorage.getItem("token"));
    if (!token) {
      throw new Error("Missing auth token for admin API access");
    }

    const originalName = `E2E Edit Topic ${Date.now()}`;
    const updatedName = `${originalName} (Updated)`;

    await topicsPage.gotoCreate();
    await topicsPage.createTopic({
      name: originalName,
      description: "Topic created for edit flow verification.",
      systemPrompt: "Respond with precise and concise answers.",
    });

    await page.waitForURL("/admin/topics", { timeout: 10000 });
    await page.waitForLoadState("networkidle");

    const filterParam = encodeURIComponent(
      JSON.stringify({ name: originalName }),
    );
    const createdTopicResponse = await request.get(
      getApiUrl(`/api/admin/topics?limit=20&filter=${filterParam}`),
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    );
    expect(createdTopicResponse.ok()).toBeTruthy();
    const createdTopicPayload = await createdTopicResponse.json();
    const createdTopicItems = Array.isArray(createdTopicPayload?.items)
      ? createdTopicPayload.items
      : Array.isArray(createdTopicPayload?.data)
        ? createdTopicPayload.data
        : Array.isArray(createdTopicPayload)
          ? createdTopicPayload
          : [];
    const createdTopic = createdTopicItems.find(
      (t: { name: string }) => t.name === originalName,
    );
    expect(createdTopic?.id).toBeDefined();

    await page.goto(`/admin/topics/edit/${createdTopic!.id}`);
    await page.waitForLoadState("networkidle");
    await expect(page).toHaveURL(
      new RegExp(`/admin/topics/edit/${createdTopic!.id}`),
    );

    await topicsPage.nameInput.clear();
    await topicsPage.nameInput.fill(updatedName);

    await topicsPage.submitButton.click();

    await page.waitForURL("/admin/topics", { timeout: 10000 });
    await page.waitForLoadState("networkidle");

    const verifyFilterParam = encodeURIComponent(
      JSON.stringify({ name: updatedName }),
    );
    const updatedResponse = await request.get(
      getApiUrl(`/api/admin/topics?limit=20&filter=${verifyFilterParam}`),
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    );
    expect(updatedResponse.ok()).toBeTruthy();

    const updatedData = await updatedResponse.json();
    const updatedItems = Array.isArray(updatedData?.items)
      ? updatedData.items
      : Array.isArray(updatedData?.data)
        ? updatedData.data
        : Array.isArray(updatedData)
          ? updatedData
          : [];

    const updatedTopic = updatedItems.find(
      (t: { name: string }) => t.name === updatedName,
    );

    expect(updatedTopic).toBeDefined();
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

    let response = await request.get(getApiUrl("/api/topics"));
    let topics = await response.json();
    const createdTopic = topics.find(
      (t: { name: string }) => t.name === tempTopicName,
    );
    expect(createdTopic).toBeDefined();
    const topicId = createdTopic.id;

    page.on("dialog", (dialog) => dialog.accept());

    const token = await page.evaluate(() => localStorage.getItem("token"));
    const deleteResponse = await request.delete(
      getApiUrl(`/api/admin/topics/${topicId}`),
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    );
    expect(deleteResponse.ok()).toBeTruthy();

    response = await request.get(getApiUrl("/api/topics"));
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

    const response = await request.get(getApiUrl("/api/topics"));
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
