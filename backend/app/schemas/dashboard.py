from pydantic import BaseModel


class PipelineStageSummary(BaseModel):
    stage_id: str
    stage_name: str
    opportunity_count: int
    total_value_usd: float
    weighted_value_usd: float


class PriorityOpportunitySummary(BaseModel):
    opportunity_id: str
    name: str
    stage_id: str
    stage_name: str
    company_id: str
    priority_score: int
    weighted_value_usd: float
    days_in_current_stage: int
    reason: str


class DashboardSummaryResponse(BaseModel):
    total_opportunities: int
    open_opportunities: int
    won_opportunities: int
    lost_opportunities: int
    pipeline_value_usd: float
    weighted_pipeline_value_usd: float
    high_priority_opportunities: int
    inactive_opportunities: int
    open_tasks: int
    overdue_tasks: int
    due_this_week_tasks: int
    activities_count: int
    average_days_in_current_stage: float
    stage_summaries: list[PipelineStageSummary]
    priority_opportunities: list[PriorityOpportunitySummary]
