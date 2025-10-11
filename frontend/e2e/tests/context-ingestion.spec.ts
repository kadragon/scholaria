import { test, expect } from "@playwright/test";
import { ContextsPage } from "../pages/contexts.page";
import { TopicsPage } from "../pages/topics.page";
import path from "path";

test.describe("Context Ingestion", () => {
  let contextsPage: ContextsPage;
  const testContextName = `E2E Test Context ${Date.now()}`;
  const pdfFilePath = path.join(__dirname, "../fixtures/sample.pdf");

  test.beforeEach(async ({ page }) => {
    contextsPage = new ContextsPage(page);
    await contextsPage.goto();
  });

  test("should display contexts list", async () => {
    await expect(contextsPage.table).toBeVisible();
    await expect(contextsPage.createButton).toBeVisible();
  });

  test("should create a markdown context", async ({ page }) => {
    await contextsPage.gotoCreate();

    await contextsPage.createMarkdownContext({
      name: testContextName,
      description: "E2E test markdown context",
      content:
        "# Test Context\n\nThis is a test markdown context for E2E testing.",
    });

    await page.waitForURL("/admin/contexts", { timeout: 10000 });

    const row = contextsPage.getContextRow(testContextName);
    await expect(row).toBeVisible();
    await expect(row).toContainText(/completed/i);
  });

  test("should upload and process PDF context", async ({ page }) => {
    await contextsPage.gotoCreate();

    const pdfContextName = `PDF Context ${Date.now()}`;
    await contextsPage.createPdfContext({
      name: pdfContextName,
      description: "E2E test PDF context",
      filePath: pdfFilePath,
    });

    await page.waitForURL("/admin/contexts", { timeout: 10000 });

    await contextsPage.waitForProcessing(pdfContextName, 30000);

    const row = contextsPage.getContextRow(pdfContextName);
    await expect(row).toContainText(/completed/i);
  });

  test("should assign context to topics", async ({ page }) => {
    const topicsPage = new TopicsPage(page);

    await topicsPage.goto();
    const firstTopicRow = topicsPage.table.locator("tr").nth(1);
    const topicName = await firstTopicRow.locator("td").nth(1).textContent();

    if (!topicName) {
      test.skip();
    }

    await contextsPage.goto();
    await contextsPage.gotoCreate();

    const contextName = `Context with Topic ${Date.now()}`;
    await contextsPage.nameInput.fill(contextName);
    await contextsPage.descriptionInput.fill("Context assigned to topic");
    await contextsPage.markdownTab.click();
    await contextsPage.markdownTextarea.fill(
      "# Test\n\nContent for topic assignment test.",
    );

    await contextsPage.assignTopics([topicName]);

    await contextsPage.submitButton.click();

    await page.waitForURL("/admin/contexts", { timeout: 10000 });

    const row = contextsPage.getContextRow(contextName);
    await expect(row).toBeVisible();
  });

  test("should validate required fields", async ({ page }) => {
    await contextsPage.gotoCreate();

    await contextsPage.submitButton.click();

    await expect(
      page.getByText(/required|cannot be empty/i).first(),
    ).toBeVisible();
  });

  test("should switch between content type tabs", async ({ page }) => {
    await contextsPage.gotoCreate();

    await expect(contextsPage.pdfTab).toBeVisible();
    await expect(contextsPage.markdownTab).toBeVisible();
    await expect(contextsPage.faqTab).toBeVisible();

    await contextsPage.markdownTab.click();
    await expect(contextsPage.markdownTextarea).toBeVisible();

    await contextsPage.faqTab.click();
    await page.waitForTimeout(500);
  });
});
