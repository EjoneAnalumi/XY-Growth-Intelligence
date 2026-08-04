from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ActivityCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "company_id": "10000000-0000-4000-8000-000000000001",
                    "activity_type": "meeting",
                    "subject": "Initial Security Assessment Scope Discussion",
                    "notes": "Met with VP of IT to review infrastructure requirements.",
                }
            ]
        }
    )

    company_id: UUID
    contact_id: UUID | None = None
    opportunity_id: UUID | None = None
    activity_type: Annotated[
        str,
        Field(
            pattern="^(call|email|meeting|linkedin_message|conference|introduction|workshop|demo|proposal|follow_up|internal_note)$"
        ),
    ]
    subject: Annotated[str, Field(min_length=1, max_length=255)]
    notes: str | None = None
    occurred_at: datetime | None = None
    owner_id: UUID | None = None


class ActivityUpdate(BaseModel):
    company_id: UUID | None = None
    contact_id: UUID | None = None
    opportunity_id: UUID | None = None
    activity_type: Annotated[
        str | None,
        Field(
            pattern="^(call|email|meeting|linkedin_message|conference|introduction|workshop|demo|proposal|follow_up|internal_note)$"
        ),
    ] = None
    subject: str | None = Field(
        default=None,
        min_length=1,
        max_length=255
    )
    notes: str | None = None
    occurred_at: datetime | None = None
    owner_id: UUID | None = None


class ActivityResponse(ActivityCreate):
    id: UUID
    created_by: UUID | None = None
    updated_by: UUID | None = None
    archived_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class ActivityListResponse(BaseModel):
    items: list[ActivityResponse]
    total: int
