import { test, expect } from "@playwright/test";
import { ContextsPage } from "../pages/contexts.page";
import path from "path";
import { fileURLToPath } from "url";
import { dirname } from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

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
    await page.waitForLoadState("networkidle");

    await contextsPage.searchContext(testContextName);
    await expect(contextsPage.searchInput).toHaveValue(testContextName);

    const row = contextsPage.getContextRow(testContextName);
    await expect(row).toBeVisible({ timeout: 15000 });
    await expect(row).toContainText(/완료|completed|pending/i);
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

    await contextsPage.waitForProcessing(pdfContextName, 60000);

    const row = contextsPage.getContextRow(pdfContextName);
    await expect(row).toContainText(/완료|completed/i);
  });

  test.skip("should assign context to topics", async () => {
    // Topic assignment is only available in edit page, not create page
  });

  test("should validate required fields", async () => {
    await contextsPage.gotoCreate();

    await contextsPage.submitButton.click();

    await expect(contextsPage.page).toHaveURL(/\/create/, { timeout: 2000 });
  });

  test("should switch between content type tabs", async () => {
    await contextsPage.gotoCreate();

    await expect(contextsPage.pdfTab).toBeVisible();
    await expect(contextsPage.markdownTab).toBeVisible();
    await expect(contextsPage.faqTab).toBeVisible();

    await contextsPage.markdownTab.click();
    await expect(contextsPage.markdownTextarea).toBeVisible();

    await contextsPage.faqTab.click();
    await expect(contextsPage.faqTab).toHaveAttribute("data-state", "active");
  });
});
