from pydantic import BaseModel


class PipelineStageSummary(BaseModel):
    stage_id: str
    stage_name: str
    opportunity_count: int
    total_value_usd: float
    weighted_value_usd: float


class DashboardSummaryResponse(BaseModel):
    total_opportunities: int
    open_opportunities: int
    won_opportunities: int
    lost_opportunities: int
    pipeline_value_usd: float
    weighted_pipeline_value_usd: float
    overdue_tasks: int
    due_this_week_tasks: int
    activities_count: int
    average_days_in_current_stage: float
    stage_summaries: list[PipelineStageSummary]
