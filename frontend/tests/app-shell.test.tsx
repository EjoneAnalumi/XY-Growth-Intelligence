import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import React from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  usePathname: () => "/dashboard",
  useRouter: () => ({ replace: vi.fn() }),
}));
vi.mock("@/lib/auth", () => ({
  getMockSession: () => ({ role: "admin" }),
  signOutMock: vi.fn(),
}));

import { AppShell } from "@/components/app-shell";

afterEach(() => {
  cleanup();
});

describe("AppShell navigation", () => {
  it("provides a keyboard-operable skip link and mobile navigation control", async () => {
    const user = userEvent.setup();
    render(
      <AppShell>
        <h1>Dashboard</h1>
      </AppShell>,
    );

    await user.tab();
    expect(screen.getByRole("link", { name: "Skip to main content" })).toHaveFocus();

    const menuButton = screen.getByRole("button", { name: "Toggle navigation" });
    expect(menuButton).toHaveAttribute("aria-expanded", "false");
    menuButton.focus();
    await user.keyboard("{Enter}");
    expect(menuButton).toHaveAttribute("aria-expanded", "true");
    expect(screen.getByRole("navigation", { name: "Main navigation" })).toBeVisible();
    expect(screen.getByRole("link", { name: "Dashboard" })).toHaveAttribute("aria-current", "page");
  });
});
