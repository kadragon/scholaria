import { test as setup, expect } from "@playwright/test";
import path from "path";
import { fileURLToPath } from "url";
import { dirname } from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const authFile = path.join(__dirname, "../../playwright/.auth/admin.json");

setup("authenticate as admin", async ({ page, request }) => {
  const baseURL =
    process.env.VITE_API_URL?.replace("/api", "") || "http://localhost:8001";
  const adminUsername = process.env.E2E_ADMIN_USERNAME || "admin";
  const adminEmail = process.env.E2E_ADMIN_EMAIL || "admin@example.com";
  const adminPassword = process.env.E2E_ADMIN_PASSWORD || "admin123!@#";

  // Listen for network requests
  const setupRequests: string[] = [];
  page.on("request", (req) => {
    if (req.url().includes("/setup/")) {
      setupRequests.push(`${req.method()} ${req.url()}`);
    }
  });

  page.on("console", (msg) => {
    console.log(`BROWSER LOG: ${msg.text()}`);
  });

  const checkResponse = await request.get(`${baseURL}/api/setup/check`);
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

  await page.waitForURL(/\/admin/);

  await expect(page.getByRole("navigation")).toBeVisible();

  await page.context().storageState({ path: authFile });
});
