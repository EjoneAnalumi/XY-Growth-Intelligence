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
  archiveNote: vi.fn(),
}));
vi.mock("@/lib/api/users", () => ({
  getUsers: mocks.getUsers,
  getCurrentUser: vi.fn(),
}));

import LoginPage from "@/app/login/page";
import StaffNotesPage from "@/app/(protected)/notes/page";

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("role-aware forms", () => {
  it.each(["technical_analyst", "read_only"])(
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

  it("does not prefill login credentials", () => {
    render(<LoginPage />);

    expect(screen.getByLabelText("Email")).toHaveValue("");
    expect(screen.getByLabelText("Password")).toHaveValue("");
  });
});
