import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import React from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

const hooks = vi.hoisted(() => ({
  useCompanies: vi.fn(),
  useContacts: vi.fn(),
  useDashboardSummary: vi.fn(),
  useOpportunities: vi.fn(),
  usePipelineStages: vi.fn(),
}));

vi.mock("@/hooks/use-companies", () => ({ useCompanies: hooks.useCompanies }));
vi.mock("@/hooks/use-contacts", () => ({ useContacts: hooks.useContacts }));
vi.mock("@/hooks/use-dashboard-summary", () => ({
  useDashboardSummary: hooks.useDashboardSummary,
}));
vi.mock("@/hooks/use-opportunities", () => ({ useOpportunities: hooks.useOpportunities }));
vi.mock("@/hooks/use-pipeline-stages", () => ({
  usePipelineStages: hooks.usePipelineStages,
}));
vi.mock("@/components/companies/company-form", () => ({ default: () => null }));
vi.mock("@/components/companies/company-card", () => ({ default: () => null }));
vi.mock("@/components/companies/icp-score-panel", () => ({ default: () => null }));
vi.mock("@/components/contacts/contact-form", () => ({ default: () => null }));
vi.mock("@/components/contacts/contact-card", () => ({ default: () => null }));
vi.mock("@/components/opportunities/opportunity-form", () => ({ default: () => null }));
vi.mock("@/components/opportunities/opportunity-kanban", () => ({ default: () => null }));
vi.mock("@/components/opportunities/opportunity-table", () => ({ default: () => null }));
vi.mock("@/lib/api/companies", () => ({ createCompany: vi.fn() }));
vi.mock("@/lib/api/contacts", () => ({ createContact: vi.fn() }));
vi.mock("@/lib/api/opportunities", () => ({
  createOpportunity: vi.fn(),
  moveOpportunityStage: vi.fn(),
}));

import CompaniesPage from "@/app/(protected)/companies/page";
import ContactsPage from "@/app/(protected)/contacts/page";
import DashboardPage from "@/app/(protected)/dashboard/page";
import OpportunitiesPage from "@/app/(protected)/opportunities/page";

const company = {
  id: "company-1",
  name: "Northstar Robotics",
  domain: "northstar.example",
  industry: "Technology",
  country: "Albania",
};

const stage = {
  id: "stage-1",
  name: "Qualified",
  sortOrder: 1,
  defaultProbability: 60,
  isWon: false,
  isLost: false,
};

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("core page async states", () => {
  it("shows Companies loading state with a screen-reader status", () => {
    hooks.useCompanies.mockReturnValue({
      companies: [],
      loading: true,
      error: null,
      setCompanies: vi.fn(),
      refreshCompanies: vi.fn(),
    });

    render(<CompaniesPage />);

    expect(screen.getByRole("status")).toHaveTextContent("Loading companies...");
  });

  it("shows an actionable empty state on Contacts", () => {
    hooks.useContacts.mockReturnValue({
      contacts: [],
      loading: false,
      error: null,
      setContacts: vi.fn(),
      refreshContacts: vi.fn(),
    });
    hooks.useCompanies.mockReturnValue({ companies: [company] });

    render(<ContactsPage />);

    expect(screen.getByRole("heading", { name: "No contacts yet" })).toBeVisible();
    expect(screen.getByRole("button", { name: "Add Contact" })).toBeEnabled();
  });

  it("retries the Opportunities request from its accessible error state", () => {
    const refreshOpportunities = vi.fn();
    hooks.useCompanies.mockReturnValue({
      companies: [company],
      loading: false,
      error: null,
      refreshCompanies: vi.fn(),
    });
    hooks.useContacts.mockReturnValue({ contacts: [] });
    hooks.usePipelineStages.mockReturnValue({
      stages: [stage],
      loading: false,
      error: null,
      refreshStages: vi.fn(),
    });
    hooks.useOpportunities.mockReturnValue({
      opportunities: [],
      loading: false,
      error: "The pipeline service is unavailable.",
      setOpportunities: vi.fn(),
      refreshOpportunities,
    });

    render(<OpportunitiesPage />);

    expect(screen.getByRole("alert")).toHaveTextContent("The pipeline service is unavailable.");
    fireEvent.click(screen.getByRole("button", { name: "Try again" }));
    expect(refreshOpportunities).toHaveBeenCalledOnce();
  });

  it("retries the Dashboard request from its accessible error state", () => {
    const refreshSummary = vi.fn();
    hooks.useDashboardSummary.mockReturnValue({
      summary: null,
      loading: false,
      error: "Dashboard metrics are unavailable.",
      refreshSummary,
    });

    render(<DashboardPage />);

    expect(screen.getByRole("alert")).toHaveTextContent("Dashboard metrics are unavailable.");
    fireEvent.click(screen.getAllByRole("button", { name: "Try again" })[0]);
    expect(refreshSummary).toHaveBeenCalledOnce();
  });
});
