import { test, expect } from "@playwright/test";
import { ChatPage } from "../pages/chat.page";
import { TopicsPage } from "../pages/topics.page";
import { ContextsPage } from "../pages/contexts.page";
import { getApiUrl } from "../helpers/api";

test.describe("Chat Q&A", () => {
  let chatPage: ChatPage;
  let topicName: string;
  let contextName: string;

  test.beforeAll(async ({ browser }) => {
    const adminContext = await browser.newContext({
      storageState: "playwright/.auth/admin.json",
    });
    const page = await adminContext.newPage();
    const topicsPage = new TopicsPage(page);
    const contextsPage = new ContextsPage(page);

    topicName = `E2E Chat Test ${Date.now()}`;
    contextName = `E2E Chat Context ${Date.now()}`;

    await topicsPage.goto();
    await topicsPage.gotoCreate();

    await topicsPage.createTopic({
      name: topicName,
      description: "Topic seeded for chat E2E coverage.",
      systemPrompt: "You are a helpful assistant for E2E testing.",
    });

    await page.waitForURL("/admin/topics", { timeout: 60000 });
    await page.waitForLoadState("networkidle");

    await contextsPage.goto();
    await contextsPage.gotoCreate();
    await contextsPage.createMarkdownContext({
      name: contextName,
      description: "Context seeded for chat E2E coverage.",
      content: [
        "# Chat QA Context",
        "The capital of France is Paris.",
        "End-to-end testing validates complete user flows and feedback pathways.",
        "Provide concise, helpful responses suitable for regression checks.",
      ].join("\n"),
    });

    await page.waitForLoadState("networkidle");

    const token = await page.evaluate(() => localStorage.getItem("token"));
    if (!token) {
      throw new Error("Missing auth token for admin API access");
    }
    let createdContext: { id: string } | null = null;

    await expect
      .poll(
        async () => {
          const response = await page.request.get(getApiUrl(`/api/contexts`), {
            headers: { Authorization: `Bearer ${token}` },
            timeout: 10000,
          });
          if (!response.ok()) {
            return null;
          }
          const contexts = await response.json();
          const items = Array.isArray(contexts) ? contexts : [];
          if (items.length === 0) {
            return null;
          }
          createdContext = items.find(
            (context: { name: string }) => context.name === contextName,
          );
          return createdContext ?? null;
        },
        {
          message: `Expected context "${contextName}" to be available`,
          intervals: [2000, 4000, 6000],
          timeout: 60000,
        },
      )
      .not.toBeNull();

    if (!createdContext) {
      throw new Error(`Context "${contextName}" was not created`);
    }

    // Skip context processing status check for E2E tests
    // Focus on testing chat UI functionality

    const topicFilterParam = encodeURIComponent(
      JSON.stringify({ name: topicName }),
    );
    const topicResponse = await page.request.get(
      getApiUrl(`/api/admin/topics?limit=20&filter=${topicFilterParam}`),
      {
        headers: { Authorization: `Bearer ${token}` },
        timeout: 10000,
      },
    );
    if (!topicResponse.ok()) {
      throw new Error(`Failed to fetch topic "${topicName}"`);
    }
    const topicPayload = await topicResponse.json();
    const topicItems = Array.isArray(topicPayload?.data)
      ? topicPayload.data
      : Array.isArray(topicPayload?.items)
        ? topicPayload.items
        : [];
    const targetTopic = topicItems.find(
      (topic: { name: string }) => topic.name === topicName,
    );
    if (!targetTopic || !targetTopic.id) {
      throw new Error(`Topic "${topicName}" not found via admin API`);
    }

    const updateResponse = await page.request.patch(
      getApiUrl(`/api/admin/contexts/${createdContext.id}`),
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        data: JSON.stringify({ topic_ids: [targetTopic.id] }),
        timeout: 10000,
      },
    );
    expect(updateResponse.ok()).toBeTruthy();

    await expect
      .poll(
        async () => {
          const detailResponse = await page.request.get(
            getApiUrl(`/api/contexts/${createdContext?.id}`),
            {
              headers: { Authorization: `Bearer ${token}` },
              timeout: 10000,
            },
          );
          if (!detailResponse.ok()) {
            return null;
          }
          const contextData = await detailResponse.json();
          const status = contextData.processing_status;
          // Accept COMPLETED or PENDING (with chunks created)
          if (
            status === "COMPLETED" ||
            (status === "PENDING" && contextData.chunk_count > 0)
          ) {
            return status;
          }
          return null;
        },
        {
          message: `Expected context "${contextName}" to be processed (COMPLETED or PENDING with chunks)`,
          intervals: [2000, 4000, 6000],
          timeout: 30000,
        },
      )
      .not.toBeNull();

    await adminContext.close();
  });

  test.beforeEach(async ({ page }) => {
    chatPage = new ChatPage(page);
    await chatPage.goto();
  });

  test("should display chat interface", async () => {
    await expect(chatPage.topicSelector).toBeVisible();
    await expect(chatPage.messageInput).toBeVisible();
    await expect(chatPage.sendButton).toBeVisible();
  });

  test("should select a topic", async () => {
    await chatPage.selectTopic(topicName);
  });

  test("should send a message and receive response", async () => {
    await chatPage.selectTopic(topicName);

    const question = "What is the capital of France?";
    await chatPage.sendMessage(question);

    await chatPage.waitForResponse(30000);

    const userMessage = chatPage.getMessage("user", 0);
    await expect(userMessage).toContainText(question);

    const trimmedResponse = await chatPage.waitForAssistantContent(0);
    expect(trimmedResponse).not.toMatch(/error/i);
  });

  test("should submit positive feedback", async ({ page }) => {
    await chatPage.selectTopic(topicName);

    await chatPage.sendMessage("Tell me about testing");
    await chatPage.waitForResponse(45000);

    const trimmedResponse = await chatPage.waitForAssistantContent(0);
    expect(trimmedResponse).not.toMatch(/error/i);

    await chatPage.waitUntilInputEnabled();
    await expect(chatPage.feedbackThumbsUp.last()).toBeVisible({
      timeout: 20000,
    });

    await chatPage.submitFeedback("up");

    // Check that feedback was submitted - submit button should be enabled again
    await expect(page.getByTestId("feedback-submit-button")).toBeEnabled({
      timeout: 5000,
    });
  });

  test("should submit negative feedback with comment", async ({ page }) => {
    await chatPage.selectTopic(topicName);

    await chatPage.sendMessage("What is E2E testing?");
    await chatPage.waitForResponse(45000);

    const trimmedResponse = await chatPage.waitForAssistantContent(0);
    expect(trimmedResponse).not.toMatch(/error/i);

    await chatPage.waitUntilInputEnabled();
    await expect(chatPage.feedbackThumbsDown.last()).toBeVisible({
      timeout: 20000,
    });

    await chatPage.submitFeedback("down", "The response was not helpful.");

    // Check that feedback was submitted - submit button should be enabled again
    await expect(page.getByTestId("feedback-submit-button")).toBeEnabled({
      timeout: 5000,
    });
  });

  test("should persist session after reload", async ({ page }) => {
    await chatPage.selectTopic(topicName);

    await chatPage.sendMessage("Test message for session persistence");
    await chatPage.waitForResponse(45000);

    await chatPage.waitForAssistantContent(0);
    await chatPage.waitUntilInputEnabled();

    const sessionId = await page.evaluate(() =>
      sessionStorage.getItem("chat_session_id"),
    );
    expect(sessionId).toBeTruthy();

    await expect(
      chatPage.messageList.locator("text=Test message for session persistence"),
    ).toBeVisible({ timeout: 10000 });

    await page.reload();
    await page.waitForLoadState("networkidle");

    // Re-select the topic after reload
    await chatPage.selectTopic(topicName);

    const restoredSessionId = await page.evaluate(() =>
      sessionStorage.getItem("chat_session_id"),
    );
    expect(restoredSessionId).toBe(sessionId);

    // Note: Messages are not persisted in UI state across reloads
    // Session persistence ensures the same sessionId is used for continuity
  });

  test("should handle multiple messages in conversation", async () => {
    await chatPage.selectTopic(topicName);

    await chatPage.sendMessage("First question");
    await chatPage.waitForResponse(45000);

    await chatPage.waitForAssistantContent(0);
    await chatPage.waitUntilInputEnabled();

    await chatPage.sendMessage("Second question");
    await chatPage.waitForResponse(45000);

    await chatPage.waitForAssistantContent(1);

    await expect(
      chatPage.messageList.locator("text=First question"),
    ).toBeVisible();
    await expect(
      chatPage.messageList.locator("text=Second question"),
    ).toBeVisible();
  });
});
