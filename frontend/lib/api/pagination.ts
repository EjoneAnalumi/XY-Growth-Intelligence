import { apiRequest } from "@/lib/api/client";

// Fetch every API page so selectors and client-side filters never silently omit records.
export async function allPages<T>(path: string): Promise<T[]> {
  const first = await apiRequest<{ items: T[]; total: number }>(path);
  const items = [...first.items];
  while (items.length < first.total) {
    const page = await apiRequest<{ items: T[]; total: number }>(`${path}?limit=100&offset=${items.length}`);
    if (!page.items.length) break;
    items.push(...page.items);
  }
  return items;
}
