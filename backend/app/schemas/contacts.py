from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ContactCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "company_id": "10000000-0000-4000-8000-000000000001",
                    "first_name": "Mira",
                    "last_name": "Vale",
                    "email": "mira.vale@northstar-robotics.example",
                    "title": "VP Operations",
                    "influence": "high",
                    "decision_category": "champion",
                    "is_primary": True,
                }
            ]
        }
    )

    company_id: UUID
    first_name: Annotated[str, Field(min_length=1, max_length=100)]
    last_name: Annotated[str, Field(min_length=1, max_length=100)]
    email: Annotated[
        str | None,
        Field(pattern=r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", max_length=255),
    ] = None
    phone: Annotated[str | None, Field(max_length=80)] = None
    title: Annotated[str | None, Field(max_length=160)] = None
    department: Annotated[str | None, Field(max_length=120)] = None
    role: Annotated[str | None, Field(max_length=160)] = None
    influence: Annotated[str | None, Field(pattern="^(high|medium|low|unknown)$")] = None
    decision_category: Annotated[
        str | None,
        Field(pattern="^(buyer|champion|influencer|procurement|unknown)$"),
    ] = None
    channels: list[str] = []
    is_primary: bool = False


class ContactResponse(ContactCreate):
    id: UUID
    owner_id: UUID
    created_by: UUID
    updated_by: UUID
    created_at: datetime
    updated_at: datetime


class ContactUpdate(BaseModel):
    company_id: UUID | None = None
    first_name: Annotated[str | None, Field(min_length=1, max_length=100)] = None
    last_name: Annotated[str | None, Field(min_length=1, max_length=100)] = None
    email: Annotated[
        str | None,
        Field(pattern=r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", max_length=255),
    ] = None
    title: Annotated[str | None, Field(max_length=160)] = None
    is_primary: bool | None = None


class ContactListResponse(BaseModel):
    items: list[ContactResponse]
    total: int
