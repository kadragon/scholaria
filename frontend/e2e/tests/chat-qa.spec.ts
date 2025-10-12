import { test, expect } from "@playwright/test";
import { ChatPage } from "../pages/chat.page";

test.describe("Chat Q&A", () => {
  let chatPage: ChatPage;
  let topicName: string;

  test.beforeAll(() => {
    // Use the topic created by auth setup instead of creating our own
    // The auth setup creates a topic with name "E2E Test Topic {timestamp}"
    // We'll find it dynamically in the test
    topicName = ""; // Will be set in the test
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

  test("should select a topic", async ({ page }) => {
    // Find a topic that starts with "E2E Test Topic"
    const topicButton = page
      .getByTestId("topic-selector-option")
      .filter({ hasText: /^E2E Test Topic/ })
      .first();
    await topicButton.waitFor({ state: "visible", timeout: 15000 });
    await topicButton.click();
    await expect(chatPage.messageInput).toBeEnabled({ timeout: 15000 });

    // Get the actual topic name that was selected
    topicName = (await topicButton.textContent()) || "";
  });

  test("should send a message and receive response", async () => {
    // Topic should already be selected from previous test

    const question = "What is the capital of France?";
    await chatPage.sendMessage(question);

    await chatPage.waitForResponse(30000);

    const userMessage = chatPage.getMessage("user", 0);
    await expect(userMessage).toContainText(question);

    const trimmedResponse = await chatPage.waitForAssistantContent(0);
    expect(trimmedResponse).not.toMatch(/error/i);
  });

  test("should submit positive feedback", async ({ page }) => {
    // Topic should already be selected from previous test

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
    // Topic should already be selected from previous test

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
    // Topic should already be selected from previous test

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
    // Topic should already be selected from previous test
    if (!topicName) {
      throw new Error("Topic not selected in previous test");
    }

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
