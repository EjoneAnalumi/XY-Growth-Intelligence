import { test as base, expect } from "@playwright/test";

// Remove only records created during this test with its known fixture naming patterns.
// Teardown runs on assertion failures too; ordinary browsing never invokes this code.
const collections = ["companies", "contacts", "opportunities", "activities", "tasks"];
export const test = base.extend<{ cleanupFixtures: void }>({
  cleanupFixtures: [async ({ request }, use) => {
    const url = process.env.DEMO_SUPABASE_URL || process.env.SUPABASE_URL;
    const key = process.env.DEMO_ANON_KEY || process.env.SUPABASE_ANON_KEY;
    if (!process.env.DEMO_PASSWORD || !url || !key) throw new Error("Live tests require local Supabase configuration for fixture cleanup.");
    if (!["localhost", "127.0.0.1"].includes(new URL(url).hostname)) throw new Error("Fixture cleanup is local-only.");
    async function authenticate() {
      const auth = await request.post(`${url}/auth/v1/token?grant_type=password`, { headers: { apikey: key! }, data: { email: "admin.demo@example.test", password: process.env.DEMO_PASSWORD } });
      expect(auth.ok()).toBeTruthy();
      return { Authorization: `Bearer ${(await auth.json()).access_token}` };
    }
    let headers = await authenticate();
    const api = "http://localhost:8000";
    async function rows(collection: string) {
      type Row = { id: string; name?: string; title?: string; subject?: string; email?: string };
      const result: Row[] = [];
      const paginated = ["companies", "contacts"].includes(collection);
      do {
        const response = await request.get(`${api}/${collection}?limit=100&offset=${result.length}`, { headers });
        expect(response.ok()).toBeTruthy();
        const data = await response.json();
        result.push(...data.items);
        if (!paginated || !data.items.length || result.length >= data.total) break;
      } while (true);
      return result;
    }

    const before = new Map<string, Set<string>>();
    for (const collection of collections) before.set(collection, new Set((await rows(collection)).map((row) => row.id)));
    try { await use(); }
    finally {
      // Account sign-out flows can invalidate the setup session.
      headers = await authenticate();
      for (const collection of [...collections].reverse()) {
        for (const row of await rows(collection)) {
          if (before.get(collection)!.has(row.id)) continue;
          const label = row.name || row.title || row.subject || row.email || "";
          if (!/^(Handover Synthetic \d+|CSV Handover \d+|Synthetic Completion \d+|Synthetic assessment \d+|Synthetic standalone \d+|Synthetic CSV \d+|Synthetic role verification|Synthetic follow-up|Synthetic discovery meeting|reviewer-\d+@example\.test)$/.test(label)) continue;
          const response = await request.delete(`${api}/${collection}/${row.id}`, { headers });
          expect(response.ok(), `Clean up ${collection} fixture`).toBeTruthy();
        }
      }
    }
  }, { auto: true }],
});
export { expect };
