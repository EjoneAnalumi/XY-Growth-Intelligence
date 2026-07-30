from typing import Literal

from pydantic import BaseModel, ConfigDict

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
