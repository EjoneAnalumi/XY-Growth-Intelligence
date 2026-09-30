import { expect, test, type Page } from "@playwright/test";
const api = "http://localhost:8000";
const password = process.env.DEMO_PASSWORD;
test.skip(!password, "Local synthetic credentials required");
async function login(page: Page, role: string) {
  await page.goto("/login");
  await page.getByLabel("Email", { exact: true }).fill(`${role}.demo@example.test`);
  await page.getByLabel("Password", { exact: true }).fill(password!);
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
  return { Authorization: `Bearer ${await page.evaluate(() => JSON.parse(localStorage.getItem("xy-growth-intelligence:supabase-session")!).accessToken)}` };
}
test("personal deletion persists while shared deletion requires author or admin", async ({ page }) => {
  const admin = await login(page, "admin");
  const body = `Note deletion acceptance ${Date.now()}`;
  const response = await page.request.post(`${api}/notes`, { headers: admin, data: { body } });
  expect(response.status()).toBe(201);
  const id = (await response.json()).id;
  try {
    await page.getByRole("button", { name: "Sign out", exact: true }).first().click();
    const manager = await login(page, "management");
    await page.goto("/notes");
    const card = page.getByRole("article").filter({ hasText: body });
    await expect(card.getByRole("button", { name: "Delete for everyone" })).toHaveCount(0);
    expect((await page.request.delete(`${api}/notes/${id}`, { headers: manager })).status()).toBe(403);
    page.once("dialog", (dialog) => dialog.accept());
    await card.getByRole("button", { name: "Delete for myself" }).click();
    await expect(card).toHaveCount(0);
    await page.reload();
    await expect(page.getByRole("heading", { name: "Staff Notes" })).toBeVisible();
    await expect(card).toHaveCount(0);
    expect((await (await page.request.get(`${api}/inbox`, { headers: manager })).json()).unread_note_ids).not.toContain(id);
    expect((await page.request.get(`${api}/notes/${id}`, { headers: admin })).status()).toBe(200);
    await page.getByRole("button", { name: "Sign out", exact: true }).first().click();
    await login(page, "admin");
    await page.goto("/notes");
    await expect(card.getByRole("button", { name: "Delete for everyone" })).toBeVisible();
    page.once("dialog", (dialog) => dialog.accept());
    await card.getByRole("button", { name: "Delete for everyone" }).click();
    await expect(card).toHaveCount(0);
    expect((await page.request.get(`${api}/notes/${id}`, { headers: admin })).status()).toBe(404);
  } finally {
    await page.request.delete(`${api}/notes/${id}`, { headers: admin });
  }
});
