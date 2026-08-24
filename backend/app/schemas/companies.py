from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CompanyCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "Northstar Robotics Labs",
                    "domain": "northstar-robotics.example",
                    "website": "https://northstar-robotics.example",
                    "industry": "Manufacturing Technology",
                    "headquarters_country": "United States",
                    "lead_source": "conference",
                    "status": "prospect",
                }
            ]
        }
    )

    name: Annotated[str, Field(min_length=1, max_length=200)]
    domain: Annotated[str | None, Field(max_length=255)] = None
    website: Annotated[str | None, Field(max_length=500)] = None
    industry: Annotated[str | None, Field(max_length=120)] = None
    company_size: Annotated[str | None, Field(max_length=80)] = None
    employee_range: Annotated[str | None, Field(max_length=80)] = None
    employee_count: Annotated[int | None, Field(ge=0)] = None
    annual_revenue_usd: Annotated[float | None, Field(ge=0)] = None
    headquarters_city: Annotated[str | None, Field(max_length=120)] = None
    headquarters_country: Annotated[str | None, Field(max_length=120)] = None
    cloud_usage: list[str] = []
    regulatory_context: list[str] = []
    lead_source: Annotated[str | None, Field(max_length=120)] = None
    last_activity_at: datetime | None = None
    next_action_due_at: datetime | None = None
    lifecycle_stage: Annotated[
        str,
        Field(pattern="^(prospect|qualified|customer|archived)$"),
    ] = "prospect"
    status: Annotated[str, Field(pattern="^(prospect|qualified|customer|partner|inactive)$")] = (
        "prospect"
    )
    tags: list[str] = []


class CompanyResponse(CompanyCreate):
    id: UUID
    fit_score: int | None = None
    created_by: UUID
    updated_by: UUID
    created_at: datetime
    updated_at: datetime


class CompanyUpdate(BaseModel):
    name: Annotated[str | None, Field(min_length=1, max_length=200)] = None
    domain: Annotated[str | None, Field(max_length=255)] = None
    industry: Annotated[str | None, Field(max_length=120)] = None
    headquarters_country: Annotated[str | None, Field(max_length=120)] = None
    status: Annotated[
        str | None, Field(pattern="^(prospect|qualified|customer|partner|inactive)$")
    ] = None


class CompanyListResponse(BaseModel):
    items: list[CompanyResponse]
    total: int


class CompanyImportResponse(BaseModel):
    created: int


class CsvValidationIssue(BaseModel):
    row: int | None = None
    field: str | None = None
    code: str
