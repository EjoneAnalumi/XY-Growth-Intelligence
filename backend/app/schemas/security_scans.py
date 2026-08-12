from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SnapshotRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "domain": "demo.xy-cyber.example",
                    "approved": True,
                    "approval_note": "Approved internal demo target.",
                    "timeout_seconds": 2,
                }
            ]
        }
    )

    domain: Annotated[str, Field(min_length=1, max_length=253)]
    approved: bool
    approval_note: Annotated[str, Field(min_length=5, max_length=500)]
    timeout_seconds: Annotated[float, Field(ge=0.5, le=10)] = 3

    @field_validator("domain")
    @classmethod
    def domain_must_not_be_empty(cls, value: str) -> str:
        normalized = value.strip()

        if not normalized:
            raise ValueError("Domain is required.")

        return normalized


class SnapshotCheckResult(BaseModel):
    check: str
    status: Literal["pass", "fail", "observation", "error", "timeout", "skipped"]
    summary: str
    finding: bool = False
    severity: Literal["info", "low", "medium", "high"] = "info"
    method: str = ""
    evidence: list[str] = []
    error_classification: str | None = None
    details: dict[str, str | int | float | bool | list[str] | None] = {}


class SnapshotResponse(BaseModel):
    domain: str
    approved: bool
    started_at: datetime
    completed_at: datetime
    duration_ms: int
    results: list[SnapshotCheckResult]
