export type PipelineStageSummary = {
  stageId: string;
  stageName: string;
  opportunityCount: number;
  totalValueUsd: number;
  weightedValueUsd: number;
};

export type PriorityOpportunitySummary = {
  opportunityId: string;
  name: string;
  stageId: string;
  stageName: string;
  companyId: string;
  priorityScore: number;
  weightedValueUsd: number;
  daysInCurrentStage: number;
  reason: string;
};

export type DashboardSummary = {
  totalOpportunities: number;
  openOpportunities: number;
  wonOpportunities: number;
  lostOpportunities: number;
  pipelineValueUsd: number;
  weightedPipelineValueUsd: number;
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
