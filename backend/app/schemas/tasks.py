from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "title": "Prepare custom SLA document for Managed SOC",
                    "due_at": "2026-08-07T17:00:00Z",
                    "priority": "high",
                }
            ]
        }
    )

    company_id: UUID | None = None
    opportunity_id: UUID | None = None
    owner_id: UUID | None = None
    title: Annotated[str, Field(min_length=1, max_length=255)]
    description: str | None = None
    due_at: datetime | None = None
    priority: Annotated[str, Field(pattern="^(low|medium|high|urgent)$")] = "medium"
    status: Annotated[str, Field(pattern="^(open|in_progress|completed|cancelled)$")] = "open"


class TaskUpdate(BaseModel):
    company_id: UUID | None = None
    opportunity_id: UUID | None = None
    owner_id: UUID | None = None
    title: Annotated[str | None, Field(min_length=1, max_length=255)] = None
    description: str | None = None
    due_at: datetime | None = None
    priority: Annotated[str | None, Field(pattern="^(low|medium|high|urgent)$")] = None
    status: Annotated[str | None, Field(pattern="^(open|in_progress|completed|cancelled)$")] = None
    outcome: str | None = None
    completed_at: datetime | None = None


class TaskResponse(TaskCreate):
    assigned_by: UUID | None = None
    assigned_at: datetime | None = None
    id: UUID
    outcome: str | None = None
    completed_at: datetime | None = None
    created_by: UUID | None = None
    updated_by: UUID | None = None
    archived_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class TaskListResponse(BaseModel):
    items: list[TaskResponse]
    total: int
