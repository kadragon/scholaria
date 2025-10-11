import { type Page, type Locator } from "@playwright/test";

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
    this.topicSelector = page.getByRole("combobox", {
      name: /토픽|topic|select/i,
    });
    this.messageInput = page.getByPlaceholder(/질문|ask|question|message/i);
    this.sendButton = page.getByRole("button", { name: /전송|send/i });
    this.messageList = page.getByTestId("message-list");
    this.feedbackThumbsUp = page.getByRole("button", {
      name: /thumbs up|like/i,
    });
    this.feedbackThumbsDown = page.getByRole("button", {
      name: /thumbs down|dislike/i,
    });
    this.feedbackCommentInput =
      page.getByPlaceholder(/코멘트|comment|feedback/i);
  }

  async goto() {
    await this.page.goto("/chat");
  }

  async selectTopic(topicName: string) {
    await this.topicSelector.click();
    await this.page.getByRole("option", { name: topicName }).click();
  }

  async sendMessage(message: string) {
    await this.messageInput.fill(message);
    await this.sendButton.click();
  }

  async waitForResponse(timeoutMs = 10000) {
    await this.messageList
      .locator('[data-role="assistant"]')
      .last()
      .waitFor({ timeout: timeoutMs });
  }

  async submitFeedback(type: "up" | "down", comment?: string) {
    const button =
      type === "up" ? this.feedbackThumbsUp : this.feedbackThumbsDown;
    await button.last().click();

    if (comment) {
      await this.feedbackCommentInput.fill(comment);
      await this.page.getByRole("button", { name: /제출|submit/i }).click();
    }
  }

  getMessage(role: "user" | "assistant", index = 0) {
    return this.messageList.locator(`[data-role="${role}"]`).nth(index);
  }
}
