import { apiRequest } from "@/lib/api/client";
import type { Opportunity, OpportunityFormValues } from "@/types/opportunity";

type OpportunityApiResponse = {
  id: string;
  company_id: string;
  contact_id: string | null;
  stage_id: string;
  name: string;
  service: string | null;
  value_usd: number | string | null;
  probability: number | null;
  weighted_value_usd: number | string | null;
  expected_close_date: string | null;
  owner_id: string | null;
  need: string | null;
  blockers: string | null;
  competitor: string | null;
  next_action: string | null;
  next_action_due_at: string | null;
  lost_reason: string | null;
  created_at: string;
  updated_at: string;
};

type OpportunityListApiResponse = {
  items: OpportunityApiResponse[];
  total: number;
};

function toNumber(value: number | string | null | undefined) {
  if (value === null || value === undefined || value === "") {
    return 0;
  }

  return Number(value);
}

export function mapOpportunity(opportunity: OpportunityApiResponse): Opportunity {
  return {
    id: opportunity.id,
    companyId: opportunity.company_id,
    contactId: opportunity.contact_id ?? "",
    stageId: opportunity.stage_id,
    name: opportunity.name,
    service: opportunity.service ?? "",
    valueUsd: toNumber(opportunity.value_usd),
    probability: opportunity.probability ?? 0,
    weightedValueUsd: toNumber(opportunity.weighted_value_usd),
    expectedCloseDate: opportunity.expected_close_date ?? "",
    ownerId: opportunity.owner_id ?? "",
    need: opportunity.need ?? "",
    blockers: opportunity.blockers ?? "",
    competitor: opportunity.competitor ?? "",
    nextAction: opportunity.next_action ?? "",
    nextActionDueAt: opportunity.next_action_due_at ?? "",
    lostReason: opportunity.lost_reason ?? "",
    createdAt: opportunity.created_at,
    updatedAt: opportunity.updated_at,
  };
}

function cleanOptional(value: string) {
  const trimmed = value.trim();
  return trimmed ? trimmed : null;
}

function buildPayload(values: OpportunityFormValues) {
  return {
    company_id: values.companyId,
    contact_id: cleanOptional(values.contactId),
    stage_id: values.stageId,
    name: values.name.trim(),
    service: cleanOptional(values.service),
    value_usd: values.valueUsd === "" ? null : Number(values.valueUsd),
    probability: values.probability === "" ? null : Number(values.probability),
    expected_close_date: cleanOptional(values.expectedCloseDate),
    owner_id: cleanOptional(values.ownerId),
    need: cleanOptional(values.need),
    blockers: cleanOptional(values.blockers),
    competitor: cleanOptional(values.competitor),
    next_action: cleanOptional(values.nextAction),
    next_action_due_at: cleanOptional(values.nextActionDueAt),
    lost_reason: cleanOptional(values.lostReason),
  };
}

export async function getOpportunities(): Promise<Opportunity[]> {
  const response = await apiRequest<OpportunityListApiResponse>("/opportunities");
  return response.items.map(mapOpportunity);
}

export async function createOpportunity(values: OpportunityFormValues): Promise<Opportunity> {
  const response = await apiRequest<OpportunityApiResponse>("/opportunities", {
    method: "POST",
    body: JSON.stringify(buildPayload(values)),
  });

  return mapOpportunity(response);
}

export async function updateOpportunity(
  opportunityId: string,
  values: OpportunityFormValues
): Promise<Opportunity> {
  const response = await apiRequest<OpportunityApiResponse>(`/opportunities/${opportunityId}`, {
    method: "PATCH",
    body: JSON.stringify(buildPayload(values)),
  });

  return mapOpportunity(response);
}

export async function deleteOpportunity(opportunityId: string): Promise<void> {
  await apiRequest(`/opportunities/${opportunityId}`, {
    method: "DELETE",
  });
}
