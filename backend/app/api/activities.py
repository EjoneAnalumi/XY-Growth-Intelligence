from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import get_current_user, require_roles
from app.schemas.activities import (
    ActivityCreate,
    ActivityListResponse,
    ActivityResponse,
    ActivityUpdate,
)
from app.schemas.users import CurrentUser
from app.services.pipeline_repository import (
    InMemoryPipelineRepository,
    get_pipeline_repository,
)

router = APIRouter(prefix="/activities", tags=["activities"])

WriterUser = Annotated[
    CurrentUser,
    Depends(require_roles("admin", "management", "business_development")),
]
ReaderUser = Annotated[CurrentUser, Depends(get_current_user)]
Repository = Annotated[InMemoryPipelineRepository, Depends(get_pipeline_repository)]


@router.post("", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
def create_activity(
    data: ActivityCreate,
    repository: Repository,
    current_user: WriterUser,
) -> ActivityResponse:
    return repository.create_record(
        "activities",
        data.model_dump(exclude_none=True, mode="json"),
        current_user,
    )


@router.get("", response_model=ActivityListResponse)
def list_activities(
    repository: Repository,
    current_user: ReaderUser,
) -> ActivityListResponse:
    activities = repository.list_records("activities")
    return ActivityListResponse(items=activities, total=len(activities))


@router.get("/{activity_id}", response_model=ActivityResponse)
def get_activity(
    activity_id: str,
    repository: Repository,
    current_user: ReaderUser,
) -> ActivityResponse:
    activity = repository.get_record("activities", activity_id)

    if activity is None:
        raise HTTPException(status_code=404, detail="Activity not found.")

    return activity


@router.patch("/{activity_id}", response_model=ActivityResponse)
def update_activity(
    activity_id: str,
    data: ActivityUpdate,
    repository: Repository,
    current_user: WriterUser,
) -> ActivityResponse:
    activity = repository.update_record(
        "activities",
        activity_id,
        data.model_dump(exclude_none=True, mode="json"),
        current_user,
    )

    if activity is None:
        raise HTTPException(status_code=404, detail="Activity not found.")

    return activity


@router.delete("/{activity_id}", response_model=ActivityResponse)
def archive_activity(
    activity_id: str,
    repository: Repository,
    current_user: WriterUser,
) -> ActivityResponse:
    activity = repository.archive_record("activities", activity_id, current_user)

    if activity is None:
        raise HTTPException(status_code=404, detail="Activity not found.")

    return activity
