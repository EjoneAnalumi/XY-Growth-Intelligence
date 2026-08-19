import { expect, test, type Page } from "@playwright/test";

const viewports = [
  { name: "mobile", width: 375, height: 812 },
  { name: "tablet", width: 768, height: 1024 },
  { name: "desktop", width: 1440, height: 900 },
] as const;

const company = {
  id: "company-1",
  name: "Northstar Robotics",
  domain: "northstar.example",
  industry: "Technology",
  headquarters_country: "Albania",
  status: "prospect",
};

const opportunity = {
  id: "opportunity-1",
  company_id: company.id,
  contact_id: null,
  stage_id: "stage-qualified",
  name: "Synthetic security assessment",
  service: "External exposure review",
  value_usd: 24000,
  probability: 60,
  weighted_value_usd: 14400,
  expected_close_date: "2026-09-20",
  owner_id: null,
  need: "Improve security posture",
  blockers: null,
  competitor: null,
  next_action: "Schedule discovery workshop",
  next_action_due_at: "2026-08-20T09:00:00Z",
  lost_reason: null,
  current_stage_entered_at: "2026-08-19T00:00:00Z",
  days_in_current_stage: 1,
  archived_at: null,
  created_at: "2026-08-19T00:00:00Z",
  updated_at: "2026-08-19T00:00:00Z",
};

async function mockApi(page: Page) {
  await page.addInitScript(() => {
    window.localStorage.setItem(
      "xy-growth-intelligence:mock-session",
      JSON.stringify({
        email: "admin.demo@example.test",
        role: "admin",
        token: "dev-admin",
      }),
    );
  });

  await page.route("http://localhost:8000/**", async (route) => {
    const pathname = new URL(route.request().url()).pathname;
    const responses: Record<string, unknown> = {
      "/companies": { items: [company], total: 1 },
      "/contacts": {
        items: [
          {
            id: "contact-1",
            company_id: company.id,
            first_name: "Alex",
            last_name: "Example",
            email: "alex@example.test",
            title: "Security Director",
            role: "champion",
          },
        ],
        total: 1,
      },
      "/pipeline-stages": {
        items: [
          {
            id: "stage-identified",
            name: "Identified",
            sort_order: 1,
            default_probability: 10,
            is_won: false,
            is_lost: false,
          },
          {
            id: "stage-qualified",
            name: "Qualified",
            sort_order: 2,
            default_probability: 60,
            is_won: false,
            is_lost: false,
          },
        ],
        total: 2,
      },
      "/opportunities": { items: [opportunity], total: 1 },
      "/dashboard/summary": {
        total_opportunities: 1,
        open_opportunities: 1,
        won_opportunities: 0,
        lost_opportunities: 0,
        pipeline_value_usd: 24000,
        weighted_pipeline_value_usd: 14400,
        high_priority_opportunities: 1,
        inactive_opportunities: 0,
        open_tasks: 1,
        overdue_tasks: 0,
        due_this_week_tasks: 1,
        activities_count: 1,
        average_days_in_current_stage: 1,
        stage_summaries: [
          {
            stage_id: "stage-qualified",
            stage_name: "Qualified",
            opportunity_count: 1,
            total_value_usd: 24000,
            weighted_value_usd: 14400,
          },
        ],
        priority_opportunities: [
          {
            opportunity_id: opportunity.id,
            name: opportunity.name,
            stage_id: "stage-qualified",
            stage_name: "Qualified",
            company_id: company.id,
            priority_score: 90,
            weighted_value_usd: 14400,
            days_in_current_stage: 1,
            reason: "Synthetic priority for viewport testing.",
          },
        ],
      },
    };

    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify(responses[pathname] ?? {}),
    });
  });
}

async function expectPageFitsViewport(page: Page) {
  await expect(page.locator("main")).toBeVisible();
  const hasHorizontalPageOverflow = await page.evaluate(
    () => document.documentElement.scrollWidth > window.innerWidth + 1,
  );
  expect(hasHorizontalPageOverflow).toBe(false);
}

