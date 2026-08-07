from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.auth import get_current_user
from app.schemas.dashboard import DashboardSummaryResponse
from app.schemas.users import CurrentUser
from app.services.growth_repository import (
    InMemoryGrowthRepository,
    get_growth_repository,
)
from app.services.pipeline_repository import (
    InMemoryPipelineRepository,
    get_pipeline_repository,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

ReaderUser = Annotated[CurrentUser, Depends(get_current_user)]
PipelineRepository = Annotated[InMemoryPipelineRepository, Depends(get_pipeline_repository)]
GrowthRepository = Annotated[InMemoryGrowthRepository, Depends(get_growth_repository)]


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    pipeline_repository: PipelineRepository,
    growth_repository: GrowthRepository,
    current_user: ReaderUser,
) -> DashboardSummaryResponse:
    return pipeline_repository.get_dashboard_summary(
        company_fit_scores=growth_repository.get_company_fit_scores(),
    )
