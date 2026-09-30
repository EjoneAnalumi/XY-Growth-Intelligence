import { expect, test, type Page } from "@playwright/test";
const password = process.env.DEMO_PASSWORD;
const api = "http://localhost:8000";
test.skip(!password, "Local synthetic demo credentials required");
test.use({ timezoneId: "Europe/Berlin" });
async function login(page: Page, role: string) {
  await page.goto("/login");
  await page.getByLabel("Email", { exact: true }).fill(`${role}.demo@example.test`);
  await page.getByLabel("Password", { exact: true }).fill(password!);
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
  return { Authorization: `Bearer ${await page.evaluate(() => JSON.parse(localStorage.getItem("xy-growth-intelligence:supabase-session")!).accessToken)}` };
}
test("analyst sees local scan time and creates a newest-first draft from Reports", async ({ page }) => {
  await login(page, "analyst");
  let reportId = "";
  try {
    await page.goto("/security-scans");
    await page.getByRole("button", { name: "Run snapshot scan", exact: true }).click();
    await expect(page.getByText("Snapshot saved. A scan is evidence; use the button below to create its draft report.")).toBeVisible();
    const time = page.locator("time").first();
    const raw = await time.getAttribute("datetime");
    const local = await page.evaluate((value) => new Date(value!).toLocaleString(), raw);
    await expect(time).toHaveText(local);
    expect(local).not.toEqual(raw);
    await page.goto("/reports");
    await page.getByRole("link", { name: "Create report from a snapshot" }).click();
    await page.getByRole("button", { name: "Run snapshot and create report" }).click();
    await expect(page).toHaveURL(/\/reports\?report_id=/);
    reportId = new URL(page.url()).searchParams.get("report_id")!;
    await expect(page.getByRole("heading", { name: /Report preview: / })).toBeVisible();
    await expect(page.getByRole("article").first()).toHaveAttribute("data-report-id", reportId);
    await expect(page.getByRole("article").first().getByRole("button", { name: "Submit for review" })).toBeVisible();
    await page.goto("/reports");
    await expect(page.getByRole("article").first()).toHaveAttribute("data-report-id", reportId);
  } finally {
    if (reportId) {
      await page.getByRole("button", { name: "Sign out", exact: true }).first().click();
      const admin = await login(page, "admin");
      expect((await page.request.post(`${api}/reports/${reportId}/archive`, { headers: admin, data: {} })).ok()).toBeTruthy();
    }
  }
});
