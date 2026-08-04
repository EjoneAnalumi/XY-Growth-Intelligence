from fastapi import APIRouter, HTTPException, status

from app.services.crud_task import (
    create_task,
    get_tasks,
    get_task,
    update_task,
    delete_task,
)
from app.schemas.tasks import TaskCreate, TaskListResponse, TaskResponse, TaskUpdate

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create(data: TaskCreate):
    return create_task(data.model_dump(exclude_none=True, mode="json"))


@router.get("", response_model=TaskListResponse)
@router.get("/", response_model=TaskListResponse)
def get_all():
    tasks = get_tasks()
    return {"items": tasks, "total": len(tasks)}


@router.get("/{task_id}", response_model=TaskResponse)
def get_one(task_id: str):
    task = get_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@router.patch("/{task_id}", response_model=TaskResponse)
@router.put("/{task_id}", response_model=TaskResponse)
def update(task_id: str, data: TaskUpdate):
    task = update_task(
        task_id,
        data.model_dump(exclude_none=True, mode="json")
    )

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@router.delete("/{task_id}")
def delete(task_id: str):
    return delete_task(task_id)
