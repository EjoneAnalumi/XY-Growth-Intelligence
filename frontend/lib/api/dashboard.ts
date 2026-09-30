import { apiRequest } from "@/lib/api/client";
import type { DashboardSummary } from "@/types/dashboard";

type DashboardSummaryApiResponse = {
  total_opportunities: number;
  open_opportunities: number;
  won_opportunities: number;
  lost_opportunities: number;
  pipeline_value_eur: number;
  weighted_pipeline_value_eur: number;
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
    total_value_eur: number;
    weighted_value_eur: number;
  }[];
  priority_opportunities: {
    opportunity_id: string;
    name: string;
    stage_id: string;
    stage_name: string;
    company_id: string;
    priority_score: number;
    weighted_value_eur: number;
    days_in_current_stage: number;
    reason: string;
    owner_id: string | null;
    next_action: string | null;
    due_at: string | null;
  }[];
};

function mapDashboardSummary(summary: DashboardSummaryApiResponse): DashboardSummary {
  return {
    totalOpportunities: summary.total_opportunities,
    openOpportunities: summary.open_opportunities,
    wonOpportunities: summary.won_opportunities,
    lostOpportunities: summary.lost_opportunities,
    pipelineValueEur: summary.pipeline_value_eur,
    weightedPipelineValueEur: summary.weighted_pipeline_value_eur,
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
      totalValueEur: stage.total_value_eur,
      weightedValueEur: stage.weighted_value_eur,
    })),
    priorityOpportunities: summary.priority_opportunities.map((opportunity) => ({
      opportunityId: opportunity.opportunity_id,
      name: opportunity.name,
      stageId: opportunity.stage_id,
      stageName: opportunity.stage_name,
      companyId: opportunity.company_id,
      priorityScore: opportunity.priority_score,
      weightedValueEur: opportunity.weighted_value_eur,
      daysInCurrentStage: opportunity.days_in_current_stage,
      reason: opportunity.reason,
      ownerId: opportunity.owner_id,
      nextAction: opportunity.next_action,
      dueAt: opportunity.due_at,
    })),
  };
}

export async function getDashboardSummary(): Promise<DashboardSummary> {
  const response = await apiRequest<DashboardSummaryApiResponse>("/dashboard/summary");
  return mapDashboardSummary(response);
}
