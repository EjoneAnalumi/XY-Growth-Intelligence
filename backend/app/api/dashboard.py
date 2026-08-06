from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.auth import get_current_user
from app.schemas.dashboard import DashboardSummaryResponse
from app.schemas.users import CurrentUser
from app.services.pipeline_repository import (
    InMemoryPipelineRepository,
    get_pipeline_repository,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

ReaderUser = Annotated[CurrentUser, Depends(get_current_user)]
Repository = Annotated[InMemoryPipelineRepository, Depends(get_pipeline_repository)]


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    repository: Repository,
    current_user: ReaderUser,
) -> DashboardSummaryResponse:
    return repository.get_dashboard_summary()
