from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.auth import get_current_user
from app.schemas.dashboard import DashboardSummaryResponse
from app.schemas.users import CurrentUser
from app.services.analytics import management_analytics
from app.services.growth_repository import (
    InMemoryGrowthRepository,
    get_growth_repository,
)
from app.services.pipeline_repository import (
    InMemoryPipelineRepository,
    get_pipeline_repository,
)
from app.services.priority_context import priority_context

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

ReaderUser = Annotated[CurrentUser, Depends(get_current_user)]
PipelineRepository = Annotated[InMemoryPipelineRepository, Depends(get_pipeline_repository)]
GrowthRepository = Annotated[InMemoryGrowthRepository, Depends(get_growth_repository)]


@router.get("/analytics")
def get_analytics(
    pipeline_repository: PipelineRepository,
    growth_repository: GrowthRepository,
    current_user: ReaderUser,
):
    companies = growth_repository.list_companies(growth_repository.count_companies(), 0)
    return management_analytics(companies, pipeline_repository)


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    pipeline_repository: PipelineRepository,
    growth_repository: GrowthRepository,
    current_user: ReaderUser,
) -> DashboardSummaryResponse:
    return pipeline_repository.get_dashboard_summary(
        company_fit_scores=growth_repository.get_company_fit_scores(),
        company_context=priority_context(growth_repository),
    )
