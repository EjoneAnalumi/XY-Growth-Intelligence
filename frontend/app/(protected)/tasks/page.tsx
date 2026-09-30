"use client";

import Link from "next/link";
import { FormEvent, useCallback, useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { ErrorState, LoadingState } from "@/components/ui/async-state";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { getTasks, createTask, completeTask } from "@/lib/api/tasks";
import { getUsers, type UserProfile } from "@/lib/api/users";
import { getSession } from "@/lib/auth";
import { emptyInbox, getInbox, markRead, refreshInbox } from "@/lib/api/inbox";
import type { Task, TaskFormValues } from "@/types/activity-task";

const initial: TaskFormValues = { title: "", description: "", companyId: "", opportunityId: "", dueAt: "", ownerId: "", priority: "medium", status: "open" };

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [users, setUsers] = useState<UserProfile[]>([]);
  const [values, setValues] = useState(initial);
  const [filter, setFilter] = useState("open");
  const [search, setSearch] = useState("");
  const [owner, setOwner] = useState("mine");
  const [sort, setSort] = useState("newest");
  const [inbox, setInbox] = useState(emptyInbox);
  const [outcomes, setOutcomes] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const profile = getSession()?.profile;
  const role = profile?.role;
  const canWrite = ["admin", "management", "business_development"].includes(role ?? "");
  const load = useCallback(async () => {
    setLoading(true); setError("");
    try { const [items, staff] = await Promise.all([getTasks(), getUsers()]); setTasks(items); setUsers(staff); setInbox(await getInbox()); }
    catch (caught) { setError(caught instanceof Error ? caught.message : "Tasks could not be loaded."); }
    finally { setLoading(false); }
  }, []);
  useEffect(() => { void load(); }, [load]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!values.title.trim()) { setError("Task title is required."); return; }
    setBusy(true); setError(""); setMessage("");
    try {
      const task = await createTask({ ...values, title: values.title.trim(), dueAt: values.dueAt ? new Date(values.dueAt).toISOString() : "" });
      setTasks((items) => [task, ...items]); setValues(initial); setMessage("Task created."); refreshInbox(); setInbox(await getInbox());
    } catch (caught) { setError(caught instanceof Error ? caught.message : "Task could not be created."); }
    finally { setBusy(false); }
  }
  async function complete(task: Task) {
    setBusy(true); setError(""); setMessage("");
    try {
      const updated = await completeTask(task.id, outcomes[task.id] ?? "");
      setTasks((items) => items.map((item) => item.id === task.id ? updated : item)); setMessage("Task completed."); refreshInbox(); setInbox(await getInbox());
    } catch (caught) { setError(caught instanceof Error ? caught.message : "Task could not be completed."); }
    finally { setBusy(false); }
  }
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const tomorrow = new Date(today); tomorrow.setDate(today.getDate() + 1);
  const weekEnd = new Date(today); weekEnd.setDate(today.getDate() + 7);
  const visible = tasks.filter((task) => {
    const open = !["completed", "cancelled"].includes(task.status);
    const due = task.dueAt ? new Date(task.dueAt) : null;
    return task.title.toLowerCase().includes(search.toLowerCase()) && (owner === "all" || (owner === "mine" && (!task.ownerId || task.ownerId === profile?.id)) || (owner === "unassigned" && !task.ownerId) || task.ownerId === owner) && (
      filter === "all" || (filter === "open" && open) || (filter === "completed" && task.status === "completed") ||
      (open && due && ((filter === "overdue" && due < now) || (filter === "today" && due >= today && due < tomorrow) || (filter === "week" && due >= today && due < weekEnd))) ||
      (filter === "undated" && open && !due)
    );
  }).sort((a, b) => {
    if (owner === "mine") { const group = Number(b.ownerId === profile?.id) - Number(a.ownerId === profile?.id); if (group) return group; }
    if (sort === "due") return (a.dueAt ? Date.parse(a.dueAt) : Infinity) - (b.dueAt ? Date.parse(b.dueAt) : Infinity) || b.createdAt.localeCompare(a.createdAt);
    if (sort === "az" || sort === "za") return a.title.localeCompare(b.title) * (sort === "za" ? -1 : 1);
    return (b.createdAt || "").localeCompare(a.createdAt || "") * (sort === "oldest" ? -1 : 1);
  });
  return <div className="space-y-5">
    <div><h1 className="text-3xl font-semibold">Tasks</h1><p className="mt-2 text-sm text-muted-foreground">Your assigned tasks appear first, followed by unassigned tasks. Use Filter owner to see the team. Dates use your local time.</p></div>
    {canWrite && <form onSubmit={submit} className="grid gap-4 rounded-md border bg-card p-5 sm:grid-cols-2">
      <div><Label htmlFor="task-title">Title</Label><Input id="task-title" required maxLength={255} value={values.title} onChange={(e) => setValues({ ...values, title: e.target.value })} /></div>
      <div><Label htmlFor="task-due">Due date</Label><Input id="task-due" type="datetime-local" value={values.dueAt} onChange={(e) => setValues({ ...values, dueAt: e.target.value })} /></div>
      <div><Label htmlFor="task-owner">Owner</Label><select id="task-owner" className="h-10 w-full rounded-md border bg-background px-3" value={values.ownerId} onChange={(e) => setValues({ ...values, ownerId: e.target.value })}><option value="">Assign to me</option><option value="unassigned">Unassigned</option>{users.filter((u) => u.active && u.role !== "read_only").map((u) => <option key={u.id} value={u.id}>{u.full_name}</option>)}</select></div>
      <div><Label htmlFor="task-priority">Priority</Label><select id="task-priority" className="h-10 w-full rounded-md border bg-background px-3" value={values.priority} onChange={(e) => setValues({ ...values, priority: e.target.value as TaskFormValues["priority"] })}>{["low", "medium", "high", "urgent"].map((p) => <option key={p}>{p}</option>)}</select></div>
      <div className="sm:col-span-2"><Label htmlFor="task-description">Description</Label><Input id="task-description" value={values.description} onChange={(e) => setValues({ ...values, description: e.target.value })} /></div>
      <Button className="w-fit" disabled={busy}>Create task</Button>
    </form>}
    <div className="grid gap-3 sm:grid-cols-3">
      <div><Label htmlFor="task-search">Search tasks</Label><Input id="task-search" value={search} onChange={(e) => setSearch(e.target.value)} /></div>
      <div><Label htmlFor="task-filter">Due/status filter</Label><select id="task-filter" className="h-10 w-full rounded-md border bg-background px-3" value={filter} onChange={(e) => setFilter(e.target.value)}>{[["open", "Open"], ["today", "Due today"], ["week", "Next seven days"], ["overdue", "Overdue"], ["undated", "No due date"], ["completed", "Completed"], ["all", "All"]].map(([v, label]) => <option key={v} value={v}>{label}</option>)}</select></div>
      <div><Label htmlFor="owner-filter">Filter owner</Label><select id="owner-filter" className="h-10 w-full rounded-md border bg-background px-3" value={owner} onChange={(e) => setOwner(e.target.value)}><option value="mine">Mine, then unassigned</option><option value="all">All owners</option><option value="unassigned">Unassigned only</option>{users.map((u) => <option key={u.id} value={u.id}>{u.full_name}</option>)}</select></div>
    </div>
    <div className="flex flex-wrap items-center gap-4"><Label htmlFor="task-sort">Sort tasks</Label><select id="task-sort" className="h-10 rounded-md border bg-background px-3" value={sort} onChange={(e) => setSort(e.target.value)}><option value="newest">Newest first</option><option value="oldest">Oldest first</option><option value="due">Due date: earliest first</option><option value="az">A-Z</option><option value="za">Z-A</option></select><p className="text-sm">{inbox.unread_task_ids.length} unseen assignments | {inbox.overdue_tasks} overdue | {inbox.due_soon_tasks} due within 24 hours</p><Button variant="outline" onClick={load}>Refresh tasks</Button></div>
    {error && <ErrorState title="Task request failed" description={error} onRetry={load} />}
    {message && <p role="status">{message}</p>}
    {loading ? <LoadingState title="Loading tasks..." /> : <section className="space-y-3" aria-label="Task list">
      {!visible.length && <p className="text-muted-foreground">No tasks match these filters.</p>}
      {visible.map((task) => <article key={task.id} className="space-y-2 rounded-md border bg-card p-4">
        <h2 className="font-semibold">{task.title} {inbox.unread_task_ids.includes(task.id) && <span className="ml-2 text-xs text-primary">New assignment</span>}</h2><p className="text-sm">{task.description}</p>
        <p className="text-sm text-muted-foreground">{users.find((u) => u.id === task.ownerId)?.full_name ?? "Unassigned"} | {task.priority} | {task.status} | {task.dueAt ? new Date(task.dueAt).toLocaleString() : "No due date"}</p>
        <p className="text-xs text-muted-foreground">Created {new Date(task.createdAt).toLocaleString()} | Assigned by {users.find((u) => u.id === (task.assignedBy || task.createdBy))?.full_name ?? "Not recorded"} to {users.find((u) => u.id === task.ownerId)?.full_name ?? "Unassigned"}</p>
        {inbox.unread_task_ids.includes(task.id) && <Button variant="outline" onClick={async () => { try { await markRead("tasks", task.id); setInbox(await getInbox()); } catch { setError("Task could not be marked as seen."); } }}>Mark seen</Button>}
        {task.opportunityId && <Link className="text-sm text-primary underline" href={`/opportunities/${task.opportunityId}`}>Open opportunity</Link>}
        {task.completedAt && <p className="text-sm">Completed {new Date(task.completedAt).toLocaleString()}{task.outcome ? `: ${task.outcome}` : ""}</p>}
        {(canWrite || (role === "technical_analyst" && task.ownerId === profile?.id)) && !["completed", "cancelled"].includes(task.status) && <div className="flex flex-wrap items-end gap-2"><div><Label htmlFor={`outcome-${task.id}`}>Outcome</Label><Input id={`outcome-${task.id}`} value={outcomes[task.id] ?? ""} onChange={(e) => setOutcomes({ ...outcomes, [task.id]: e.target.value })} /></div><Button disabled={busy} onClick={() => complete(task)}>Complete</Button></div>}
      </article>)}
    </section>}
  </div>;
}
