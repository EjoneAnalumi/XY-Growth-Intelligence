from datetime import date, datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OpportunityCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "company_id": "10000000-0000-4000-8000-000000000001",
                    "contact_id": "20000000-0000-4000-8000-000000000001",
                    "stage_id": "30000000-0000-4000-8000-000000000002",
                    "name": "Enterprise Security Audit & SOC Setup",
                    "service": "Managed SOC",
                    "value_usd": 45000.00,
                    "probability": 60,
                    "expected_close_date": "2026-09-30",
                    "need": "Compliance requirement for ISO 27001",
                    "next_action": "Schedule technical demo with CISO",
                }
            ]
        }
    )

    company_id: UUID
    contact_id: UUID | None = None
    stage_id: UUID
    name: Annotated[str, Field(min_length=1, max_length=255)]
    service: Annotated[str | None, Field(max_length=120)] = None
    value_usd: Annotated[float | None, Field(ge=0)] = 0.0
    probability: Annotated[int | None, Field(ge=0, le=100)] = 0
    expected_close_date: date | None = None
    owner_id: UUID | None = None
    need: str | None = None
    blockers: str | None = None
    competitor: str | None = None
    next_action: str | None = None
    next_action_due_at: datetime | None = None
    lost_reason: str | None = None


class OpportunityUpdate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "stage_id": "30000000-0000-4000-8000-000000000003",
                    "value_usd": 50000.00,
                    "probability": 80,
                    "next_action": "Send final commercial proposal",
                }
            ]
        }
    )

    name: Annotated[str | None, Field(min_length=1, max_length=255)] = None
    contact_id: UUID | None = None
    stage_id: UUID | None = None
    service: Annotated[str | None, Field(max_length=120)] = None
    value_usd: Annotated[float | None, Field(ge=0)] = None
    probability: Annotated[int | None, Field(ge=0, le=100)] = None
    expected_close_date: date | None = None
    owner_id: UUID | None = None
    need: str | None = None
    blockers: str | None = None
    competitor: str | None = None
    next_action: str | None = None
    next_action_due_at: datetime | None = None
    lost_reason: str | None = None


class OpportunityStageMove(BaseModel):
    to_stage_id: UUID
    note: str | None = None


class OpportunityResponse(OpportunityCreate):
    id: UUID
    weighted_value_usd: float | None = 0.0
    created_by: UUID | None = None
    updated_by: UUID | None = None
    archived_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class OpportunityListResponse(BaseModel):
    items: list[OpportunityResponse]
    total: int


class OpportunityStageHistoryResponse(BaseModel):
    id: UUID
    opportunity_id: UUID
    from_stage_id: UUID | None = None
    to_stage_id: UUID
    changed_by: UUID | None = None
    note: str | None = None
    changed_at: datetime