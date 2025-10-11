import { type Page, type Locator } from "@playwright/test";

export class ContextsPage {
  readonly page: Page;
  readonly createButton: Locator;
  readonly nameInput: Locator;
  readonly descriptionInput: Locator;
  readonly pdfTab: Locator;
  readonly markdownTab: Locator;
  readonly faqTab: Locator;
  readonly fileInput: Locator;
  readonly markdownTextarea: Locator;
  readonly submitButton: Locator;
  readonly table: Locator;
  readonly topicMultiSelect: Locator;

  constructor(page: Page) {
    this.page = page;
    this.createButton = page.getByRole("link", { name: /create/i });
    this.nameInput = page.getByLabel(/name/i);
    this.descriptionInput = page.getByLabel(/description/i);
    this.pdfTab = page.getByRole("tab", { name: /pdf/i });
    this.markdownTab = page.getByRole("tab", { name: /markdown/i });
    this.faqTab = page.getByRole("tab", { name: /faq/i });
    this.fileInput = page.getByLabel(/upload|file/i);
    this.markdownTextarea = page.getByLabel(/content|text/i);
    this.submitButton = page.getByRole("button", { name: /save|create/i });
    this.table = page.getByRole("table");
    this.topicMultiSelect = page.getByRole("combobox", { name: /topic/i });
  }

  async goto() {
    await this.page.goto("/admin/contexts");
  }

  async gotoCreate() {
    await this.page.goto("/admin/contexts/create");
  }

  async createPdfContext(data: {
    name: string;
    description?: string;
    filePath: string;
  }) {
    await this.nameInput.fill(data.name);
    if (data.description) {
      await this.descriptionInput.fill(data.description);
    }
    await this.pdfTab.click();
    await this.fileInput.setInputFiles(data.filePath);
    await this.submitButton.click();
  }

  async createMarkdownContext(data: {
    name: string;
    description?: string;
    content: string;
  }) {
    await this.nameInput.fill(data.name);
    if (data.description) {
      await this.descriptionInput.fill(data.description);
    }
    await this.markdownTab.click();
    await this.markdownTextarea.fill(data.content);
    await this.submitButton.click();
  }

  async editContext(contextName: string) {
    const row = this.table.locator("tr", { hasText: contextName });
    await row.getByRole("button", { name: /edit/i }).click();
  }

  async assignTopics(topics: string[]) {
    for (const topic of topics) {
      await this.topicMultiSelect.click();
      await this.page.getByRole("option", { name: topic }).click();
    }
  }

  getContextRow(contextName: string) {
    return this.table.locator("tr", { hasText: contextName });
  }

  async waitForProcessing(contextName: string, timeoutMs = 30000) {
    const row = this.getContextRow(contextName);
    await row.getByText(/completed/i).waitFor({ timeout: timeoutMs });
  }
}
