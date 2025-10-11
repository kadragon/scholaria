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
  const adminEmail = process.env.E2E_ADMIN_EMAIL || "admin@scholaria.test";
  const adminPassword = process.env.E2E_ADMIN_PASSWORD || "admin123!@#";

  const checkResponse = await request.get(`${baseURL}/api/setup/check`);
  const { setup_needed } = await checkResponse.json();

  if (setup_needed) {
    await page.goto("/admin/setup");

    await page.getByLabel(/username/i).fill(adminUsername);
    await page.getByLabel(/email/i).fill(adminEmail);
    await page.getByLabel(/^password$/i).fill(adminPassword);
    await page.getByLabel(/confirm password/i).fill(adminPassword);

    await page.getByRole("button", { name: /create account|submit/i }).click();

    await page.waitForURL("/admin/login");
  }

  await page.goto("/admin/login");

  await page.getByLabel(/email/i).fill(adminEmail);
  await page.getByLabel(/password/i).fill(adminPassword);
  await page.getByRole("button", { name: /sign in|login/i }).click();

  await page.waitForURL("/admin/topics");

  await expect(page.getByRole("navigation")).toBeVisible();

  await page.context().storageState({ path: authFile });
});
