import { test, expect } from "@playwright/test";
import { ChatPage } from "../pages/chat.page";
import { TopicsPage } from "../pages/topics.page";

test.describe("Chat Q&A", () => {
  let chatPage: ChatPage;
  let topicName: string;

  test.beforeAll(async ({ browser }) => {
    const page = await browser.newPage();
    const topicsPage = new TopicsPage(page);

    topicName = `E2E Chat Test ${Date.now()}`;

    await topicsPage.goto();
    await topicsPage.gotoCreate();

    await topicsPage.createTopic({
      name: topicName,
      systemPrompt: "You are a helpful assistant for E2E testing.",
    });

    await page.waitForURL("/admin/topics");
    await page.close();
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

    const assistantMessage = chatPage.getMessage("assistant", 0);
    await expect(assistantMessage).toBeVisible();
  });

  test("should submit positive feedback", async ({ page }) => {
    await chatPage.selectTopic(topicName);

    await chatPage.sendMessage("Tell me about testing");
    await chatPage.waitForResponse(30000);

    await chatPage.submitFeedback("up");

    await expect(page.getByText(/feedback submitted|thank you/i)).toBeVisible({
      timeout: 5000,
    });
  });

  test("should submit negative feedback with comment", async ({ page }) => {
    await chatPage.selectTopic(topicName);

    await chatPage.sendMessage("What is E2E testing?");
    await chatPage.waitForResponse(30000);

    await chatPage.submitFeedback("down", "The response was not helpful.");

    await expect(page.getByText(/feedback submitted|thank you/i)).toBeVisible({
      timeout: 5000,
    });
  });

  test("should persist session after reload", async ({ page }) => {
    await chatPage.selectTopic(topicName);

    await chatPage.sendMessage("Test message for session persistence");
    await chatPage.waitForResponse(30000);

    await page.reload();
    await page.waitForLoadState("networkidle");

    const userMessage = chatPage.getMessage("user", 0);
    await expect(userMessage).toContainText(
      "Test message for session persistence",
      { timeout: 10000 },
    );
  });

  test("should handle multiple messages in conversation", async () => {
    await chatPage.selectTopic(topicName);

    await chatPage.sendMessage("First question");
    await chatPage.waitForResponse(30000);

    await chatPage.sendMessage("Second question");
    await chatPage.waitForResponse(30000);

    const userMessages = chatPage.messageList.locator(
      ".bg-gradient-to-br.from-primary-600.to-primary-700",
    );
    await expect(userMessages).toHaveCount(2);

    const assistantMessages = chatPage.messageList.locator(
      ".bg-white.border-2.border-secondary-100",
    );
    await expect(assistantMessages).toHaveCount(2);
  });
});