for (const viewport of viewports) {
  test.describe(`${viewport.name} ${viewport.width}x${viewport.height}`, () => {
    test.use({ viewport: { width: viewport.width, height: viewport.height } });

    test.beforeEach(async ({ page }) => {
      await mockApi(page);
    });

    test("keeps navigation and primary dashboard content usable", async ({ page }, testInfo) => {
      await page.goto("/dashboard");

      await expect(page.getByRole("heading", { name: "Growth Intelligence dashboard" })).toBeVisible();
      await expect(page.getByRole("button", { name: "Refresh" })).toBeVisible();
      await expectPageFitsViewport(page);

      if (viewport.width < 1024) {
        const menu = page.getByRole("button", { name: "Toggle navigation" });
        await expect(menu).toBeVisible();
        await menu.click();
        await expect(menu).toHaveAttribute("aria-expanded", "true");
        await expect(page.locator("#main-navigation")).toBeVisible();
        await expect(page.getByRole("link", { name: "Dashboard", exact: true })).toHaveAttribute(
          "aria-current",
          "page",
        );
        await page.getByRole("link", { name: "Companies", exact: true }).click();
        await expect(menu).toHaveAttribute("aria-expanded", "false");
      } else {
        await expect(page.getByRole("link", { name: "Dashboard", exact: true })).toHaveAttribute(
          "aria-current",
          "page",
        );
      }

      await page.screenshot({ path: testInfo.outputPath(`dashboard-${viewport.name}.png`), fullPage: true });
    });

    test("keeps CRM forms, cards, and actions accessible", async ({ page }, testInfo) => {
      await page.goto("/companies");
      await expect(page.getByRole("heading", { name: "Companies" })).toBeVisible();
      await page.getByRole("button", { name: "Add Company" }).click();
      await expect(page.getByRole("heading", { name: "Add company" })).toBeVisible();
      await expect(page.getByLabel("Company name")).toBeEditable();
      await expect(page.getByRole("button", { name: "Save company" })).toBeVisible();
      await expect(page.getByRole("heading", { name: "Northstar Robotics" })).toBeVisible();
      await expectPageFitsViewport(page);

      await page.goto("/contacts");
      await page.getByRole("button", { name: "Add Contact" }).click();
      await expect(page.getByLabel("Company")).toBeVisible();
      await expect(page.getByLabel("First name")).toBeEditable();
      await expect(page.getByRole("button", { name: "Save contact" })).toBeVisible();
      await expectPageFitsViewport(page);

      await page.screenshot({ path: testInfo.outputPath(`crm-${viewport.name}.png`), fullPage: true });
    });

    test("contains intentional table and Kanban overflow", async ({ page }, testInfo) => {
      await page.goto("/opportunities");
      await expect(page.getByRole("heading", { name: "Opportunities" })).toBeVisible();
      await expect(page.getByRole("button", { name: "New Opportunity" })).toBeEnabled();

      await page.getByRole("button", { name: "Table" }).click();
      const table = page.getByRole("table", { name: "Opportunities pipeline table" });
      await expect(table).toBeVisible();
      await expect(page.getByRole("link", { name: "Details" })).toBeVisible();

      const tableScroller = table.locator("xpath=..");
      if (viewport.width < 920) {
        expect(await tableScroller.evaluate((element) => element.scrollWidth > element.clientWidth)).toBe(true);
      }
      await expectPageFitsViewport(page);

      await page.getByRole("button", { name: "Kanban" }).click();
      await expect(page.getByRole("heading", { name: "Qualified" })).toBeVisible();
      await expect(
        page.getByRole("combobox", { name: "Move Synthetic security assessment to another stage" }),
      ).toBeVisible();
      await expect(
        page.getByRole("textbox", { name: "Movement note for Synthetic security assessment" }),
      ).toBeEditable();

      const kanbanScroller = page.locator("div.overflow-x-auto").last();
      if (viewport.width < 1120) {
        expect(await kanbanScroller.evaluate((element) => element.scrollWidth > element.clientWidth)).toBe(true);
      }
      await expectPageFitsViewport(page);

      await page.screenshot({ path: testInfo.outputPath(`pipeline-${viewport.name}.png`), fullPage: true });
    });
  });
}
