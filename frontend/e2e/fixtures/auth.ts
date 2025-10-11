import { test as base, type Page } from "@playwright/test";

type AuthenticatedFixtures = {
  authenticatedPage: Page;
};

export const test = base.extend<AuthenticatedFixtures>({
  authenticatedPage: async ({ browser }, useFn) => {
    const context = await browser.newContext({
      storageState: "playwright/.auth/admin.json",
    });
    const page = await context.newPage();
    await useFn(page);
    await context.close();
  },
});

export { expect } from "@playwright/test";
