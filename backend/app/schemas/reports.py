from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

ReportStatus = Literal["draft", "review", "approved", "shared", "archived"]


class ReportGenerateRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "security_scan_id": "30000000-0000-4000-8000-000000000001",
                }
            ]
        }
    )

    security_scan_id: UUID


class ReportStatusUpdate(BaseModel):
    note: Annotated[str | None, Field(max_length=500)] = None


class ReportResponse(BaseModel):
    id: UUID
    company_id: UUID
    # Day 13 rows predate snapshot linkage. New generation requests still require this value.
    security_scan_id: UUID | None = None
    is_legacy: bool = False
    company_name: str
    domain: str
    title: str
    status: ReportStatus
    storage_bucket: str | None = None
    storage_path: str | None = None
    download_url: str | None = None
    html_preview: str
    created_by: UUID | None = None
    reviewed_by: UUID | None = None
    approved_by: UUID | None = None
    shared_by: UUID | None = None
    archived_by: UUID | None = None
    created_at: datetime
    updated_at: datetime
    reviewed_at: datetime | None = None
    approved_at: datetime | None = None
    shared_at: datetime | None = None
    archived_at: datetime | None = None


class ReportListResponse(BaseModel):
    items: list[ReportResponse]
    total: int


class ReportDownloadResponse(BaseModel):
    id: UUID
    filename: str
    content_type: str
    storage_bucket: str
    storage_path: str
    size_bytes: int
    content_base64: str
