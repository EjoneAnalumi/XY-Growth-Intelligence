"use client";

import { Plus, StickyNote } from "lucide-react";
import { FormEvent, useCallback, useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { ErrorState, LoadingState } from "@/components/ui/async-state";
import { deleteNote, deleteNoteForMe, createNote, getNotes, updateNote, type Note } from "@/lib/api/notes";
import { getUsers } from "@/lib/api/users";
import { emptyInbox, getInbox, markRead, refreshInbox } from "@/lib/api/inbox";
import { getSession } from "@/lib/auth";

export default function StaffNotesPage() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [body, setBody] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [userNames, setUserNames] = useState<Map<string, string>>(new Map());
  const profile = getSession()?.profile;
  const role = profile?.role;
  const [inbox, setInbox] = useState(emptyInbox);
  const [sort, setSort] = useState("newest");
  const [unreadOnly, setUnreadOnly] = useState(false);
  const canWrite = role === "admin" || role === "management" || role === "business_development" || role === "technical_analyst";

  const loadNotes = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const [loadedNotes, users] = await Promise.all([getNotes(), getUsers()]);
      setNotes(loadedNotes);
      setInbox(await getInbox());
      setUserNames(new Map(users.map((user) => [user.id, user.full_name])));
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Failed to load notes.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { void loadNotes(); }, [loadNotes]);

  async function saveNote(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!body.trim()) return;
    try {
      const created = await createNote({
        companyId: null,
        contactId: null,
        opportunityId: null,
        body: body.trim(),
      });
      setNotes((items) => [created, ...items]);
      setBody(""); refreshInbox();
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Failed to save note.");
    }
  }

  async function removeNote(note: Note, everyone: boolean) {
    if (!window.confirm(everyone ? "Delete this note for everyone? It will disappear from the team's notes." : "Delete this note for yourself? Everyone else will still be able to see it.")) return;
    try {
      if (everyone) await deleteNote(note.id);
      else await deleteNoteForMe(note.id);
      setNotes((items) => items.filter((item) => item.id !== note.id));
      setInbox(await getInbox());
      refreshInbox();
    } catch {
      setError("Note could not be deleted.");
    }
  }

  return (
    <div className="space-y-5">
      <div>
        <p className="text-sm font-medium text-primary">Team workspace</p>
        <h1 className="mt-1 text-2xl font-semibold sm:text-3xl">Staff Notes</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Shared team notes, not private messages. Unread counts are personal; your own notes are already read. Delete for myself hides a note only for you. Only its author or an admin can delete it for everyone.
        </p>
      </div>

      {canWrite ? (
        <form onSubmit={saveNote} className="rounded-md border bg-card p-5 shadow-sm">
          <label htmlFor="staff-note" className="font-semibold">New note</label>
          <textarea
            id="staff-note"
            className="mt-3 min-h-28 w-full rounded-md border bg-background px-3 py-2 text-sm"
            value={body}
            onChange={(event) => setBody(event.target.value)}
            placeholder="Write a reminder, decision, or context the team should remember..."
          />
          <Button type="submit" className="mt-3 gap-2" disabled={!body.trim()}>
            <Plus className="h-4 w-4" /> Save note
          </Button>
        </form>
      ) : (
        <p className="rounded-md border bg-card p-4 text-sm text-muted-foreground">
          Your role has read-only access to staff notes.
        </p>
      )}

      <div className="flex flex-wrap items-center gap-3"><label>Sort notes <select aria-label="Sort notes" className="h-10 rounded-md border bg-background px-3" value={sort} onChange={(e) => setSort(e.target.value)}><option value="newest">Newest first</option><option value="oldest">Oldest first</option><option value="az">A-Z</option><option value="za">Z-A</option></select></label><Button variant="outline" onClick={() => setUnreadOnly(!unreadOnly)}>{unreadOnly ? "Show all notes" : `Unread only (${inbox.unread_note_ids.length})`}</Button><Button variant="outline" onClick={loadNotes}>Refresh notes</Button></div>
      {loading ? <LoadingState title="Loading staff notes..." /> : null}
      {error ? <ErrorState title="Notes could not be loaded" description={error} onRetry={loadNotes} /> : null}

      <section className="space-y-3" aria-label="Saved staff notes">
        {!loading && notes.length === 0 ? (
          <p className="rounded-md border bg-card p-5 text-sm text-muted-foreground">No notes yet.</p>
        ) : null}
        {notes.filter((n) => !unreadOnly || inbox.unread_note_ids.includes(n.id)).sort((a, b) => sort === "newest" || sort === "oldest" ? b.createdAt.localeCompare(a.createdAt) * (sort === "oldest" ? -1 : 1) : a.body.localeCompare(b.body) * (sort === "za" ? -1 : 1)).map((note) => (
          <article key={note.id} className="rounded-md border bg-card p-4 shadow-sm">
            <div className="flex gap-3">
              <StickyNote className="mt-0.5 h-5 w-5 shrink-0 text-primary" />
              <div className="min-w-0 flex-1">
                <p className="whitespace-pre-wrap text-sm">{note.body}</p>
                <p className="mt-2 text-xs text-muted-foreground">{new Date(note.createdAt).toLocaleString()}</p>
                <p className="mt-1 text-xs text-muted-foreground">Written by {note.createdBy ? userNames.get(note.createdBy) ?? "Unknown staff member" : "Seed data"}</p>
                {inbox.unread_note_ids.includes(note.id) && <Button className="mt-2" variant="outline" onClick={async () => { try { await markRead("notes", note.id); setInbox(await getInbox()); } catch { setError("Note could not be marked as read."); } }}>Mark read</Button>}
                {canWrite && (role !== "technical_analyst" || note.createdBy === profile?.id) ? <div className="mt-3 flex gap-2">
                  <Button type="button" variant="outline" onClick={async () => {
                    const nextBody = window.prompt("Edit note", note.body);
                    if (!nextBody?.trim()) return;
                    try { const updated = await updateNote(note.id, nextBody.trim());
                    setNotes((items) => items.map((item) => item.id === note.id ? updated : item)); refreshInbox(); } catch { setError("Note could not be updated."); }
                  }}>Edit</Button>
                </div> : null}
                <div className="mt-3 flex flex-wrap gap-2">
                  <Button type="button" variant="outline" onClick={() => removeNote(note, false)}>Delete for myself</Button>
                  {(role === "admin" || note.createdBy === profile?.id) && <Button type="button" variant="outline" onClick={() => removeNote(note, true)}>Delete for everyone</Button>}
                </div>
              </div>
            </div>
          </article>
        ))}
      </section>
    </div>
  );
}
