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
    headquarters_city: Annotated[str | None, Field(max_length=120)] = None
    headquarters_country: Annotated[str | None, Field(max_length=120)] = None
    lead_source: Annotated[str | None, Field(max_length=120)] = None
    status: Annotated[str, Field(pattern="^(prospect|qualified|customer|partner|inactive)$")] = (
        "prospect"
    )
    tags: list[str] = []


class CompanyResponse(CompanyCreate):
    id: UUID
    created_by: UUID
    updated_by: UUID
    created_at: datetime
    updated_at: datetime


class CompanyListResponse(BaseModel):
    items: list[CompanyResponse]
    total: int
