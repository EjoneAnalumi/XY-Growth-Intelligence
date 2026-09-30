import { cleanup, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import TasksPage from "@/app/(protected)/tasks/page";
import AdministrationPage from "@/app/(protected)/administration/page";
import { allPages } from "@/lib/api/pagination";

const mocks = vi.hoisted(() => ({ tasks: vi.fn(), users: vi.fn(), complete: vi.fn(), create: vi.fn(), session: vi.fn(), request: vi.fn() }));
vi.mock("@/lib/api/tasks", () => ({ getTasks: mocks.tasks, completeTask: mocks.complete, createTask: mocks.create }));
vi.mock("@/lib/api/users", () => ({ getUsers: mocks.users }));
vi.mock("@/lib/auth", () => ({ getSession: mocks.session }));
vi.mock("@/lib/api/client", () => ({ apiRequest: mocks.request }));
vi.mock("@/lib/api/inbox", () => ({ emptyInbox: { unread_task_ids: [], unread_note_ids: [], overdue_tasks: 0, due_soon_tasks: 0 }, getInbox: vi.fn().mockResolvedValue({ unread_task_ids: [], unread_note_ids: [], overdue_tasks: 0, due_soon_tasks: 0 }), markRead: vi.fn(), refreshInbox: vi.fn() }));
afterEach(cleanup);
beforeEach(() => {
  vi.clearAllMocks();
  mocks.session.mockReturnValue({ profile: { id: "owner", role: "business_development" } });
  mocks.users.mockResolvedValue([{ id: "owner", full_name: "Synthetic Owner", active: true }]);
  mocks.tasks.mockResolvedValue([{ id: "task", title: "Synthetic overdue follow-up", ownerId: "owner", status: "open", dueAt: "2020-01-01T10:00:00Z", priority: "high", description: "" }]);
});

describe("MVP completion", () => {
  it("filters overdue tasks and saves a completion outcome", async () => {
    const user = userEvent.setup();
    mocks.complete.mockResolvedValue({ id: "task", title: "Synthetic overdue follow-up", ownerId: "owner", status: "completed", completedAt: "2026-09-28T10:00:00Z", outcome: "Mock scope confirmed" });
    render(<TasksPage />);
    await screen.findByText("Synthetic overdue follow-up");
    await user.selectOptions(screen.getByLabelText("Due/status filter"), "overdue");
    await user.type(screen.getByLabelText("Outcome"), "Mock scope confirmed");
    await user.click(screen.getByRole("button", { name: "Complete" }));
    await waitFor(() => expect(mocks.complete).toHaveBeenCalledWith("task", "Mock scope confirmed"));
    expect(screen.queryByText("Synthetic overdue follow-up")).not.toBeInTheDocument();
    await user.selectOptions(screen.getByLabelText("Due/status filter"), "completed");
    expect(await screen.findByText(/Mock scope confirmed/)).toBeVisible();
  });
  it("hides task writes and administration from Read Only", async () => {
    mocks.session.mockReturnValue({ profile: { id: "owner", role: "read_only" } });
    render(<TasksPage />);
    await screen.findByText("Synthetic overdue follow-up");
    expect(screen.queryByRole("button", { name: "Create task" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Complete" })).not.toBeInTheDocument();
    cleanup(); render(<AdministrationPage />);
    expect(screen.getByRole("alert")).toHaveTextContent("Only administrators");
  });
  it("loads subsequent API pages so records after the first page are discoverable", async () => {
    mocks.request.mockResolvedValueOnce({ items: [{ id: "a" }], total: 2 })
      .mockResolvedValueOnce({ items: [{ id: "b" }], total: 2 });
    expect(await allPages("/companies")).toEqual([{ id: "a" }, { id: "b" }]);
    expect(mocks.request).toHaveBeenLastCalledWith("/companies?limit=100&offset=1");
  });
});


it("shows mine before unassigned, defaults newest, and allows earliest due and all-owner views", async () => {
  const user = userEvent.setup();
  const base = { status: "open", priority: "medium", description: "", createdAt: "2026-01-01", dueAt: "2026-05-01" };
  mocks.tasks.mockResolvedValue([
    { ...base, id: "1", title: "Mine old urgent", ownerId: "owner", dueAt: "2026-01-01" },
    { ...base, id: "2", title: "Mine new", ownerId: "owner", createdAt: "2026-02-01" },
    { ...base, id: "3", title: "Unassigned newest", ownerId: null, createdAt: "2026-03-01" },
    { ...base, id: "4", title: "Someone else", ownerId: "someone" },
  ]);
  mocks.users.mockResolvedValue([{ id: "owner", full_name: "Owner", role: "admin", active: true }, { id: "readonly", full_name: "Read Only", role: "read_only", active: true }]);
  render(<TasksPage />);
  await screen.findByText("Mine new");
  const titles = () => screen.getAllByRole("article").map((article) => within(article).getByRole("heading").textContent);
  expect(titles()).toEqual(["Mine new ", "Mine old urgent ", "Unassigned newest "]);
  expect(within(screen.getByLabelText("Owner", { exact: true })).queryByRole("option", { name: "Read Only" })).not.toBeInTheDocument();
  await user.selectOptions(screen.getByLabelText("Sort tasks"), "due");
  expect(titles()[0]).toBe("Mine old urgent ");
  await user.selectOptions(screen.getByLabelText("Filter owner"), "all");
  expect(await screen.findByText("Someone else")).toBeVisible();
});
