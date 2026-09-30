import type { Page } from "@playwright/test";
import { expect, test } from "./fixture-cleanup";
import { mkdir } from "node:fs/promises";
import path from "node:path";

const password = process.env.DEMO_PASSWORD;
const evidence = process.env.COMPLETION_EVIDENCE_DIR || "../tmp/completion-evidence";
test.skip(!password, "Local synthetic demo password required.");

async function login(page: Page, role: string) {
  await page.goto("/login");
  await page.getByLabel("Email", { exact: true }).fill(`${role}.demo@example.test`);
  await page.getByLabel("Password", { exact: true }).fill(password!);
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
  const token = await page.evaluate(() => JSON.parse(localStorage.getItem("xy-growth-intelligence:supabase-session")!).accessToken);
  return { Authorization: `Bearer ${token}` };
}
async function screenshot(page: Page, name: string) {
  await mkdir(evidence, { recursive: true });
  await page.screenshot({ path: path.join(evidence, name), fullPage: true });
}

test("profile intelligence, standalone tasks, management panels and CSV", async ({ page }) => {
  const headers = await login(page, "bd");
  const suffix = Date.now();
  const result = await page.request.post("http://localhost:8000/companies", {
    headers, data: { name: `Synthetic Completion ${suffix}`, domain: `completion-${suffix}.example` },
  });
  expect(result.status()).toBe(201);
  const company = await result.json();
  await page.goto(`/companies/${company.id}`);
  await page.getByLabel("employee count", { exact: true }).fill("650");
  await page.getByLabel("cloud usage (comma separated)").fill("Synthetic cloud");
  await page.getByLabel("regulatory context (comma separated)").fill("SOC 2");
  await page.getByLabel("strategic importance").fill("4");
  await page.getByRole("button", { name: "Save profile" }).click();
  await expect(page.getByRole("status")).toContainText("Profile saved");
  await page.reload();
  await expect(page.getByLabel("employee count", { exact: true })).toHaveValue("650");
  await screenshot(page, "01-company-profile.png");
  const scoring = await page.request.post(`http://localhost:8000/companies/${company.id}/calculate-icp`, { headers });
  expect(scoring.status()).toBe(201);
  const recommendation = await page.request.get(`http://localhost:8000/companies/${company.id}/recommendations`, { headers });
  expect((await recommendation.json()).primary).toBe("Cloud Security Assessment");
  await page.goto("/tasks");
  const title = `Synthetic standalone ${suffix}`;
  await page.getByLabel("Title", { exact: true }).fill(title);
  await page.getByLabel("Due date", { exact: true }).fill("2026-01-01T09:00");
  await page.getByRole("button", { name: "Create task" }).click();
  await expect(page.getByText("Task created.", { exact: true })).toBeVisible();
  await page.getByLabel("Search tasks").fill(title);
  await page.getByLabel("Due/status filter").selectOption("overdue");
  await page.getByLabel("Outcome", { exact: true }).fill("Mock follow-up completed");
  await page.getByRole("button", { name: "Complete", exact: true }).click();
  await page.getByLabel("Due/status filter").selectOption("completed");
  await expect(page.getByText(/Completed .*Mock follow-up completed/)).toBeVisible();
  await screenshot(page, "02-tasks.png");
  await page.goto("/data");
  await page.getByLabel("Record type").selectOption("tasks");
  await page.getByLabel("Synthetic CSV file").setInputFiles({ name: "synthetic-tasks.csv", mimeType: "text/csv", buffer: Buffer.from(`title,priority,status\nSynthetic CSV ${suffix},high,open\n`) });
  await page.getByRole("button", { name: "Import CSV" }).click();
  await expect(page.getByRole("status")).toContainText("1 records imported");
  const download = page.waitForEvent("download");
  await page.getByRole("button", { name: "Export CSV" }).click();
  expect((await download).suggestedFilename()).toBe("tasks.csv");
  await page.goto("/dashboard");
  await expect(page.getByRole("heading", { name: "Monthly closing forecast" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Stage conversion and duration" })).toBeVisible();
  await expect(page.getByText("Management analytics unavailable")).toHaveCount(0);
  await screenshot(page, "03-management-analytics.png");
});

test("admin configuration saves and all five roles have enforced permissions", async ({ page }) => {
  const admin = await login(page, "admin");
  await page.goto("/administration");
  await expect(page.getByRole("heading", { name: "ICP weights" })).toBeVisible();
  await page.getByRole("button", { name: "Save weights" }).click();
  await expect(page.getByRole("status")).toContainText("Configuration saved");
  await screenshot(page, "04-administration.png");
  const config = await (await page.request.get("http://localhost:8000/icp-rules", { headers: admin })).json();
  for (const role of ["management", "bd", "analyst", "readonly"]) {
    await page.getByRole("button", { name: "Sign out", exact: true }).first().click();
    const headers = await login(page, role);
    const denied = await page.request.put("http://localhost:8000/icp-rules", { headers, data: config });
    expect(denied.status()).toBe(403);
    const tasks = await page.request.post("http://localhost:8000/tasks", { headers, data: { title: "Synthetic role verification" } });
    expect(tasks.status()).toBe(["analyst", "readonly"].includes(role) ? 403 : 201);
    await page.goto("/administration");
    await expect(page.getByText("Only administrators can manage this configuration.", { exact: true })).toBeVisible();
  }
  // Expire only the browser's timestamp; refresh must still be accepted by real Supabase Auth.
  await page.evaluate(() => {
    const key = "xy-growth-intelligence:supabase-session";
    const session = JSON.parse(localStorage.getItem(key)!); session.expiresAt = 0;
    localStorage.setItem(key, JSON.stringify(session));
  });
  await page.goto("/tasks");
  await expect(page.getByLabel("Search tasks")).toBeVisible();
  await expect.poll(() => page.evaluate(() => JSON.parse(localStorage.getItem("xy-growth-intelligence:supabase-session")!).expiresAt)).toBeGreaterThan(Date.now());
});

test("local invitation, password recovery and invalid-session sign-out", async ({ page }) => {
  await login(page, "admin");
  const email = `acceptance-${Date.now()}@example.test`;
  await page.goto("/users");
  await page.getByLabel("Full name", { exact: true }).fill("Synthetic Invitation Acceptance");
  await page.getByLabel("Work email", { exact: true }).fill(email);
  await page.getByRole("button", { name: "Send invitation", exact: true }).click();
  await expect(page.getByRole("status")).toContainText("Invitation sent.");
  await screenshot(page, "05-invitation-sent.png");

  async function mailLink(subject: string) {
    let messageId = "";
    await expect.poll(async () => {
      const response = await page.request.get("http://127.0.0.1:54324/api/v1/messages");
      const inbox = await response.json();
      const message = inbox.messages.find((item: { ID: string; Subject: string; To: { Address: string }[] }) => item.To.some((to) => to.Address === email) && item.Subject.toLowerCase().includes(subject));
      messageId = message?.ID ?? "";
      return Boolean(messageId);
    }).toBeTruthy();
    const response = await page.request.get(`http://127.0.0.1:54324/api/v1/message/${messageId}`);
    const message = await response.json();
    const link = (message.HTML as string).match(/href="([^"]*\/auth\/v1\/verify[^\"]*)"/);
    if (!link) throw new Error("Local Auth email has no verification link.");
    return link[1].replaceAll("&amp;", "&");
  }
  const invitation = await mailLink("invited");
  await page.getByRole("button", { name: "Sign out", exact: true }).first().click();
  await page.goto(invitation);
  await page.getByLabel("New password", { exact: true }).fill(password!);
  await page.getByLabel("Confirm password", { exact: true }).fill(password!);
  await page.getByRole("button", { name: "Save password", exact: true }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
  await screenshot(page, "06-invitation-accepted.png");
  await page.getByRole("button", { name: "Sign out", exact: true }).first().click();
  await page.goto("/forgot-password");
  await page.getByLabel("Email", { exact: true }).fill(email);
  await page.getByRole("button", { name: "Send reset link", exact: true }).click();
  await expect(page.getByRole("status")).toContainText("has sent a reset link");
  await screenshot(page, "07-recovery-requested.png");
  await page.goto(await mailLink("reset"));
  const recoveredPassword = `${password!}-Recovered`;
  await page.getByLabel("New password", { exact: true }).fill(recoveredPassword);
  await page.getByLabel("Confirm password", { exact: true }).fill(recoveredPassword);
  await page.getByRole("button", { name: "Save password", exact: true }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
  await screenshot(page, "08-recovery-completed.png");
  await page.evaluate(() => {
    const key = "xy-growth-intelligence:supabase-session";
    const session = JSON.parse(localStorage.getItem(key)!);
    session.expiresAt = 0; session.refreshToken = "invalid-synthetic-refresh-token";
    localStorage.setItem(key, JSON.stringify(session));
  });
  await page.goto("/tasks");
  await expect(page).toHaveURL(/\/login$/);
  await screenshot(page, "09-expired-session.png");
  const adminHeaders = await login(page, "admin");
  const users = await (await page.request.get("http://localhost:8000/users", { headers: adminHeaders })).json();
  const fixture = users.items.find((item: { email: string }) => item.email === email);
  if (fixture) expect((await page.request.delete(`http://localhost:8000/users/${fixture.id}`, { headers: adminHeaders })).ok()).toBeTruthy();
});
