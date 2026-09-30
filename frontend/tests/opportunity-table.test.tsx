import { render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it } from "vitest";

import OpportunityTable from "@/components/opportunities/opportunity-table";
import type { Company } from "@/types/company";
import type { Opportunity, PipelineStage } from "@/types/opportunity";

const companies: Company[] = [
  {
    id: "company-1",
    name: "Northstar Robotics",
    domain: "northstar.example",
    industry: "Technology",
    country: "Albania",
  },
];

const stages: PipelineStage[] = [
  {
    id: "stage-1",
    name: "Qualified",
    sortOrder: 1,
    defaultProbability: 60,
    isWon: false,
    isLost: false,
  },
];

const opportunities: Opportunity[] = [
  {
    id: "opportunity-1",
    companyId: "company-1",
    contactId: null,
    stageId: "stage-1",
    name: "Security assessment",
    service: "Security assessment",
    valueEur: 24000,
    probability: 60,
    weightedValueEur: 14400,
    nextAction: "Schedule discovery workshop",
    nextActionDueAt: "2026-08-20",
    expectedCloseDate: "2026-09-20",
    ownerId: null,
    need: "Improve security posture",
    blockers: "",
    competitor: "",
    lostReason: "",
    currentStageEnteredAt: "2026-08-19T00:00:00Z",
    daysInCurrentStage: 0,
    archivedAt: null,
    createdAt: "2026-08-19T00:00:00Z",
    updatedAt: "2026-08-19T00:00:00Z",
    createdBy: null,
    updatedBy: null,
  },
];

describe("OpportunityTable", () => {
  it("provides an accessible table name and opportunity detail link", () => {
    render(<OpportunityTable opportunities={opportunities} companies={companies} stages={stages} />);

    expect(screen.getByRole("table", { name: "Opportunities pipeline table" })).toBeVisible();
    expect(screen.getByRole("link", { name: "Details" })).toHaveAttribute(
      "href",
      "/opportunities/opportunity-1",
    );
  });
});
