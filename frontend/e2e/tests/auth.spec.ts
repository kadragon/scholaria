import { test, expect } from "@playwright/test";
import { LoginPage } from "../pages/login.page";
import { SetupPage } from "../pages/setup.page";

test.describe("Authentication & Setup", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.context().clearCookies();
    await page.evaluate(() => localStorage.clear());
  });

  test("should redirect to setup when setup is needed", async ({ page }) => {
    const setupPage = new SetupPage(page);

    await page.goto("/admin/login");

    const response = await page.request.get(
      "http://localhost:8001/api/setup/check",
    );
    const { setup_needed } = await response.json();

    if (setup_needed) {
      await page.waitForURL("/admin/setup");
      await expect(setupPage.usernameInput).toBeVisible();
    }
  });

  test("should complete setup flow successfully", async ({ page }) => {
    const setupPage = new SetupPage(page);
    const loginPage = new LoginPage(page);

    const response = await page.request.get(
      "http://localhost:8001/api/setup/check",
    );
    const { setup_needed } = await response.json();

    if (!setup_needed) {
      test.skip();
    }

    await setupPage.goto();

    await setupPage.setup("testadmin", "test@scholaria.test", "Test123!@#");

    await page.waitForURL("/admin/login", { timeout: 10000 });

    await expect(loginPage.emailInput).toBeVisible();
  });

  test("should login successfully with valid credentials", async ({ page }) => {
    const loginPage = new LoginPage(page);

    await loginPage.goto();

    await loginPage.login("admin@scholaria.test", "admin123!@#");

    await page.waitForURL("/admin/topics", { timeout: 10000 });

    await expect(page.getByRole("navigation")).toBeVisible();

    const token = await page.evaluate(() => localStorage.getItem("token"));
    expect(token).toBeTruthy();
  });

  test("should show error with invalid credentials", async ({ page }) => {
    const loginPage = new LoginPage(page);

    await loginPage.goto();

    await loginPage.login("wrong@email.com", "wrongpassword");

    await expect(loginPage.errorMessage).toBeVisible({ timeout: 5000 });
  });

  test("should persist session after reload", async ({ page }) => {
    const loginPage = new LoginPage(page);

    await loginPage.goto();
    await loginPage.login("admin@scholaria.test", "admin123!@#");
    await page.waitForURL("/admin/topics");

    await page.reload();

    await expect(page).toHaveURL("/admin/topics");
    await expect(page.getByRole("navigation")).toBeVisible();
  });

  test("should logout successfully", async ({ page }) => {
    const loginPage = new LoginPage(page);

    await loginPage.goto();
    await loginPage.login("admin@scholaria.test", "admin123!@#");
    await page.waitForURL("/admin/topics");

    await page.getByRole("button", { name: /logout|sign out/i }).click();

    await page.waitForURL("/admin/login", { timeout: 5000 });

    const token = await page.evaluate(() => localStorage.getItem("token"));
    expect(token).toBeNull();
  });
});
