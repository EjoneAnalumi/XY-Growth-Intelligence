import { expect, test, type Page } from "@playwright/test";
import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";

// Opt-in local acceptance: real Supabase sessions, no routed or mocked responses.
const password = process.env.DEMO_PASSWORD;
const evidence = process.env.DAY20_EVIDENCE_DIR || "../tmp/day20-evidence";
const api = "http://localhost:8000";
test.skip(!password, "Supply the local synthetic demo password in DEMO_PASSWORD.");

async function login(page: Page, email: string) {
  await page.goto("/login");
  await page.getByLabel("Email", { exact: true }).fill(email);
  await page.getByLabel("Password", { exact: true }).fill(password!);
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
}
async function shot(page: Page, name: string) {
  await page.waitForLoadState("networkidle");
  await page.screenshot({ path: path.join(evidence, name + ".png"), fullPage: true });
}
async function saved(page: Page, endpoint: string, action: () => Promise<unknown>) {
  const pending = page.waitForResponse(r => r.url().endsWith(endpoint) && ["POST", "PATCH"].includes(r.request().method()));
  await action();
  const response = await pending;
  expect(response.ok(), `POST ${endpoint}: ${response.status()}`).toBeTruthy();
  return response.json();
}

test("real login, CRM, pipeline, follow-up, snapshot, approval and PDF", async ({ page }) => {
  await mkdir(evidence, { recursive: true });
  const suffix = Date.now().toString();
  const companyName = `Handover Synthetic ${suffix}`;
  const opportunityName = `Synthetic assessment ${suffix}`;
  await page.goto("/login");
  await shot(page, "01-login");
  await login(page, "bd.demo@example.test");
  // Obtain the signed-in token solely for independent read-only API comparisons.
  const token = await page.evaluate(() => JSON.parse(localStorage.getItem("xy-growth-intelligence:supabase-session")!).accessToken);
  const headers = { Authorization: `Bearer ${token}` };
  const before = await (await page.request.get(`${api}/dashboard/summary`, { headers })).json();
  await page.goto("/companies");
  await page.getByRole("button", { name: "Add Company", exact: true }).click();
  await page.getByLabel("Company name", { exact: true }).fill(companyName);
  await page.getByLabel("Domain", { exact: true }).fill(`handover-${suffix}.example`);
  await page.getByLabel("Industry", { exact: true }).fill("Technology");
  await page.getByLabel("Country", { exact: true }).fill("Germany");
  const company = await saved(page, "/companies", () => page.getByRole("button", { name: "Save company", exact: true }).click());
  await page.getByLabel("Company for ICP scoring").selectOption(company.id);
  await saved(page, `/companies/${company.id}/calculate-icp`, () => page.getByRole("button", { name: "Calculate", exact: true }).click());
  await shot(page, "02-company-icp");
  await page.goto("/contacts");
  await page.getByRole("button", { name: "Add Contact", exact: true }).click();
  await page.getByLabel("Company", { exact: true }).selectOption(company.id);
  await page.getByLabel("First name", { exact: true }).fill("Synthetic");
  await page.getByLabel("Last name", { exact: true }).fill("Reviewer");
  await page.getByLabel("Email", { exact: true }).fill(`reviewer-${suffix}@example.test`);
  await page.getByLabel("Role", { exact: true }).fill("champion");
  await saved(page, "/contacts", () => page.getByRole("button", { name: "Save contact", exact: true }).click());
  await page.goto("/opportunities");
  await page.getByRole("button", { name: "New Opportunity", exact: true }).click();
  await page.getByLabel("Company", { exact: true }).selectOption(company.id);
  await page.getByLabel("Opportunity name", { exact: true }).fill(opportunityName);
  await page.getByLabel("Value USD", { exact: true }).fill("10000");
  await page.getByLabel("Probability", { exact: true }).fill("50");
  const opportunity = await saved(page, "/opportunities", () => page.getByRole("button", { name: "Create opportunity", exact: true }).click());
  const move = page.getByRole("combobox", { name: `Move ${opportunityName} to another stage` });
  await move.selectOption({ label: "Qualified" });
  const card = page.locator("article").filter({ hasText: opportunityName });
  await saved(page, `/opportunities/${opportunity.id}/move-stage`, () => card.getByRole("button", { name: "Move", exact: true }).click());
  await page.goto(`/opportunities/${opportunity.id}`);
  await page.getByLabel("Subject", { exact: true }).fill("Synthetic discovery meeting");
  await saved(page, "/activities", () => page.getByRole("button", { name: "Record activity", exact: true }).click());
  await page.getByLabel("Title", { exact: true }).fill("Synthetic follow-up");
  const yesterday = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString().slice(0, 10);
  await page.getByLabel("Due", { exact: true }).fill(`${yesterday}T09:00`);
  await saved(page, "/tasks", () => page.getByRole("button", { name: "Schedule task", exact: true }).click());
  await shot(page, "03-opportunity-history-follow-up");
  await page.goto("/dashboard");
  await expect(page.getByRole("heading", { name: "Growth Intelligence dashboard" })).toBeVisible();
  const after = await (await page.request.get(`${api}/dashboard/summary`, { headers })).json();
  expect(after.pipeline_value_usd - before.pipeline_value_usd).toBe(10000);
  expect(after.activities_count - before.activities_count).toBe(1);
  expect(after.overdue_tasks - before.overdue_tasks).toBe(1);
  await writeFile(path.join(evidence, "dashboard-comparison.json"), JSON.stringify({ before, after }, null, 2));
  await shot(page, "04-dashboard");
  await page.getByRole("button", { name: /sign out/i }).click();
  await expect(page).toHaveURL(/\/login$/);
  await login(page, "management.demo@example.test");
  await page.goto("/security-scans");
  await page.getByLabel("Synthetic company ID").fill(company.id);
  await page.getByLabel("Domain or URL").fill(`handover-${suffix}.example`);
  const scan = await saved(page, "/security-scans/snapshot", () => page.getByRole("button", { name: "Run snapshot scan", exact: true }).click());
  await shot(page, "05-snapshot");
  await page.goto(`/reports?security_scan_id=${scan.id}`);
  const report = await saved(page, "/reports/generate", () => page.getByRole("button", { name: "Generate from snapshot", exact: true }).click());
  const reportCard = page.locator("article").filter({ hasText: companyName });
  await saved(page, `/reports/${report.id}/review`, () => reportCard.getByRole("button", { name: "Review", exact: true }).click());
  await saved(page, `/reports/${report.id}/approve`, () => reportCard.getByRole("button", { name: "Approve", exact: true }).click());
  const downloading = page.waitForEvent("download");
  await reportCard.getByRole("button", { name: "Download", exact: true }).click();
  const download = await downloading;
  await download.saveAs(path.join(evidence, "approved-synthetic-report.pdf"));
  await download.delete();
  await reportCard.getByRole("button", { name: "Preview", exact: true }).click();
  await shot(page, "06-approved-report");
  await page.getByRole("button", { name: /sign out/i }).click();
  await login(page, "readonly.demo@example.test");
  const readonlyToken = await page.evaluate(() => JSON.parse(localStorage.getItem("xy-growth-intelligence:supabase-session")!).accessToken);
  const denied = await page.request.post(`${api}/companies`, { headers: { Authorization: `Bearer ${readonlyToken}` }, data: { name: "Denied Synthetic" } });
  expect(denied.status()).toBe(403);
  await page.goto("/reports");
  await expect(page.getByRole("button", { name: "Download", exact: true }).first()).toBeDisabled();
  await shot(page, "07-read-only-permissions");
});


test("company CSV import and export use the authenticated UI", async ({ page }) => {
  await mkdir(evidence, { recursive: true });
  await login(page, "bd.demo@example.test");
  await page.goto("/companies");
  const suffix = Date.now();
  await page.locator("#company-csv-file").setInputFiles({
    name: "synthetic-handover.csv", mimeType: "text/csv",
    buffer: Buffer.from(`name,domain\nCSV Handover ${suffix},csv-${suffix}.example\n`),
  });
  const imported = await saved(page, "/companies/import", () => page.getByRole("button", { name: "Import CSV", exact: true }).click());
  expect(imported.created).toBe(1);
  const pending = page.waitForEvent("download");
  await page.getByRole("button", { name: "Export CSV", exact: true }).click();
  const download = await pending;
  await download.saveAs(path.join(evidence, "synthetic-companies.csv"));
  await download.delete();
  await shot(page, "08-csv");
});
