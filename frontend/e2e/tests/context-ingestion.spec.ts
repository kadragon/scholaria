import { test, expect } from "@playwright/test";
import { ContextsPage } from "../pages/contexts.page";
import { getApiUrl } from "../helpers/api";
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

    // Wait for form submission to complete
    await expect(
      page.getByRole("button", { name: /생성|create/i }),
    ).not.toBeDisabled({ timeout: 10000 });
    await page.waitForLoadState("networkidle");

    const token = await page.evaluate(() => localStorage.getItem("token"));

    let createdContext: {
      id: string;
      name: string;
      context_type: string;
    } | null = null;
    await expect
      .poll(
        async () => {
          const response = await request.get(getApiUrl("/api/contexts"), {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          });
          if (!response.ok()) return null;
          const json = await response.json();
          const contexts = json.data || json;
          if (!Array.isArray(contexts)) return null;
          createdContext = contexts.find(
            (c: { name: string }) => c.name === testContextName,
          );
          return createdContext || null;
        },
        {
          message: `Expected context "${testContextName}" to be created`,
          intervals: [1000, 2000, 3000],
          timeout: 10000,
        },
      )
      .toBeDefined();

    expect(createdContext).toBeDefined();
    expect(createdContext.context_type).toBe("MARKDOWN");
  });

  test("should upload and process PDF context", async ({ page, request }) => {
    test.setTimeout(120000);
    await contextsPage.gotoCreate();

    const pdfContextName = `PDF Context ${Date.now()}`;
    await contextsPage.createPdfContext({
      name: pdfContextName,
      description: "E2E test PDF context",
      filePath: pdfFilePath,
    });

    // Wait for form submission to complete
    await expect(
      page.getByRole("button", { name: /생성|create/i }),
    ).not.toBeDisabled({ timeout: 10000 });
    await page.waitForLoadState("networkidle");

    const token = await page.evaluate(() => localStorage.getItem("token"));

    let createdContext: {
      id: string;
      name: string;
      context_type: string;
    } | null = null;
    await expect
      .poll(
        async () => {
          try {
            const response = await request.get(getApiUrl("/api/contexts"), {
              headers: {
                Authorization: `Bearer ${token}`,
              },
              timeout: 10000,
            });
            if (!response.ok()) return null;
            const json = await response.json();
            const contexts = json.data || json;
            if (!Array.isArray(contexts)) return null;
            createdContext = contexts.find(
              (c: { name: string }) => c.name === pdfContextName,
            );
            return createdContext;
          } catch (error) {
            console.log("Polling error:", error);
            return null;
          }
        },
        {
          message: `Expected PDF context "${pdfContextName}" to be created`,
          intervals: [2000, 3000, 4000],
          timeout: 30000,
        },
      )
      .toBeDefined();

    expect(createdContext).toBeDefined();
    expect(createdContext.context_type).toBe("PDF");
  });

  test("should assign context to topics", async ({ page, request }) => {
    const token = await page.evaluate(() => localStorage.getItem("token"));
    const contextName = `E2E Context Assignment ${Date.now()}`;

    await contextsPage.gotoCreate();
    await contextsPage.createMarkdownContext({
      name: contextName,
      description: "Test context for topic assignment",
      content: "# Assignment Test\n\nThis context will be assigned to topics.",
    });

    // Wait for form submission to complete
    await expect(
      page.getByRole("button", { name: /생성|create/i }),
    ).not.toBeDisabled({ timeout: 10000 });
    await page.waitForLoadState("networkidle");

    const contextsResponse = await request.get(getApiUrl("/api/contexts"), {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const contextsData = await contextsResponse.json();
    let contexts = contextsData.data || contextsData;
    if (!Array.isArray(contexts)) {
      contexts = [];
    }
    const context = contexts.find(
      (c: { name: string }) => c.name === contextName,
    );

    if (!context) {
      throw new Error(`Context "${contextName}" not found`);
    }

    await page.goto(`/admin/contexts/${context.id}/edit`);
    await page.waitForLoadState("networkidle");

    const topicsResponse = await request.get(
      "http://localhost:8001/api/admin/topics",
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    );

    const topicsData = await topicsResponse.json();
    const topics = topicsData.data || topicsData.items || topicsData;
    const topicsArray = Array.isArray(topics) ? topics : [];
    const testTopic = topicsArray.find((t: { name: string }) =>
      t.name.includes("E2E Test Topic"),
    );

    if (!testTopic) {
      test.skip();
      return;
    }

    await contextsPage.assignTopics([testTopic.name]);
    await contextsPage.submitButton.click();

    await expect(page.getByText(/successfully|성공/i)).toBeVisible({
      timeout: 5000,
    });

    const updatedContextResponse = await request.get(
      getApiUrl(`/api/contexts/${context.id}`),
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    );

    const updatedContext = await updatedContextResponse.json();
    expect(updatedContext.topics).toContainEqual(
      expect.objectContaining({ name: testTopic.name }),
    );
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
