export type PipelineStageSummary = {
  stageId: string;
  stageName: string;
  opportunityCount: number;
  totalValueEur: number;
  weightedValueEur: number;
};

export type PriorityOpportunitySummary = {
  opportunityId: string;
  name: string;
  stageId: string;
  stageName: string;
  companyId: string;
  priorityScore: number;
  weightedValueEur: number;
  daysInCurrentStage: number;
  reason: string;
  ownerId?: string | null;
  nextAction?: string | null;
  dueAt?: string | null;
};

export type DashboardSummary = {
  totalOpportunities: number;
  openOpportunities: number;
  wonOpportunities: number;
  lostOpportunities: number;
  pipelineValueEur: number;
  weightedPipelineValueEur: number;
  highPriorityOpportunities: number;
  inactiveOpportunities: number;
  openTasks: number;
  overdueTasks: number;
  dueThisWeekTasks: number;
  activitiesCount: number;
  averageDaysInCurrentStage: number;
  stageSummaries: PipelineStageSummary[];
  priorityOpportunities: PriorityOpportunitySummary[];
};
