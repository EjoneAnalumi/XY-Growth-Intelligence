export type PipelineStage = {
  id: string;
  name: string;
  sortOrder: number;
  defaultProbability: number;
  isWon: boolean;
  isLost: boolean;
};

export type Opportunity = {
  id: string;
  companyId: string;
  contactId: string | null;
  stageId: string;
  name: string;
  service: string;
  valueEur: number;
  probability: number;
  weightedValueEur: number;
  expectedCloseDate: string;
  ownerId: string | null;
  need: string;
  blockers: string;
  competitor: string;
  nextAction: string;
  nextActionDueAt: string;
  lostReason: string;
  currentStageEnteredAt: string | null;
  daysInCurrentStage: number;
  archivedAt: string | null;
  createdAt: string;
  updatedAt: string;
  createdBy: string | null;
  updatedBy: string | null;
};

export type OpportunityFormValues = {
  companyId: string;
  contactId: string;
  stageId: string;
  name: string;
  service: string;
  valueEur: string;
  probability: string;
  expectedCloseDate: string;
  need: string;
  blockers: string;
  competitor: string;
  nextAction: string;
  nextActionDueAt: string;
  lostReason: string;
};

export type OpportunityStageHistory = {
  id: string;
  opportunityId: string;
  fromStageId: string | null;
  toStageId: string;
  changedBy: string | null;
  note: string | null;
  changedAt: string;
};
