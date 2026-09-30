import { cleanup, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { useRecordList } from "@/components/record-list-controls";
import ReportsPage from "@/app/(protected)/reports/page";

const reports = vi.hoisted(() => ({ list: vi.fn(), role: "admin" }));
vi.mock("@/lib/api/reports", () => ({ listReports: reports.list }));
vi.mock("@/lib/auth", () => ({ getSession: () => ({ profile: { role: reports.role } }) }));
vi.mock("@/components/reports/cyber-risk-report-preview", () => ({ CyberRiskReportPreview: ({ htmlPreview }: { htmlPreview: string }) => <p>{htmlPreview}</p> }));
afterEach(() => { cleanup(); reports.role = "admin"; });

function Records() {
  const list = useRecordList([
    { name: "Alpha", createdAt: "2026-01-01" },
    { name: "Zulu", createdAt: "2026-02-01" },
  ], (item) => item.name, "companies");
  return <>{list.controls}<ul>{list.visible.map((item) => <li key={item.name}>{item.name}</li>)}</ul></>;
}
describe("Review usability", () => {
  it("defaults to newest records and supports chronological and alphabetic ordering", async () => {
    const user = userEvent.setup(); render(<Records />);
    expect(screen.getAllByRole("listitem").map((item) => item.textContent)).toEqual(["Zulu", "Alpha"]);
    await user.selectOptions(screen.getByLabelText("Sort companies"), "oldest");
    expect(screen.getAllByRole("listitem")[0]).toHaveTextContent("Alpha");
    await user.selectOptions(screen.getByLabelText("Sort companies"), "za");
    expect(screen.getAllByRole("listitem")[0]).toHaveTextContent("Zulu");
    await user.selectOptions(screen.getByLabelText("Sort companies"), "az");
    expect(screen.getAllByRole("listitem")[0]).toHaveTextContent("Alpha");
  });
  it("identifies the selected preview, collapses the list and shows valid workflow actions", async () => {
    HTMLElement.prototype.scrollIntoView = vi.fn();
    reports.list.mockResolvedValue({ items: [
      { id: "old", title: "Alpha", companyName: "Demo", domain: "demo.example", createdAt: "2026-01-01", status: "draft", htmlPreview: "Alpha report contents" },
      { id: "new", title: "Zulu", companyName: "Demo", domain: "demo.example", createdAt: "2026-02-01", status: "approved", htmlPreview: "Zulu report contents" },
    ] });
    const user = userEvent.setup(); render(<ReportsPage />);
    await screen.findByText("Zulu");
    const cards = screen.getAllByRole("article");
    expect(within(cards[0]).getByRole("heading")).toHaveTextContent("Zulu");
    expect(within(cards[0]).queryByRole("button", { name: "Submit for review" })).not.toBeInTheDocument();
    expect(within(cards[0]).getByRole("button", { name: "Archive" })).toBeEnabled();
    await user.click(within(cards[0]).getByRole("button", { name: "Preview" }));
    expect(screen.getByRole("heading", { name: "Report preview: Zulu" })).toBeVisible();
    expect(screen.getByText("Zulu report contents")).toBeVisible();
    await user.click(screen.getByRole("button", { name: "Hide reports" }));
    expect(screen.queryByRole("region", { name: "Report list" })).not.toBeInTheDocument();
    expect(screen.getByText("Zulu report contents")).toBeVisible();
    await user.click(screen.getByRole("button", { name: "Show reports" }));
    await user.selectOptions(screen.getByLabelText("Sort reports"), "az");
    expect(within(screen.getAllByRole("article")[0]).getByRole("heading")).toHaveTextContent("Alpha");
  });
});


it.each(["admin", "management", "technical_analyst", "business_development", "read_only"])("matches report guidance and actions to %s", async (role) => {
  reports.role = role;
  reports.list.mockResolvedValue({ items: ["draft", "review", "approved", "shared", "archived"].map((status) => ({ id: status, status, title: `${status} report`, companyName: "Demo", domain: "demo.example", createdAt: "2026-09-29", htmlPreview: "Findings" })) });
  render(<ReportsPage />);
  await screen.findByText("draft report");
  const prepare = ["admin", "management", "technical_analyst"].includes(role);
  const approve = ["admin", "management"].includes(role);
  expect(Boolean(screen.queryByRole("button", { name: "Submit for review" }))).toBe(prepare);
  expect(Boolean(screen.queryByRole("button", { name: "Approve" }))).toBe(approve);
  expect(screen.queryAllByRole("button", { name: "Download" }).length > 0).toBe(approve);
  expect(Boolean(screen.queryByText("Draft: check the preview, then submit it for review."))).toBe(prepare);
  if (!prepare) expect(screen.getByText("Draft: you can preview the findings. The report is not yet reviewed or approved.")).toBeVisible();
});


import CompanyCard from "@/components/companies/company-card";
import ContactCard from "@/components/contacts/contact-card";
it("shows company and contact creation date and time without author metadata", () => {
  const createdAt = "2026-09-29T12:34:56Z";
  render(<><CompanyCard name="Demo" domain="demo.example" industry="Technology" country="Germany" createdAt={createdAt} /><ContactCard firstName="Demo" lastName="Contact" email="demo@example.test" role="champion" createdAt={createdAt} /></>);
  expect(screen.getAllByText(new Date(createdAt).toLocaleString())).toHaveLength(2);
  expect(document.querySelectorAll(`time[datetime="${createdAt}"]`)).toHaveLength(2);
  expect(screen.queryByText(/Written by/)).not.toBeInTheDocument();
});


it("sorts reports by actual creation instant and opens the requested draft", async () => {
  window.history.replaceState({}, "", "/reports?report_id=newest");
  HTMLElement.prototype.scrollIntoView = vi.fn();
  reports.list.mockResolvedValue({ items: [
    { id: "older", title: "Older offset", companyName: "Demo", domain: "demo.example", createdAt: "2026-09-29T22:00:00+02:00", status: "draft", htmlPreview: "Older contents" },
    { id: "newest", title: "New draft", companyName: "Demo", domain: "demo.example", createdAt: "2026-09-29T20:04:43Z", status: "draft", htmlPreview: "New contents" },
  ] });
  render(<ReportsPage />);
  await screen.findByRole("heading", { name: "Report preview: New draft" });
  expect(within(screen.getAllByRole("article")[0]).getByRole("heading")).toHaveTextContent("New draft");
  expect(screen.getByText("New contents")).toBeVisible();
  window.history.replaceState({}, "", "/");
});
