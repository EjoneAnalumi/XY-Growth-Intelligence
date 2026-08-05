from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import get_current_user, require_roles
from app.schemas.tasks import TaskCreate, TaskListResponse, TaskResponse, TaskUpdate
from app.schemas.users import CurrentUser
from app.services.pipeline_repository import (
    InMemoryPipelineRepository,
    get_pipeline_repository,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])

WriterUser = Annotated[
    CurrentUser,
    Depends(require_roles("admin", "management", "business_development")),
]
ReaderUser = Annotated[CurrentUser, Depends(get_current_user)]
Repository = Annotated[InMemoryPipelineRepository, Depends(get_pipeline_repository)]


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    data: TaskCreate,
    repository: Repository,
    current_user: WriterUser,
) -> TaskResponse:
    return repository.create_record(
        "tasks",
        data.model_dump(exclude_none=True, mode="json"),
        current_user,
    )


@router.get("", response_model=TaskListResponse)
def list_tasks(
    repository: Repository,
    current_user: ReaderUser,
) -> TaskListResponse:
    tasks = repository.list_records("tasks")
    return TaskListResponse(items=tasks, total=len(tasks))


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: str,
    repository: Repository,
    current_user: ReaderUser,
) -> TaskResponse:
    task = repository.get_record("tasks", task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found.")

    return task


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: str,
    data: TaskUpdate,
    repository: Repository,
    current_user: WriterUser,
) -> TaskResponse:
    task = repository.update_record(
        "tasks",
        task_id,
        data.model_dump(exclude_none=True, mode="json"),
        current_user,
    )

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found.")

    return task


@router.delete("/{task_id}", response_model=TaskResponse)
def archive_task(
    task_id: str,
    repository: Repository,
    current_user: WriterUser,
) -> TaskResponse:
    task = repository.archive_record("tasks", task_id, current_user)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found.")

    return task
