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

  test("should create a markdown context", async ({ page, request }) => {
    await contextsPage.gotoCreate();

    await contextsPage.createMarkdownContext({
      name: testContextName,
      description: "E2E test markdown context",
      content:
        "# Test Context\n\nThis is a test markdown context for E2E testing.",
    });

    await page.waitForURL("/admin/contexts", { timeout: 10000 });
    await page.waitForLoadState("networkidle");

    await page.waitForTimeout(1000);

    const token = await page.evaluate(() => localStorage.getItem("token"));
    const response = await request.get(
      "http://localhost:8001/api/admin/contexts",
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    );
    expect(response.ok()).toBeTruthy();
    const json = await response.json();
    const contexts = json.data || json;
    const createdContext = contexts.find(
      (c: { name: string }) => c.name === testContextName,
    );
    expect(createdContext).toBeDefined();
    expect(createdContext.context_type).toBe("MARKDOWN");
  });

  test("should upload and process PDF context", async ({ page, request }) => {
    test.setTimeout(90000);
    await contextsPage.gotoCreate();

    const pdfContextName = `PDF Context ${Date.now()}`;
    await contextsPage.createPdfContext({
      name: pdfContextName,
      description: "E2E test PDF context",
      filePath: pdfFilePath,
    });

    await page.waitForURL("/admin/contexts", { timeout: 10000 });

    const token = await page.evaluate(() => localStorage.getItem("token"));

    let createdContext;
    for (let i = 0; i < 12; i++) {
      const response = await request.get(
        "http://localhost:8001/api/admin/contexts",
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      );
      const json = await response.json();
      const contexts = json.data || json;
      createdContext = contexts.find(
        (c: { name: string }) => c.name === pdfContextName,
      );
      if (createdContext && createdContext.processing_status === "COMPLETED") {
        break;
      }
      await page.waitForTimeout(5000);
    }

    expect(createdContext).toBeDefined();
    expect(createdContext.context_type).toBe("PDF");
    expect(createdContext.processing_status).toBe("COMPLETED");
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
