import { apiRequest } from "@/lib/api/client";
import type { DashboardSummary } from "@/types/dashboard";

type DashboardSummaryApiResponse = {
  total_opportunities: number;
  open_opportunities: number;
  won_opportunities: number;
  lost_opportunities: number;
  pipeline_value_usd: number;
  weighted_pipeline_value_usd: number;
  high_priority_opportunities: number;
  inactive_opportunities: number;
  open_tasks: number;
  overdue_tasks: number;
  due_this_week_tasks: number;
  activities_count: number;
  average_days_in_current_stage: number;
  stage_summaries: {
    stage_id: string;
    stage_name: string;
    opportunity_count: number;
    total_value_usd: number;
    weighted_value_usd: number;
  }[];
  priority_opportunities: {
    opportunity_id: string;
    name: string;
    stage_id: string;
    stage_name: string;
    company_id: string;
    priority_score: number;
    weighted_value_usd: number;
    days_in_current_stage: number;
    reason: string;
  }[];
};

function mapDashboardSummary(summary: DashboardSummaryApiResponse): DashboardSummary {
  return {
    totalOpportunities: summary.total_opportunities,
    openOpportunities: summary.open_opportunities,
    wonOpportunities: summary.won_opportunities,
    lostOpportunities: summary.lost_opportunities,
    pipelineValueUsd: summary.pipeline_value_usd,
    weightedPipelineValueUsd: summary.weighted_pipeline_value_usd,
    highPriorityOpportunities: summary.high_priority_opportunities,
    inactiveOpportunities: summary.inactive_opportunities,
    openTasks: summary.open_tasks,
    overdueTasks: summary.overdue_tasks,
    dueThisWeekTasks: summary.due_this_week_tasks,
    activitiesCount: summary.activities_count,
    averageDaysInCurrentStage: summary.average_days_in_current_stage,
    stageSummaries: summary.stage_summaries.map((stage) => ({
      stageId: stage.stage_id,
      stageName: stage.stage_name,
      opportunityCount: stage.opportunity_count,
      totalValueUsd: stage.total_value_usd,
      weightedValueUsd: stage.weighted_value_usd,
    })),
    priorityOpportunities: summary.priority_opportunities.map((opportunity) => ({
      opportunityId: opportunity.opportunity_id,
      name: opportunity.name,
      stageId: opportunity.stage_id,
      stageName: opportunity.stage_name,
      companyId: opportunity.company_id,
      priorityScore: opportunity.priority_score,
      weightedValueUsd: opportunity.weighted_value_usd,
      daysInCurrentStage: opportunity.days_in_current_stage,
      reason: opportunity.reason,
    })),
  };
}

export async function getDashboardSummary(): Promise<DashboardSummary> {
  const response = await apiRequest<DashboardSummaryApiResponse>("/dashboard/summary");
  return mapDashboardSummary(response);
}
