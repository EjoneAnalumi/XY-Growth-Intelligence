import { expect, test, type Page } from "@playwright/test";
import { mkdir } from "node:fs/promises";

const password = process.env.DEMO_PASSWORD;
const api = "http://localhost:8000";
test.skip(!password, "Local synthetic password required.");
async function login(page: Page, role: string) {
  await page.goto("/login");
  await page.getByLabel("Email", { exact: true }).fill(`${role}.demo@example.test`);
  await page.getByLabel("Password", { exact: true }).fill(password!);
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
  return { Authorization: `Bearer ${await page.evaluate(() => JSON.parse(localStorage.getItem("xy-growth-intelligence:supabase-session")!).accessToken)}` };
}
test("personal assignments, note receipts, EUR CSV and focused report preview", async ({ page }) => {
  await mkdir("../tmp/review-evidence", { recursive: true });
  let admin = await login(page, "admin");
  const suffix = Date.now();
  const taskIds: string[] = [];
  let noteId = "";
  let reportId = "";
  try {
    for (const [name, owner] of [["Analyst", "00000000-0000-4000-8000-000000000004"], ["Unassigned", null], ["Admin", "00000000-0000-4000-8000-000000000001"]]) {
      const response = await page.request.post(`${api}/tasks`, { headers: admin, data: { title: `Review acceptance ${name} ${suffix}`, owner_id: owner, due_at: new Date(Date.now() + 3600000).toISOString() } });
      expect(response.status()).toBe(201); taskIds.push((await response.json()).id);
    }
    const note = await page.request.post(`${api}/notes`, { headers: admin, data: { body: `Review acceptance note ${suffix}` } });
    noteId = (await note.json()).id;
    await page.goto("/tasks");
    await expect(page.getByLabel("Sort tasks")).toHaveValue("newest");
    await expect(page.getByLabel("Owner", { exact: true }).locator('option[value="00000000-0000-4000-8000-000000000005"]')).toHaveCount(0);
    await page.getByRole("button", { name: "Sign out", exact: true }).first().click();
    const analyst = await login(page, "analyst");
    await page.goto("/tasks");
    await expect(page.getByText(`Review acceptance Analyst ${suffix}`, { exact: false })).toBeVisible();
    await expect(page.getByText(`Review acceptance Admin ${suffix}`, { exact: true })).toHaveCount(0);
    const card = page.getByRole("article").filter({ hasText: `Review acceptance Analyst ${suffix}` });
    await expect(card.getByText(/Assigned by Admin Demo/)).toBeVisible();
    await card.getByRole("button", { name: "Mark seen" }).click();
    await expect(card.getByRole("button", { name: "Mark seen" })).toHaveCount(0);
    await page.reload();
    const inbox = await (await page.request.get(`${api}/inbox`, { headers: analyst })).json();
    expect(inbox.unread_task_ids).not.toContain(taskIds[0]);
    await expect(card.getByRole("heading")).toBeVisible();
    await page.screenshot({ path: "../tmp/review-evidence/01-personal-tasks.png", fullPage: true });
    await card.getByLabel("Outcome").fill("Reviewed synthetic scope");
    await card.getByRole("button", { name: "Complete", exact: true }).click();
    await expect(page.getByText("Task completed.", { exact: true })).toBeVisible();
    await page.goto("/notes");
    const noteCard = page.getByRole("article").filter({ hasText: `Review acceptance note ${suffix}` });
    await noteCard.getByRole("button", { name: "Mark read" }).click();
    await expect(noteCard.getByRole("button", { name: "Mark read" })).toHaveCount(0);
    await expect(page.getByLabel("New note")).toBeVisible();
    await page.screenshot({ path: "../tmp/review-evidence/02-personal-notes.png", fullPage: true });
    await page.getByRole("button", { name: "Sign out", exact: true }).first().click();
    admin = await login(page, "admin");
    const csv = await page.request.get(`${api}/data/opportunities/export`, { headers: admin });
    expect(await csv.text()).toContain("value_eur"); expect(await csv.text()).not.toContain("value_usd");
    const scan = await page.request.post(`${api}/security-scans/snapshot`, { headers: admin, data: { company_id: "10000000-0000-4000-8000-000000000001", domain: "northstar-robotics.example", approved: true, approval_note: "Local synthetic review acceptance" } });
    expect(scan.status()).toBe(200);
    const report = await page.request.post(`${api}/reports/generate`, { headers: admin, data: { security_scan_id: (await scan.json()).id } });
    expect(report.status()).toBe(201); reportId = (await report.json()).id;
    await page.goto("/reports");
    const reportCard = page.locator(`[data-report-id="${reportId}"]`);
    await reportCard.getByRole("button", { name: "Submit for review" }).click();
    await reportCard.getByRole("button", { name: "Approve", exact: true }).click();
    await expect(reportCard.getByRole("button", { name: "Download", exact: true })).toBeEnabled();
    await reportCard.getByRole("button", { name: "Preview", exact: true }).click();
    await expect(page.getByRole("heading", { name: /Report preview: Cyber Risk Snapshot/ })).toBeVisible();
    await page.getByRole("button", { name: "Hide reports" }).click();
    await expect(page.getByRole("region", { name: "Report list" })).toHaveCount(0);
    await page.screenshot({ path: "../tmp/review-evidence/03-focused-report.png", fullPage: true });
    await page.getByRole("button", { name: "Show reports" }).click();
    page.once("dialog", (dialog) => dialog.accept());
    await reportCard.getByRole("button", { name: "Archive", exact: true }).click();
    await expect(page.getByText("Report archived. Find it with the Archived status filter.")).toBeVisible();
    await page.getByLabel("Report status").selectOption("archived");
    await expect(reportCard).toBeVisible();
  } finally {
    // Remove only records created by this test; never leave extra tasks/notes in the review app.
    for (const id of taskIds) await page.request.delete(`${api}/tasks/${id}`, { headers: admin });
    if (noteId) await page.request.delete(`${api}/notes/${noteId}`, { headers: admin });
    if (reportId) await page.request.post(`${api}/reports/${reportId}/archive`, { headers: admin, data: {} });
  }
});
