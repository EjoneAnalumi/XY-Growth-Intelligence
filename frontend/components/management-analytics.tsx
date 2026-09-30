"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { apiRequest } from "@/lib/api/client";
import { getUsers } from "@/lib/api/users";
import { listReports, type Report } from "@/lib/api/reports";
import { ErrorState, LoadingState } from "@/components/ui/async-state";
import { Button } from "@/components/ui/button";

type Group = { label: string; count: number; value: number; weighted: number };
type Analytics = {
  total_prospects: number; qualified_prospects: number; meetings: number; pilots: number;
  proposals: number; conversion_percent: number; average_deal_value: number;
  pipeline_groups: Record<string, Group[]>; forecast: Group[];
  icp_distribution: { label: string; count: number }[];
  win_loss_trend: { month: string; won: number; lost: number }[];
  stage_conversion: { stage: string; reached: number; progressed: number; conversion_percent: number; average_current_days: number }[];
  missing_next_action: { id: string; name: string }[];
  proposal_awaiting_response: { id: string; name: string }[];
  due_today: { id: string; title: string }[];
  upcoming_meetings: { id: string; subject: string; occurred_at: string }[];
  recent_activity: { id: string; subject: string; occurred_at: string }[];
};
const money = (value: number) => new Intl.NumberFormat("en-US", { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(value);

function ValueTable({ rows }: { rows: Group[] }) {
  return rows.length ? <div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead><tr><th className="p-2">Group</th><th className="p-2">Deals</th><th className="p-2">Value</th><th className="p-2">Weighted</th></tr></thead><tbody>{rows.map((row) => <tr key={row.label} className="border-t"><th scope="row" className="p-2 font-normal">{row.label}</th><td className="p-2">{row.count}</td><td className="p-2">{money(row.value)}</td><td className="p-2">{money(row.weighted)}</td></tr>)}</tbody></table></div> : <p className="text-sm text-muted-foreground">No matching records.</p>;
}

export function ManagementAnalytics() {
  const [data, setData] = useState<Analytics | null>(null);
  const [names, setNames] = useState<Record<string, string>>({});
  const [error, setError] = useState("");
  const [reports, setReports] = useState<Report[]>([]);
  const load = useCallback(async () => {
    setError("");
    try {
      const [result, users, reportList] = await Promise.all([apiRequest<Analytics>("/dashboard/analytics"), getUsers(), listReports()]);
      setReports(reportList.items);
      setData(result); setNames(Object.fromEntries(users.map((u) => [u.id, u.full_name])));
    } catch (caught) { setError(caught instanceof Error ? caught.message : "Analytics could not be loaded."); }
  }, []);
  useEffect(() => { void load(); }, [load]);
  if (error) return <ErrorState title="Management analytics unavailable" description={error} onRetry={load} />;
  if (!data) return <LoadingState title="Loading management analytics..." />;
  const metrics = { Prospects: data.total_prospects, Qualified: data.qualified_prospects, Meetings: data.meetings, "Active pilots": data.pilots, Proposals: data.proposals, "Win rate (closed deals)": `${data.conversion_percent}%`, "Average deal value": money(data.average_deal_value) };
  return <section className="space-y-5" aria-label="Management analytics">
    <div className="flex items-center justify-between"><h2 className="text-xl font-semibold">Management analytics</h2><Button variant="outline" onClick={load}>Refresh analytics</Button></div>
    <article className="rounded-md border bg-card p-4"><h3 className="font-semibold">Reports generated: {reports.length}</h3><p className="text-sm text-muted-foreground">Most recent reports across all workflow statuses.</p>{[...reports].sort((a, b) => b.createdAt.localeCompare(a.createdAt)).slice(0, 5).map((report) => <Link key={report.id} href="/reports" className="mt-2 block text-sm text-primary underline">{report.title} · {report.status}</Link>)}{!reports.length && <p>No reports yet.</p>}</article>
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">{Object.entries(metrics).map(([label, value]) => <div key={label} className="rounded-md border bg-card p-4"><p className="text-sm text-muted-foreground">{label}</p><p className="mt-2 text-2xl font-semibold">{value}</p></div>)}</div>
    <div className="grid gap-5 xl:grid-cols-2">{Object.entries(data.pipeline_groups).map(([key, rows]) => <article key={key} className="min-w-0 rounded-md border bg-card p-4"><h3 className="mb-3 font-semibold">Open pipeline by {key === "owner_id" ? "owner" : key === "headquarters_country" ? "country" : key.replaceAll("_", " ")}</h3><ValueTable rows={key === "owner_id" ? rows.map((r) => ({ ...r, label: names[r.label] ?? r.label })) : rows} /></article>)}
      <article className="min-w-0 rounded-md border bg-card p-4"><h3 className="mb-3 font-semibold">Monthly closing forecast</h3><p className="text-sm text-muted-foreground">Open deals grouped by expected close month; no date stays unscheduled.</p><ValueTable rows={data.forecast} /></article>
      <article className="rounded-md border bg-card p-4"><h3 className="mb-3 font-semibold">ICP distribution</h3>{data.icp_distribution.map((r) => <div key={r.label} className="mb-2 grid grid-cols-[5rem_1fr_3rem] items-center gap-2 text-sm"><span>{r.label}</span><meter className="w-full" min={0} max={Math.max(1, ...data.icp_distribution.map((v) => v.count))} value={r.count} aria-label={`Companies with ICP ${r.label}`} /><span>{r.count}</span></div>)}</article>
      <article className="rounded-md border bg-card p-4"><h3 className="mb-3 font-semibold">Win/loss trend</h3><p className="text-sm text-muted-foreground">Currently closed deals by their latest entry into the current closing stage (UTC).</p>{data.win_loss_trend.map((r) => <p key={r.month} className="mt-2 text-sm">{r.month}: {r.won} won / {r.lost} lost</p>)}{!data.win_loss_trend.length && <p>No closed deals.</p>}</article>
    </div>
    <article className="overflow-x-auto rounded-md border bg-card p-4"><h3 className="font-semibold">Stage conversion and duration</h3><p className="my-2 text-sm text-muted-foreground">Progression counts distinct deals that moved forward from each stage, excluding moves to Lost. Duration averages current occupants; historical dwell time is not included.</p><table className="w-full text-left text-sm"><thead><tr>{["Stage", "Reached", "Progressed", "Conversion", "Average current days"].map((h) => <th className="p-2" key={h}>{h}</th>)}</tr></thead><tbody>{data.stage_conversion.map((r) => <tr key={r.stage} className="border-t"><th scope="row" className="p-2 font-normal">{r.stage}</th><td>{r.reached}</td><td>{r.progressed}</td><td>{r.conversion_percent}%</td><td>{r.average_current_days}</td></tr>)}</tbody></table></article>
    <div className="grid gap-5 lg:grid-cols-2">{[["Missing next action", data.missing_next_action], ["Proposals awaiting response", data.proposal_awaiting_response]].map(([title, items]) => <article className="rounded-md border bg-card p-4" key={title as string}><h3 className="font-semibold">{title as string}</h3>{(items as { id: string; name: string }[]).map((item) => <Link key={item.id} className="mt-2 block text-sm text-primary underline" href={`/opportunities/${item.id}`}>{item.name}</Link>)}{!(items as unknown[]).length && <p className="mt-2 text-sm">None.</p>}</article>)}
      <article className="rounded-md border bg-card p-4"><h3 className="font-semibold">Tasks due today (UTC)</h3>{data.due_today.map((t) => <p className="mt-2 text-sm" key={t.id}>{t.title}</p>)}{!data.due_today.length && <p className="mt-2 text-sm">None.</p>}<Link href="/tasks" className="text-sm text-primary underline">Manage tasks</Link></article>
      <article className="rounded-md border bg-card p-4"><h3 className="font-semibold">Upcoming meetings</h3>{data.upcoming_meetings.map((a) => <p className="mt-2 text-sm" key={a.id}>{a.subject} · {new Date(a.occurred_at).toLocaleString()}</p>)}{!data.upcoming_meetings.length && <p className="mt-2 text-sm">None.</p>}</article>
      <article className="rounded-md border bg-card p-4"><h3 className="font-semibold">Recent activity</h3>{data.recent_activity.map((a) => <p className="mt-2 text-sm" key={a.id}>{a.subject} · {new Date(a.occurred_at).toLocaleString()}</p>)}{!data.recent_activity.length && <p className="mt-2 text-sm">None.</p>}</article>
    </div>
  </section>;
}
