from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field


class PipelineStageCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=120)]
    sort_order: int
    default_probability: Annotated[int, Field(ge=0, le=100)] = 0
    is_won: bool = False
    is_lost: bool = False


class PipelineStageUpdate(BaseModel):
    name: Annotated[str | None, Field(min_length=1, max_length=120)] = None
    sort_order: int | None = None
    default_probability: Annotated[int | None, Field(ge=0, le=100)] = None
    is_won: bool | None = None
    is_lost: bool | None = None


class PipelineStageResponse(PipelineStageCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime


class PipelineStageListResponse(BaseModel):
    items: list[PipelineStageResponse]
    total: int
