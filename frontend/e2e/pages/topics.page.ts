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
    this.createButton = page.getByRole("button", { name: /생성|create/i });
    this.nameInput = page.getByLabel(/이름|name/i);
    this.slugInput = page.getByLabel(/슬러그|slug/i);
    this.descriptionInput = page.getByLabel(/설명|description/i);
    this.systemPromptInput = page.getByLabel(/시스템 프롬프트|system prompt/i);
    this.submitButton = page.getByRole("button", {
      name: /저장|save|생성|create/i,
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
    await row.getByRole("button", { name: /수정|edit/i }).click();
  }

  async deleteTopic(topicName: string) {
    const row = this.table.locator("tr", { hasText: topicName });
    await row.getByRole("button", { name: /삭제|delete/i }).click();
  }

  getTopicRow(topicName: string) {
    return this.table.locator("tr", { hasText: topicName });
  }
}
