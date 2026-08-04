export type Opportunity = {
  id: string;
  companyId: string;
  contactId: string;
  stageId: string;
  name: string;
  service: string;
  valueUsd: number;
  probability: number;
  weightedValueUsd: number;
  expectedCloseDate: string;
  ownerId: string;
  need: string;
  blockers: string;
  competitor: string;
  nextAction: string;
  nextActionDueAt: string;
  lostReason: string;
  createdAt: string;
  updatedAt: string;
};

export type OpportunityFormValues = {
  companyId: string;
  contactId: string;
  stageId: string;
  name: string;
  service: string;
  valueUsd: string;
  probability: string;
  expectedCloseDate: string;
  ownerId: string;
  need: string;
  blockers: string;
  competitor: string;
  nextAction: string;
  nextActionDueAt: string;
  lostReason: string;
};
