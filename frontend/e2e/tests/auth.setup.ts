import { test as setup, expect } from "@playwright/test";
import path from "path";

const authFile = path.join(__dirname, "../../playwright/.auth/admin.json");

setup("authenticate as admin", async ({ page, request }) => {
  const baseURL = "http://localhost:8001";

  const checkResponse = await request.get(`${baseURL}/api/setup/check`);
  const { setup_needed } = await checkResponse.json();

  if (setup_needed) {
    await page.goto("/admin/setup");

    await page.getByLabel(/username/i).fill("admin");
    await page.getByLabel(/email/i).fill("admin@scholaria.test");
    await page.getByLabel(/^password$/i).fill("admin123!@#");
    await page.getByLabel(/confirm password/i).fill("admin123!@#");

    await page.getByRole("button", { name: /create account|submit/i }).click();

    await page.waitForURL("/admin/login");
  }

  await page.goto("/admin/login");

  await page.getByLabel(/email/i).fill("admin@scholaria.test");
  await page.getByLabel(/password/i).fill("admin123!@#");
  await page.getByRole("button", { name: /sign in|login/i }).click();

  await page.waitForURL("/admin/topics");

  await expect(page.getByRole("navigation")).toBeVisible();

  await page.context().storageState({ path: authFile });
});
