import { apiRequest } from "@/lib/api/client";
import type {
  Opportunity,
  OpportunityFormValues,
  OpportunityStageHistory,
  PipelineStage,
} from "@/types/opportunity";

type PipelineStageApiResponse = {
  id: string;
  name: string;
  sort_order: number;
  default_probability: number;
  is_won: boolean;
  is_lost: boolean;
};

type PipelineStageListApiResponse = {
  items: PipelineStageApiResponse[];
  total: number;
};

type OpportunityApiResponse = {
  id: string;
  company_id: string;
  contact_id: string | null;
  stage_id: string;
  name: string;
  service: string | null;
  value_usd: number | null;
  probability: number | null;
  weighted_value_usd: number | null;
  expected_close_date: string | null;
  owner_id: string | null;
  need: string | null;
  blockers: string | null;
  competitor: string | null;
  next_action: string | null;
  next_action_due_at: string | null;
  lost_reason: string | null;
  current_stage_entered_at: string | null;
  days_in_current_stage: number;
  archived_at: string | null;
  created_at: string;
  updated_at: string;
  created_by: string | null;
  updated_by: string | null;
};

type OpportunityListApiResponse = {
  items: OpportunityApiResponse[];
  total: number;
};

type StageHistoryApiResponse = {
  id: string;
  opportunity_id: string;
  from_stage_id: string | null;
  to_stage_id: string;
  changed_by: string | null;
  note: string | null;
  changed_at: string;
};

type OpportunityStageMoveApiResponse = {
  message: string;
  opportunity: OpportunityApiResponse;
  history: StageHistoryApiResponse;
};

function mapPipelineStage(stage: PipelineStageApiResponse): PipelineStage {
  return {
    id: stage.id,
    name: stage.name,
    sortOrder: stage.sort_order,
    defaultProbability: stage.default_probability,
    isWon: stage.is_won,
    isLost: stage.is_lost,
  };
}

function mapOpportunity(opportunity: OpportunityApiResponse): Opportunity {
  return {
    id: opportunity.id,
    companyId: opportunity.company_id,
    contactId: opportunity.contact_id,
    stageId: opportunity.stage_id,
    name: opportunity.name,
    service: opportunity.service ?? "",
    valueUsd: opportunity.value_usd ?? 0,
    probability: opportunity.probability ?? 0,
    weightedValueUsd: opportunity.weighted_value_usd ?? 0,
    expectedCloseDate: opportunity.expected_close_date ?? "",
    ownerId: opportunity.owner_id,
    need: opportunity.need ?? "",
    blockers: opportunity.blockers ?? "",
    competitor: opportunity.competitor ?? "",
    nextAction: opportunity.next_action ?? "",
    nextActionDueAt: opportunity.next_action_due_at ?? "",
    lostReason: opportunity.lost_reason ?? "",
    currentStageEnteredAt: opportunity.current_stage_entered_at,
    daysInCurrentStage: opportunity.days_in_current_stage,
    archivedAt: opportunity.archived_at,
    createdAt: opportunity.created_at,
    updatedAt: opportunity.updated_at,
    createdBy: opportunity.created_by,
    updatedBy: opportunity.updated_by,
  };
}

function mapStageHistory(history: StageHistoryApiResponse): OpportunityStageHistory {
  return {
    id: history.id,
    opportunityId: history.opportunity_id,
    fromStageId: history.from_stage_id,
    toStageId: history.to_stage_id,
    changedBy: history.changed_by,
    note: history.note,
    changedAt: history.changed_at,
  };
}

function buildOpportunityPayload(values: OpportunityFormValues) {
  return {
    company_id: values.companyId,
    contact_id: values.contactId || null,
    stage_id: values.stageId,
    name: values.name,
    service: values.service || null,
    value_usd: Number(values.valueUsd || 0),
    probability: Number(values.probability || 0),
    expected_close_date: values.expectedCloseDate || null,
    need: values.need || null,
    blockers: values.blockers || null,
    competitor: values.competitor || null,
    next_action: values.nextAction || null,
    next_action_due_at: values.nextActionDueAt || null,
    lost_reason: values.lostReason || null,
  };
}

export function opportunityToFormValues(opportunity: Opportunity): OpportunityFormValues {
  return {
    companyId: opportunity.companyId,
    contactId: opportunity.contactId ?? "",
    stageId: opportunity.stageId,
    name: opportunity.name,
    service: opportunity.service,
    valueUsd: String(opportunity.valueUsd),
    probability: String(opportunity.probability),
    expectedCloseDate: opportunity.expectedCloseDate,
    need: opportunity.need,
    blockers: opportunity.blockers,
    competitor: opportunity.competitor,
    nextAction: opportunity.nextAction,
    nextActionDueAt: opportunity.nextActionDueAt ? opportunity.nextActionDueAt.slice(0, 16) : "",
    lostReason: opportunity.lostReason,
  };
}

export async function getPipelineStages(): Promise<PipelineStage[]> {
  const response = await apiRequest<PipelineStageListApiResponse>("/pipeline-stages");
  return response.items.map(mapPipelineStage);
}

export async function getOpportunities(): Promise<Opportunity[]> {
  const response = await apiRequest<OpportunityListApiResponse>("/opportunities");
  return response.items.map(mapOpportunity);
}

export async function getOpportunity(opportunityId: string): Promise<Opportunity> {
  const response = await apiRequest<OpportunityApiResponse>(`/opportunities/${opportunityId}`);
  return mapOpportunity(response);
}

export async function createOpportunity(values: OpportunityFormValues): Promise<Opportunity> {
  const response = await apiRequest<OpportunityApiResponse>("/opportunities", {
    method: "POST",
    body: JSON.stringify(buildOpportunityPayload(values)),
  });

  return mapOpportunity(response);
}

export async function updateOpportunity(
  opportunityId: string,
  values: OpportunityFormValues,
): Promise<Opportunity> {
  const response = await apiRequest<OpportunityApiResponse>(`/opportunities/${opportunityId}`, {
    method: "PATCH",
    body: JSON.stringify(buildOpportunityPayload(values)),
  });

  return mapOpportunity(response);
}

export async function archiveOpportunity(opportunityId: string): Promise<void> {
  await apiRequest(`/opportunities/${opportunityId}`, { method: "DELETE" });
}

export async function getOpportunityStageHistory(
  opportunityId: string,
): Promise<OpportunityStageHistory[]> {
  const response = await apiRequest<StageHistoryApiResponse[]>(
    `/opportunities/${opportunityId}/stage-history`,
  );
  return response.map(mapStageHistory);
}

export async function moveOpportunityStage(
  opportunityId: string,
  toStageId: string,
  note: string,
): Promise<{
  opportunity: Opportunity;
  history: OpportunityStageHistory;
}> {
  const response = await apiRequest<OpportunityStageMoveApiResponse>(
    `/opportunities/${opportunityId}/move-stage`,
    {
      method: "PATCH",
      body: JSON.stringify({
        to_stage_id: toStageId,
        note: note || null,
      }),
    },
  );

  return {
    opportunity: mapOpportunity(response.opportunity),
    history: mapStageHistory(response.history),
  };
}
