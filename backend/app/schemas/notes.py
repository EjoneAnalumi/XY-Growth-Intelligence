from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class NoteCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "company_id": "10000000-0000-4000-8000-000000000001",
                    "body": (
                        "Client requested SOC 2 Type II compliance evidence "
                        "before contract signing."
                    ),
                }
            ]
        }
    )

    company_id: UUID | None = None
    contact_id: UUID | None = None
    opportunity_id: UUID | None = None
    body: Annotated[str, Field(min_length=1)]


class NoteUpdate(BaseModel):
    company_id: UUID | None = None
    contact_id: UUID | None = None
    opportunity_id: UUID | None = None
    body: Annotated[str | None, Field(min_length=1)] = None


class NoteResponse(NoteCreate):
    id: UUID
    created_by: UUID | None = None
    updated_by: UUID | None = None
    archived_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class NoteListResponse(BaseModel):
    items: list[NoteResponse]
    total: int
