from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

UserRole = Literal[
    "admin",
    "management",
    "business_development",
    "technical_analyst",
    "read_only",
]


class CurrentUser(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": "00000000-0000-4000-8000-000000000003",
                    "email": "bd.demo@example.test",
                    "full_name": "Business Development Demo",
                    "role": "business_development",
                }
            ]
        }
    )

    id: str
    email: str
    full_name: str
    role: UserRole


class UserProfile(CurrentUser):
    active: bool
    last_login_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class UserListResponse(BaseModel):
    items: list[UserProfile]
    total: int


class UserInvitationCreate(BaseModel):
    email: str = Field(pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    full_name: str = Field(min_length=2, max_length=200)
    role: UserRole = "read_only"
    redirect_to: str | None = None


class UserRoleUpdate(BaseModel):
    role: UserRole | None = None
    active: bool | None = None


class InvitationResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: UserRole


class AuditLogResponse(BaseModel):
    id: str
    user_id: str | None = None
    user_name: str | None = None
    entity_type: str
    entity_id: str
    action: str
    changed_at: datetime


class AuditLogListResponse(BaseModel):
    items: list[AuditLogResponse]
    total: int
