import { apiRequest } from "@/lib/api/client";

export type Inbox = { unread_task_ids: string[]; unread_note_ids: string[]; overdue_tasks: number; due_soon_tasks: number };
export const emptyInbox: Inbox = { unread_task_ids: [], unread_note_ids: [], overdue_tasks: 0, due_soon_tasks: 0 };
export const getInbox = () => apiRequest<Inbox>("/inbox");
export function refreshInbox() { window.dispatchEvent(new Event("inbox-changed")); }
export async function markRead(kind: "tasks" | "notes", id: string) {
  await apiRequest(`/inbox/${kind}/${id}/read`, { method: "POST" });
  refreshInbox();
}
