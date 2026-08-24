"use client";

import { Plus, StickyNote } from "lucide-react";
import { FormEvent, useCallback, useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { ErrorState, LoadingState } from "@/components/ui/async-state";
import { archiveNote, createNote, getNotes, updateNote, type Note } from "@/lib/api/notes";

export default function StaffNotesPage() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [body, setBody] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadNotes = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      setNotes(await getNotes());
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
      setBody("");
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Failed to save note.");
    }
  }

  return (
    <div className="space-y-5">
      <div>
        <p className="text-sm font-medium text-primary">Team workspace</p>
        <h1 className="mt-1 text-2xl font-semibold sm:text-3xl">Staff Notes</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Shared reminders and context for staff. For a dated follow-up, create a Task inside an opportunity.
        </p>
      </div>

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

      {loading ? <LoadingState title="Loading staff notes..." /> : null}
      {error ? <ErrorState title="Notes could not be loaded" description={error} onRetry={loadNotes} /> : null}

      <section className="space-y-3" aria-label="Saved staff notes">
        {!loading && notes.length === 0 ? (
          <p className="rounded-md border bg-card p-5 text-sm text-muted-foreground">No notes yet.</p>
        ) : null}
        {notes.map((note) => (
          <article key={note.id} className="rounded-md border bg-card p-4 shadow-sm">
            <div className="flex gap-3">
              <StickyNote className="mt-0.5 h-5 w-5 shrink-0 text-primary" />
              <div className="min-w-0 flex-1">
                <p className="whitespace-pre-wrap text-sm">{note.body}</p>
                <p className="mt-2 text-xs text-muted-foreground">{new Date(note.createdAt).toLocaleString()}</p>
                <div className="mt-3 flex gap-2">
                  <Button type="button" variant="outline" onClick={async () => {
                    const nextBody = window.prompt("Edit note", note.body);
                    if (!nextBody?.trim()) return;
                    const updated = await updateNote(note.id, nextBody.trim());
                    setNotes((items) => items.map((item) => item.id === note.id ? updated : item));
                  }}>Edit</Button>
                  <Button type="button" variant="outline" onClick={async () => {
                    if (!window.confirm("Archive this note?")) return;
                    await archiveNote(note.id);
                    setNotes((items) => items.filter((item) => item.id !== note.id));
                  }}>Archive</Button>
                </div>
              </div>
            </div>
          </article>
        ))}
      </section>
    </div>
  );
}
