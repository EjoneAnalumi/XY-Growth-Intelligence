"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { FormEvent, useCallback, useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { ErrorState, LoadingState } from "@/components/ui/async-state";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { apiRequest } from "@/lib/api/client";
import { listReports, type Report } from "@/lib/api/reports";
import { getUsers, type UserProfile } from "@/lib/api/users";
import { getSession } from "@/lib/auth";

type RecordData = Record<string, string | number | boolean | string[] | null>;
type Timeline = {
  timeline: { id: string; kind: string; at: string; title: string }[];
  contacts?: { id: string; first_name: string; last_name: string }[];
  opportunities: { id: string; name: string }[];
  tasks: { id: string; title: string; status: string }[];
  score?: { score: number; explanations: { rule_id: string; label: string; points: number; max_points: number; explanation: string }[] } | null;
};
const companyFields = ["name", "domain", "website", "industry", "headquarters_country", "headquarters_city", "company_size", "employee_range", "employee_count", "annual_revenue_eur", "cloud_usage", "regulatory_context", "lead_source", "tags", "status", "lifecycle_stage", "next_action", "next_action_due_at", "last_activity_at", "strategic_importance"];
const contactFields = ["first_name", "last_name", "email", "phone", "title", "department", "role", "influence", "decision_category", "channels", "last_contact_at", "next_follow_up_at"];
const lists = ["cloud_usage", "regulatory_context", "tags", "channels"];
const numbers = ["employee_count", "annual_revenue_eur", "strategic_importance"];
const options: Record<string, string[]> = {
  status: ["prospect", "qualified", "customer", "partner", "inactive"],
  lifecycle_stage: ["prospect", "qualified", "customer", "archived"],
  influence: ["", "high", "medium", "low", "unknown"],
  decision_category: ["", "buyer", "champion", "influencer", "procurement", "unknown"],
};
function localInput(value: string) {
  if (!value) return "";
  const date = new Date(value);
  return new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
}

