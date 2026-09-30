import { cleanup, render, screen, waitFor } from "@testing-library/react";
import React from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  getSession: vi.fn(),
  getNotes: vi.fn().mockResolvedValue([]),
  getUsers: vi.fn().mockResolvedValue([]),
}));

vi.mock("next/navigation", () => ({ useRouter: () => ({ replace: vi.fn() }) }));
vi.mock("@/lib/auth", async () => {
  const actual = await vi.importActual<typeof import("@/lib/auth")>("@/lib/auth");
  return { ...actual, getSession: mocks.getSession };
});
vi.mock("@/lib/api/notes", () => ({
  getNotes: mocks.getNotes,
  createNote: vi.fn(),
  updateNote: vi.fn(),
  deleteNote: vi.fn(),
  deleteNoteForMe: vi.fn(),
}));
vi.mock("@/lib/api/users", () => ({
  getUsers: mocks.getUsers,
  getCurrentUser: vi.fn(),
}));

import LoginPage from "@/app/login/page";
import StaffNotesPage from "@/app/(protected)/notes/page";

vi.mock("@/lib/api/inbox", () => ({ emptyInbox: { unread_task_ids: [], unread_note_ids: [], overdue_tasks: 0, due_soon_tasks: 0 }, getInbox: vi.fn().mockResolvedValue({ unread_task_ids: [], unread_note_ids: [], overdue_tasks: 0, due_soon_tasks: 0 }), markRead: vi.fn(), refreshInbox: vi.fn() }));

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("role-aware forms", () => {
  it.each(["read_only"])(
    "hides note write controls for %s",
    async (role) => {
      mocks.getSession.mockReturnValue({ profile: { role } });
      render(<StaffNotesPage />);

      await waitFor(() => expect(mocks.getNotes).toHaveBeenCalled());
      expect(screen.queryByLabelText("New note")).not.toBeInTheDocument();
      expect(screen.queryByRole("button", { name: "Save note" })).not.toBeInTheDocument();
      expect(screen.getByText("Your role has read-only access to staff notes.")).toBeVisible();
    },
  );

  it("lets Technical Analysts write team notes", async () => {
    mocks.getSession.mockReturnValue({ profile: { role: "technical_analyst" } });
    render(<StaffNotesPage />);
    expect(screen.getByLabelText("New note")).toBeVisible();
  });

  it("does not prefill login credentials", () => {
    render(<LoginPage />);

    expect(screen.getByLabelText("Email")).toHaveValue("");
    expect(screen.getByLabelText("Password")).toHaveValue("");
  });
});


it.each([
  ["admin", "other", true],
  ["management", "other", false],
  ["business_development", "other", false],
  ["technical_analyst", "other", false],
  ["read_only", "other", false],
  ["management", "me", true],
  ["business_development", "me", true],
])("shows scoped delete actions for %s with author %s", async (role, author, canDeleteEveryone) => {
  mocks.getSession.mockReturnValue({ profile: { id: "me", role } });
  mocks.getNotes.mockResolvedValueOnce([{ id: "note", body: "Shared synthetic note", createdAt: "2026-09-29T10:00:00Z", createdBy: author }]);
  render(<StaffNotesPage />);
  expect(await screen.findByRole("button", { name: "Delete for myself" })).toBeVisible();
  expect(Boolean(screen.queryByRole("button", { name: "Delete for everyone" }))).toBe(canDeleteEveryone);
  expect(screen.queryByRole("button", { name: "Archive" })).not.toBeInTheDocument();
});
