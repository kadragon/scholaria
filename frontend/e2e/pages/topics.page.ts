import { type Page, type Locator } from "@playwright/test";

export class TopicsPage {
  readonly page: Page;
  readonly createButton: Locator;
  readonly nameInput: Locator;
  readonly slugInput: Locator;
  readonly descriptionInput: Locator;
  readonly systemPromptInput: Locator;
  readonly submitButton: Locator;
  readonly table: Locator;

  constructor(page: Page) {
    this.page = page;
    this.createButton = page.getByRole("button", { name: "토픽 생성" });
    this.nameInput = page.locator("#name");
    this.slugInput = page.locator("#slug");
    this.descriptionInput = page.locator("#description");
    this.systemPromptInput = page.locator("#systemPrompt");
    this.submitButton = page.getByRole("button", {
      name: /생성/,
    });
    this.table = page.getByRole("table");
  }

  async goto() {
    await this.page.goto("/admin/topics");
  }

  async gotoCreate() {
    await this.page.goto("/admin/topics/create");
  }

  async createTopic(data: {
    name: string;
    slug?: string;
    description?: string;
    systemPrompt: string;
  }) {
    await this.nameInput.fill(data.name);
    if (data.slug) {
      await this.slugInput.fill(data.slug);
    }
    if (data.description) {
      await this.descriptionInput.fill(data.description);
    }
    await this.systemPromptInput.fill(data.systemPrompt);
    await this.submitButton.click();
  }

  async editTopic(topicName: string) {
    const row = this.table.locator("tr", { hasText: topicName });
    await row.getByRole("button", { name: "편집" }).click();
  }

  async deleteTopic(topicName: string) {
    const row = this.table.locator("tr", { hasText: topicName });
    await row.getByRole("button", { name: "삭제" }).click();
  }

  getTopicRow(topicName: string) {
    return this.table.locator("tr", { hasText: topicName });
  }
}