export function RecordProfile({ kind }: { kind: "companies" | "contacts" }) {
  const { id } = useParams<{ id: string }>();
  const [record, setRecord] = useState<RecordData | null>(null);
  const [values, setValues] = useState<Record<string, string>>({});
  const [related, setRelated] = useState<Timeline | null>(null);
  const [reports, setReports] = useState<Report[]>([]);
  const [users, setUsers] = useState<UserProfile[]>([]);
  const [reportError, setReportError] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const canWrite = ["admin", "management", "business_development"].includes(getSession()?.profile?.role ?? "");
  const fields = kind === "companies" ? companyFields : contactFields;
  const load = useCallback(async () => {
    setError("");
    try {
      const [item, timeline, staff] = await Promise.all([apiRequest<RecordData>(`/${kind}/${id}`), apiRequest<Timeline>(`/${kind}/${id}/timeline`), getUsers()]);
      setRecord(item); setRelated(timeline); setUsers(staff);
      setValues(Object.fromEntries(Object.entries(item).map(([key, value]) => [key, Array.isArray(value) ? value.join(", ") : key.endsWith("_at") && value ? localInput(String(value)) : String(value ?? "")])));
    } catch (caught) { setError(caught instanceof Error ? caught.message : "Profile could not be loaded."); }
  }, [kind, id]);
  useEffect(() => { void load(); }, [load]);
  useEffect(() => {
    if (kind === "companies") void listReports().then((r) => setReports(r.items.filter((item) => item.companyId === id))).catch(() => setReportError("Reports could not be loaded. Open Reports to retry."));
  }, [kind, id]);
  async function submit(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError(""); setMessage("");
    const payload: Record<string, unknown> = {};
    for (const key of fields) {
      const value = values[key] ?? "";
      payload[key] = lists.includes(key) ? value.split(",").map((v) => v.trim()).filter(Boolean) : numbers.includes(key) ? (value === "" ? null : Number(value)) : key.endsWith("_at") ? (value ? new Date(value).toISOString() : null) : value || null;
    }
    if (kind === "companies") payload.owner_id = values.owner_id || null;
    try { await apiRequest(`/${kind}/${id}`, { method: "PATCH", body: JSON.stringify(payload) }); await load(); setMessage("Profile saved. Recalculate ICP to reflect new intelligence."); }
    catch (caught) { setError(caught instanceof Error ? caught.message : "Profile could not be saved."); }
    finally { setBusy(false); }
  }
  return <div className="space-y-5">
    <Link href={`/${kind}`} className="text-primary underline">Back to {kind}</Link>
    {error && <ErrorState title="Profile request failed" description={error} onRetry={load} />}
    {!record ? <LoadingState title="Loading profile..." /> : <>
      <h1 className="text-3xl font-semibold">{String(record.name ?? `${record.first_name} ${record.last_name}`)}</h1>
      {kind === "contacts" && <Link className="text-primary underline" href={`/companies/${record.company_id}`}>Company profile</Link>}
      <form onSubmit={submit} className="space-y-4 rounded-md border bg-card p-5"><h2 className="text-xl font-semibold">Intelligence and follow-up</h2><div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">{fields.map((key) => <div key={key}><Label htmlFor={key}>{key.replaceAll("_", " ")}{lists.includes(key) ? " (comma separated)" : ""}</Label>{options[key] ? <select id={key} disabled={!canWrite} className="h-10 w-full rounded-md border bg-background px-3" value={values[key] ?? ""} onChange={(e) => setValues({ ...values, [key]: e.target.value })}>{options[key].map((v) => <option key={v} value={v}>{v || "Not recorded"}</option>)}</select> : <Input id={key} disabled={!canWrite} type={numbers.includes(key) ? "number" : key.endsWith("_at") ? "datetime-local" : key === "email" ? "email" : "text"} required={["name", "first_name", "last_name", "strategic_importance"].includes(key)} min={numbers.includes(key) ? 0 : undefined} max={key === "strategic_importance" ? 5 : undefined} step={key === "annual_revenue_eur" ? "0.01" : undefined} value={values[key] ?? ""} onChange={(e) => setValues({ ...values, [key]: e.target.value })} />}</div>)}
        {kind === "companies" && <div><Label htmlFor="profile-owner">Owner</Label><select id="profile-owner" disabled={!canWrite} className="h-10 w-full rounded-md border bg-background px-3" value={values.owner_id ?? ""} onChange={(e) => setValues({ ...values, owner_id: e.target.value })}><option value="">Unassigned</option>{users.map((u) => <option key={u.id} value={u.id}>{u.full_name}</option>)}</select></div>}
      </div>{canWrite && <Button disabled={busy}>{busy ? "Saving..." : "Save profile"}</Button>}{message && <p role="status">{message}</p>}</form>
      {related?.score && <section className="rounded-md border bg-card p-5"><h2 className="font-semibold">Stored ICP score: {related.score.score}/100</h2>{related.score.explanations.map((r) => <p className="mt-2 text-sm" key={r.rule_id}>{r.label}: {r.points}/{r.max_points} — {r.explanation}</p>)}<Link className="text-primary underline" href="/companies">Calculate score and view recommendations</Link></section>}
      <div className="grid gap-5 lg:grid-cols-2">
        {kind === "companies" && <section className="rounded-md border bg-card p-5"><h2 className="font-semibold">Contacts</h2>{related?.contacts?.map((c) => <Link className="mt-2 block text-primary underline" key={c.id} href={`/contacts/${c.id}`}>{c.first_name} {c.last_name}</Link>)}{!related?.contacts?.length && <p>No contacts.</p>}</section>}
        <section className="rounded-md border bg-card p-5"><h2 className="font-semibold">Opportunities</h2>{related?.opportunities.map((o) => <Link className="mt-2 block text-primary underline" key={o.id} href={`/opportunities/${o.id}`}>{o.name}</Link>)}{!related?.opportunities.length && <p>No opportunities.</p>}</section>
        <section className="rounded-md border bg-card p-5"><h2 className="font-semibold">Tasks</h2>{related?.tasks.map((t) => <p className="mt-2 text-sm" key={t.id}>{t.title}: {t.status}</p>)}{!related?.tasks.length && <p>No directly linked tasks.</p>}<Link href="/tasks" className="text-primary underline">Manage tasks</Link></section>
        {kind === "companies" && <section className="rounded-md border bg-card p-5"><h2 className="font-semibold">Reports</h2>{reportError && <p role="alert">{reportError}</p>}{reports.map((r) => <p className="mt-2 text-sm" key={r.id}>{r.title}: {r.status}</p>)}{!reports.length && !reportError && <p>No reports.</p>}<Link href="/reports" className="text-primary underline">Review reports</Link></section>}
      </div>
      <section className="rounded-md border bg-card p-5"><h2 className="font-semibold">Relationship timeline</h2>{related?.timeline.map((e) => <div className="mt-3 border-t pt-3 text-sm" key={`${e.kind}-${e.id}`}><p className="font-medium">{e.title}</p><p className="text-muted-foreground">{e.kind} · {new Date(e.at).toLocaleString()}</p></div>)}{!related?.timeline.length && <p>No relationship activity yet.</p>}</section>
    </>}
  </div>;
}
