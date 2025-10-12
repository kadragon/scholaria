import { type Page, type Locator, expect } from "@playwright/test";

export class ChatPage {
  readonly page: Page;
  readonly topicSelector: Locator;
  readonly messageInput: Locator;
  readonly sendButton: Locator;
  readonly messageList: Locator;
  readonly feedbackThumbsUp: Locator;
  readonly feedbackThumbsDown: Locator;
  readonly feedbackCommentInput: Locator;

  constructor(page: Page) {
    this.page = page;
    this.topicSelector = page.getByTestId("topic-selector-option");
    this.messageInput = page.getByPlaceholder(
      /질문을 입력하세요... \(Enter: 전송, Shift\+Enter: 줄바꿈\)/i,
    );
    this.sendButton = page.getByRole("button", { name: /전송|send/i });
    this.messageList = page.getByTestId("chat-message-list");
    this.feedbackThumbsUp = page.getByTestId("feedback-option-positive");
    this.feedbackThumbsDown = page.getByTestId("feedback-option-negative");
    this.feedbackCommentInput = page.getByTestId("feedback-comment-input");
  }

  async goto() {
    await this.page.goto("/chat");
  }

  async selectTopic(topicName: string) {
    const topicButton = this.page
      .getByTestId("topic-selector-option")
      .filter({ hasText: topicName })
      .first();
    await topicButton.waitFor({ state: "visible", timeout: 15000 });
    await topicButton.click();
    await expect(this.messageInput).toBeEnabled({ timeout: 15000 });
  }

  async sendMessage(message: string) {
    await this.waitUntilInputEnabled();
    await this.messageInput.fill(message);
    await this.sendButton.click();
  }

  async waitForResponse(timeoutMs = 10000) {
    await this.page
      .getByTestId("chat-message-assistant")
      .last()
      .waitFor({ timeout: timeoutMs });
  }

  async waitForAssistantContent(index = 0, timeoutMs = 45000): Promise<string> {
    await expect
      .poll(
        async () => {
          const text =
            (await this.getMessage("assistant", index).textContent()) ?? "";
          return text.trim().length > 0 ? text.trim() : null;
        },
        { timeout: timeoutMs },
      )
      .toBeTruthy();

    return (
      (await this.getMessage("assistant", index).textContent()) ?? ""
    ).trim();
  }

  async waitUntilInputEnabled(timeoutMs = 45000) {
    await expect(this.messageInput).toBeEnabled({ timeout: timeoutMs });
  }

  async submitFeedback(type: "up" | "down", comment?: string) {
    const button =
      type === "up" ? this.feedbackThumbsUp : this.feedbackThumbsDown;
    await button.last().click();

    if (typeof comment === "string") {
      await this.feedbackCommentInput.fill(comment);
    }

    await this.page.getByTestId("feedback-submit-button").click();
  }

  getMessage(role: "user" | "assistant", index = 0) {
    if (role === "user") {
      return this.page.getByTestId("chat-message-user").nth(index);
    }
    return this.page.getByTestId("chat-message-assistant").nth(index);
  }
}
