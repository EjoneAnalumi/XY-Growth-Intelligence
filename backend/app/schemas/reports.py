from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

ReportStatus = Literal["draft", "review", "approved", "archived"]


class ReportGenerateRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "company_id": "10000000-0000-4000-8000-000000000001",
                    "company_name": "Northstar Commerce Group",
                    "domain": "demo.xy-cyber.example",
                    "scan_summary": (
                        "Approved demo snapshot with SPF pass, DMARC monitoring, and missing CSP."
                    ),
                }
            ]
        }
    )

    company_id: UUID
    company_name: Annotated[str, Field(min_length=1, max_length=160)]
    domain: Annotated[str, Field(min_length=1, max_length=253)]
    scan_summary: Annotated[str, Field(min_length=10, max_length=1000)]


class ReportStatusUpdate(BaseModel):
    note: Annotated[str | None, Field(max_length=500)] = None


class ReportResponse(BaseModel):
    id: UUID
    company_id: UUID
    company_name: str
    domain: str
    title: str
    status: ReportStatus
    storage_bucket: str
    storage_path: str
    download_url: str | None = None
    html_preview: str
    created_by: UUID | None = None
    reviewed_by: UUID | None = None
    approved_by: UUID | None = None
    archived_by: UUID | None = None
    created_at: datetime
    updated_at: datetime
    reviewed_at: datetime | None = None
    approved_at: datetime | None = None
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
