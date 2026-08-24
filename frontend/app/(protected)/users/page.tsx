"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { getAuditLogs, getUsers, inviteUser, updateUser, type AuditLog, type CurrentUser, type UserProfile } from "@/lib/api/users";

const roles: CurrentUser["role"][] = ["admin", "management", "business_development", "technical_analyst", "read_only"];

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
    <div><p className="text-sm font-medium text-primary">Administration</p><h1 className="mt-1 text-2xl font-semibold sm:text-3xl">Users</h1><p className="mt-2 text-sm text-muted-foreground">Invite staff, assign least-privilege roles, and deactivate access. There is no public registration.</p></div>
    <form onSubmit={submit} className="grid gap-4 rounded-md border bg-card p-5 shadow-sm md:grid-cols-3">
      <div className="space-y-2"><Label htmlFor="invite-name">Full name</Label><Input id="invite-name" required value={fullName} onChange={(event) => setFullName(event.target.value)} /></div>
      <div className="space-y-2"><Label htmlFor="invite-email">Work email</Label><Input id="invite-email" type="email" required value={email} onChange={(event) => setEmail(event.target.value)} /></div>
      <div className="space-y-2"><Label htmlFor="invite-role">Initial role</Label><select id="invite-role" className="h-10 w-full rounded-md border bg-background px-3 text-sm" value={role} onChange={(event) => setRole(event.target.value as CurrentUser["role"])}>{roles.map((item) => <option key={item} value={item}>{item.replaceAll("_", " ")}</option>)}</select></div>
      <Button type="submit" className="w-fit">Send invitation</Button>
    </form>
    {message ? <p role="status" className="text-sm text-muted-foreground">{message}</p> : null}
    <section className="space-y-3">{users.map((user) => <article key={user.id} className="flex flex-col gap-3 rounded-md border bg-card p-4 sm:flex-row sm:items-center sm:justify-between">
      <div><p className="font-medium">{user.full_name}</p><p className="text-sm text-muted-foreground">{user.email} · Last login {user.last_login_at ? new Date(user.last_login_at).toLocaleString() : "never"}</p></div>
      <div className="flex gap-2"><select aria-label={`Role for ${user.full_name}`} className="h-10 rounded-md border bg-background px-3 text-sm" value={user.role} onChange={async (event) => { const updated=await updateUser(user.id,{role:event.target.value as CurrentUser["role"]}); setUsers((items)=>items.map((item)=>item.id===updated.id?updated:item)); }}>{roles.map((item)=><option key={item} value={item}>{item.replaceAll("_"," ")}</option>)}</select><Button type="button" variant="outline" onClick={async()=>{const updated=await updateUser(user.id,{active:!user.active});setUsers((items)=>items.map((item)=>item.id===updated.id?updated:item));}}>{user.active?"Deactivate":"Reactivate"}</Button></div>
    </article>)}</section>
    <section className="rounded-md border bg-card p-5 shadow-sm"><h2 className="font-semibold">Recent audit events</h2><p className="mt-1 text-sm text-muted-foreground">Important CRM writes recorded with the responsible staff profile.</p><div className="mt-3 space-y-2">{auditLogs.slice(0,20).map((log)=><div key={log.id} className="rounded-md border bg-background p-3 text-sm"><p><strong>{log.user_name ?? "Seed/system"}</strong> {log.action} {log.entity_type.replaceAll("_"," ")}</p><p className="mt-1 text-xs text-muted-foreground">{new Date(log.changed_at).toLocaleString()} · {log.entity_id}</p></div>)}</div></section>
  </div>;
}
