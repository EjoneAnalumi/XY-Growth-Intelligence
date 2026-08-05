from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import get_current_user, require_roles
from app.schemas.pipeline_stages import (
    PipelineStageCreate,
    PipelineStageListResponse,
    PipelineStageResponse,
    PipelineStageUpdate,
)
from app.schemas.users import CurrentUser
from app.services.pipeline_repository import (
    InMemoryPipelineRepository,
    get_pipeline_repository,
)

router = APIRouter(prefix="/pipeline-stages", tags=["pipeline stages"])

ManagerUser = Annotated[CurrentUser, Depends(require_roles("admin", "management"))]
ReaderUser = Annotated[CurrentUser, Depends(get_current_user)]
Repository = Annotated[InMemoryPipelineRepository, Depends(get_pipeline_repository)]


@router.post("", response_model=PipelineStageResponse, status_code=status.HTTP_201_CREATED)
def create_pipeline_stage(
    data: PipelineStageCreate,
    repository: Repository,
    current_user: ManagerUser,
) -> PipelineStageResponse:
    return repository.create_record("pipeline_stages", data.model_dump(mode="json"), current_user)


@router.get("", response_model=PipelineStageListResponse)
def list_pipeline_stages(
    repository: Repository,
    current_user: ReaderUser,
) -> PipelineStageListResponse:
    stages = sorted(
        repository.list_records("pipeline_stages"),
        key=lambda stage: stage["sort_order"],
    )
    return PipelineStageListResponse(items=stages, total=len(stages))


@router.get("/{stage_id}", response_model=PipelineStageResponse)
def get_pipeline_stage(
    stage_id: str,
    repository: Repository,
    current_user: ReaderUser,
) -> PipelineStageResponse:
    stage = repository.get_record("pipeline_stages", stage_id)

    if stage is None:
        raise HTTPException(status_code=404, detail="Pipeline stage not found.")

    return stage


@router.patch("/{stage_id}", response_model=PipelineStageResponse)
def update_pipeline_stage(
    stage_id: str,
    data: PipelineStageUpdate,
    repository: Repository,
    current_user: ManagerUser,
) -> PipelineStageResponse:
    stage = repository.update_record(
        "pipeline_stages",
        stage_id,
        data.model_dump(exclude_none=True, mode="json"),
        current_user,
    )

    if stage is None:
        raise HTTPException(status_code=404, detail="Pipeline stage not found.")

    return stage


@router.delete("/{stage_id}", response_model=PipelineStageResponse)
def archive_pipeline_stage(
    stage_id: str,
    repository: Repository,
    current_user: ManagerUser,
) -> PipelineStageResponse:
    stage = repository.archive_record("pipeline_stages", stage_id, current_user)

    if stage is None:
        raise HTTPException(status_code=404, detail="Pipeline stage not found.")

    return stage
