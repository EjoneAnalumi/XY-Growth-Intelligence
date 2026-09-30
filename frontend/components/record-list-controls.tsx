"use client";
import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export function useRecordList<T extends { createdAt?: string }>(records: T[], text: (item: T) => string, label: string) {
  const [query, setQuery] = useState("");
  const [page, setPage] = useState(0);
  const [sort, setSort] = useState("newest");
  const filtered = records.filter((r) => text(r).toLowerCase().includes(query.toLowerCase()))
    .sort((a, b) => sort === "newest" || sort === "oldest"
      ? ((Date.parse(b.createdAt || "") || 0) - (Date.parse(a.createdAt || "") || 0)) * (sort === "oldest" ? -1 : 1)
      : text(a).localeCompare(text(b)) * (sort === "za" ? -1 : 1));
  const lastPage = Math.max(0, Math.ceil(filtered.length / 20) - 1);
  const current = Math.min(page, lastPage);
  return {
    visible: filtered.slice(current * 20, (current + 1) * 20),
    controls: <div className="mb-4 flex flex-wrap items-center gap-3">
      <Input className="max-w-sm" aria-label={`Search ${label}`} placeholder={`Search ${label}`} value={query} onChange={(e) => { setQuery(e.target.value); setPage(0); }} />
      <label className="text-sm">Sort {label}<select aria-label={`Sort ${label}`} className="ml-2 h-10 rounded-md border bg-background px-3" value={sort} onChange={(e) => { setSort(e.target.value); setPage(0); }}><option value="newest">Newest first</option><option value="oldest">Oldest first</option><option value="az">A–Z</option><option value="za">Z–A</option></select></label>
      <Button variant="outline" disabled={current === 0} onClick={() => setPage(current - 1)}>Previous</Button>
      <span className="text-sm" role="status">Page {current + 1} of {lastPage + 1} · {filtered.length} records</span>
      <Button variant="outline" disabled={current >= lastPage} onClick={() => setPage(current + 1)}>Next</Button>
      {!filtered.length && <p>No matching records.</p>}
    </div>,
  };
}
