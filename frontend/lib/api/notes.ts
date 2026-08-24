import { apiRequest } from "@/lib/api/client";

export type Note = {
  id: string;
  companyId: string | null;
  contactId: string | null;
  opportunityId: string | null;
  body: string;
  createdAt: string;
  createdBy: string | null;
  updatedBy: string | null;
};

type NoteResponse = {
  id: string;
  company_id: string | null;
  contact_id: string | null;
  opportunity_id: string | null;
  body: string;
  created_at: string;
  created_by: string | null;
  updated_by: string | null;
};

const mapNote = (note: NoteResponse): Note => ({
  id: note.id,
  companyId: note.company_id,
  contactId: note.contact_id,
  opportunityId: note.opportunity_id,
  body: note.body,
  createdAt: note.created_at,
  createdBy: note.created_by,
  updatedBy: note.updated_by,
});

export async function getNotes(): Promise<Note[]> {
  const response = await apiRequest<{ items: NoteResponse[] }>("/notes");
  return response.items.map(mapNote);
}

export async function createNote(values: Omit<Note, "id" | "createdAt" | "createdBy" | "updatedBy">): Promise<Note> {
  const response = await apiRequest<NoteResponse>("/notes", {
    method: "POST",
    body: JSON.stringify({
      company_id: values.companyId,
      contact_id: values.contactId,
      opportunity_id: values.opportunityId,
      body: values.body,
    }),
  });
  return mapNote(response);
}

export async function updateNote(id: string, body: string): Promise<Note> {
  return mapNote(await apiRequest<NoteResponse>(`/notes/${id}`, {
    method: "PATCH",
    body: JSON.stringify({ body }),
  }));
}

export async function archiveNote(id: string): Promise<void> {
  await apiRequest(`/notes/${id}`, { method: "DELETE" });
}
