import { test as setup, expect, type Page } from "@playwright/test";
import { getApiUrl } from "../helpers/api";
import path from "path";
import { fileURLToPath } from "url";
import { dirname } from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const authFile = path.join(__dirname, "../../playwright/.auth/admin.json");

async function getAccessToken(page: Page): Promise<string> {
  const token = await page.evaluate(() => {
    return localStorage.getItem("token");
  });
  if (!token) {
    throw new Error("No access token found in localStorage");
  }
  return token;
}

setup("authenticate as admin", async ({ page, request }) => {
  const adminUsername = process.env.E2E_ADMIN_USERNAME || "admin";
  const adminEmail = process.env.E2E_ADMIN_EMAIL || "admin@example.com";
  const adminPassword = process.env.E2E_ADMIN_PASSWORD || "admin123!@#";

  const setupRequests: string[] = [];
  page.on("request", (req) => {
    if (req.url().includes("/setup/")) {
      setupRequests.push(`${req.method()} ${req.url()}`);
    }
  });

  page.on("console", (msg) => {
    console.log(`BROWSER LOG: ${msg.text()}`);
  });

  const checkResponse = await request.get(getApiUrl("/api/setup/check"));
  const responseData = await checkResponse.json();
  const { needs_setup } = responseData;

  if (needs_setup) {
    await page.goto("/admin/setup");

    await page.getByRole("textbox", { name: "Username" }).fill(adminUsername);
    await page.getByRole("textbox", { name: "Email" }).fill(adminEmail);

    const passwordFields = page.getByPlaceholder("••••••••");
    await passwordFields.first().fill(adminPassword);
    await passwordFields.nth(1).fill(adminPassword);

    await page
      .getByRole("button", { name: /관리자 계정 생성|create account/i })
      .click();

    await page.waitForURL("/admin/login", { timeout: 10000 });
  } else {
    await page.goto("/admin/login");
  }

  await page.getByRole("textbox", { name: "Email" }).fill(adminEmail);
  await page.getByRole("textbox", { name: "Password" }).fill(adminPassword);
  await page.getByRole("button", { name: /로그인|login/i }).click();

  await page.waitForURL(/\/admin/, { timeout: 15000 });

  await expect(page.getByRole("navigation")).toBeVisible();

  await page.context().storageState({ path: authFile });

  console.log("Creating test data: topic with context...");
  const topicName = `E2E Test Topic ${Date.now()}`;
  const topicSlug = topicName.toLowerCase().replace(/\s+/g, "-");

  const topicResponse = await request.post(getApiUrl("/api/admin/topics"), {
    headers: {
      Authorization: `Bearer ${await getAccessToken(page)}`,
      "Content-Type": "application/json",
    },
    data: {
      name: topicName,
      slug: topicSlug,
      description: "Test topic for E2E testing with context",
      system_prompt:
        "You are a helpful assistant. Answer questions based on the provided context.",
    },
  });

  if (!topicResponse.ok()) {
    console.error("Failed to create topic:", await topicResponse.text());
    throw new Error("Topic creation failed");
  }

  const topic = await topicResponse.json();
  console.log(`Created topic: ${topic.name} (ID: ${topic.id})`);

  const contextName = `E2E Test Context ${Date.now()}`;
  const formData = new FormData();
  formData.append("name", contextName);
  formData.append("description", "Test context for E2E testing");
  formData.append("context_type", "MARKDOWN");
  formData.append(
    "original_content",
    `# Test Documentation\n\n## Overview\nThis is test documentation for E2E testing.\n\n## Features\n- Feature 1: Authentication\n- Feature 2: Topic Management\n- Feature 3: Context Ingestion\n\n## FAQ\nQ: What is this?\nA: This is a test context for E2E testing.`,
  );

  const contextResponse = await request.post(getApiUrl("/api/contexts"), {
    headers: {
      Authorization: `Bearer ${await getAccessToken(page)}`,
    },
    multipart: {
      name: contextName,
      description: "Test context for E2E testing",
      context_type: "MARKDOWN",
      original_content: `# Test Documentation\n\n## Overview\nThis is test documentation for E2E testing.\n\n## Features\n- Feature 1: Authentication\n- Feature 2: Topic Management\n- Feature 3: Context Ingestion\n\n## FAQ\nQ: What is this?\nA: This is a test context for E2E testing.`,
    },
  });

  if (!contextResponse.ok()) {
    console.error("Failed to create context:", await contextResponse.text());
    throw new Error("Context creation failed");
  }

  const context = await contextResponse.json();
  console.log(`Created context: ${context.name} (ID: ${context.id})`);

  const assignResponse = await request.patch(
    getApiUrl(`/api/admin/contexts/${context.id}`),
    {
      headers: {
        Authorization: `Bearer ${await getAccessToken(page)}`,
        "Content-Type": "application/json",
      },
      data: {
        topic_ids: [topic.id],
      },
    },
  );

  if (!assignResponse.ok()) {
    console.error(
      "Failed to assign context to topic:",
      await assignResponse.text(),
    );
    throw new Error("Context assignment failed");
  }

  console.log(`Assigned context to topic successfully`);
  console.log(
    `Test data ready - Topic: "${topicName}", Context: "${contextName}"`,
  );
});
