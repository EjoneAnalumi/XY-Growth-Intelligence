"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { deleteUser, getAuditLogs, getUsers, inviteUser, updateUser, type AuditLog, type CurrentUser, type UserProfile } from "@/lib/api/users";

const roles: CurrentUser["role"][] = ["admin", "management", "business_development", "technical_analyst", "read_only"];

function UserRow({ user, onChanged, onDeleted, onMessage }: { user: UserProfile; onChanged: (user: UserProfile) => void; onDeleted: (id: string) => void; onMessage: (message: string) => void }) {
  const [fullName, setFullName] = useState(user.full_name);
  const [email, setEmail] = useState(user.email);
  const [role, setRole] = useState(user.role);
  const [saving, setSaving] = useState(false);

  async function save() {
    setSaving(true);
    try {
      const updated = await updateUser(user.id, { full_name: fullName.trim(), email: email.trim(), role });
      onChanged(updated);
      onMessage(`${updated.full_name} was updated.`);
    } catch (error) { onMessage(error instanceof Error ? error.message : "User update failed."); }
    finally { setSaving(false); }
  }

  async function toggleActive() {
    try {
      const updated = await updateUser(user.id, { active: !user.active });
      onChanged(updated);
      onMessage(`${updated.full_name} was ${updated.active ? "reactivated" : "deactivated"}.`);
    } catch (error) { onMessage(error instanceof Error ? error.message : "User status update failed."); }
  }

  async function remove() {
    if (!window.confirm(`Delete ${user.full_name}? This permanently removes their login.`)) return;
    try {
      await deleteUser(user.id);
      onDeleted(user.id);
      onMessage(`${user.full_name} was deleted.`);
    } catch (error) { onMessage(error instanceof Error ? error.message : "User deletion failed."); }
  }

  return <article className="space-y-3 rounded-md border bg-card p-4">
    <div className="grid gap-3 md:grid-cols-3">
      <div className="space-y-1"><Label htmlFor={`name-${user.id}`}>Full name</Label><Input id={`name-${user.id}`} value={fullName} onChange={(event) => setFullName(event.target.value)} /></div>
      <div className="space-y-1"><Label htmlFor={`email-${user.id}`}>Email</Label><Input id={`email-${user.id}`} type="email" value={email} onChange={(event) => setEmail(event.target.value)} /></div>
      <div className="space-y-1"><Label htmlFor={`role-${user.id}`}>Role</Label><select id={`role-${user.id}`} className="h-10 w-full rounded-md border bg-background px-3 text-sm" value={role} onChange={(event) => setRole(event.target.value as CurrentUser["role"])}>{roles.map((item) => <option key={item} value={item}>{item.replaceAll("_", " ")}</option>)}</select></div>
    </div>
    <p className="text-xs text-muted-foreground">{user.active ? "Active" : "Inactive"} · Last login {user.last_login_at ? new Date(user.last_login_at).toLocaleString() : "never"}</p>
    <div className="flex flex-wrap gap-2">
      <Button type="button" onClick={save} disabled={saving}>{saving ? "Saving..." : "Save changes"}</Button>
      <Button type="button" variant="outline" onClick={toggleActive}>{user.active ? "Deactivate" : "Reactivate"}</Button>
      <Button type="button" variant="outline" className="text-destructive" onClick={remove}>Delete user</Button>
    </div>
  </article>;
}

export default function UsersPage() {
  const [users, setUsers] = useState<UserProfile[]>([]);
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [role, setRole] = useState<CurrentUser["role"]>("read_only");
  const [message, setMessage] = useState<string | null>(null);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const load = useCallback(async () => { try { const [loadedUsers, logs] = await Promise.all([getUsers(), getAuditLogs()]); setUsers(loadedUsers); setAuditLogs(logs); } catch (error) { setMessage(error instanceof Error ? error.message : "Users could not be loaded."); } }, []);
  useEffect(() => { void load(); }, [load]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    try {
      await inviteUser({ email: email.trim(), fullName: fullName.trim(), role });
      setEmail(""); setFullName(""); setMessage("Invitation sent."); await load();
    } catch (error) { setMessage(error instanceof Error ? error.message : "Invitation failed."); }
  }

  return <div className="space-y-5">
    <div><p className="text-sm font-medium text-primary">Administration</p><h1 className="mt-1 text-2xl font-semibold sm:text-3xl">Users</h1><p className="mt-2 text-sm text-muted-foreground">Invite staff and manage their name, email, role, status, or account. There is no public registration.</p></div>
    <form onSubmit={submit} className="grid gap-4 rounded-md border bg-card p-5 shadow-sm md:grid-cols-3">
      <div className="space-y-2"><Label htmlFor="invite-name">Full name</Label><Input id="invite-name" required value={fullName} onChange={(event) => setFullName(event.target.value)} /></div>
      <div className="space-y-2"><Label htmlFor="invite-email">Work email</Label><Input id="invite-email" type="email" required value={email} onChange={(event) => setEmail(event.target.value)} /></div>
      <div className="space-y-2"><Label htmlFor="invite-role">Initial role</Label><select id="invite-role" className="h-10 w-full rounded-md border bg-background px-3 text-sm" value={role} onChange={(event) => setRole(event.target.value as CurrentUser["role"])}>{roles.map((item) => <option key={item} value={item}>{item.replaceAll("_", " ")}</option>)}</select></div>
      <Button type="submit" className="w-fit">Send invitation</Button>
    </form>
    {message ? <p role="status" className="text-sm text-muted-foreground">{message}</p> : null}
    <section className="space-y-3">{users.map((user) => <UserRow key={user.id} user={user} onChanged={(updated) => setUsers((items) => items.map((item) => item.id === updated.id ? updated : item))} onDeleted={(id) => setUsers((items) => items.filter((item) => item.id !== id))} onMessage={setMessage} />)}</section>
    <section className="rounded-md border bg-card p-5 shadow-sm"><h2 className="font-semibold">Recent audit events</h2><p className="mt-1 text-sm text-muted-foreground">Important CRM and account changes recorded with the responsible staff profile.</p><div className="mt-3 space-y-2">{auditLogs.slice(0, 20).map((log) => <div key={log.id} className="rounded-md border bg-background p-3 text-sm"><p><strong>{log.user_name ?? "Seed/system"}</strong> {log.action} {log.entity_type.replaceAll("_", " ")}</p><p className="mt-1 text-xs text-muted-foreground">{new Date(log.changed_at).toLocaleString()} · {log.entity_id}</p></div>)}</div></section>
  </div>;
}
