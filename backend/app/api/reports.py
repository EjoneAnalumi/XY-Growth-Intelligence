import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import get_current_user, require_roles
from app.schemas.reports import (
    ReportDownloadResponse,
    ReportGenerateRequest,
    ReportListResponse,
    ReportResponse,
    ReportStatusUpdate,
)
from app.schemas.users import CurrentUser
from app.services.report_repository import (
    ReportPersistenceError,
    ReportScanIneligibleError,
    ReportScanNotFoundError,
    SupabaseReportRepository,
    get_report_repository,
)

router = APIRouter(prefix="/reports", tags=["reports"])
logger = logging.getLogger(__name__)

ReaderUser = Annotated[CurrentUser, Depends(get_current_user)]
GeneratorUser = Annotated[
    CurrentUser,
    Depends(require_roles("admin", "management", "technical_analyst")),
]
ApproverUser = Annotated[CurrentUser, Depends(require_roles("admin", "management"))]


def get_configured_report_repository() -> SupabaseReportRepository:
    try:
        return get_report_repository()
    except ReportPersistenceError as exc:
        raise HTTPException(
            status_code=503, detail="Report service is temporarily unavailable."
        ) from exc


Repository = Annotated[SupabaseReportRepository, Depends(get_configured_report_repository)]


@router.get("", response_model=ReportListResponse)
def list_reports(repository: Repository, current_user: ReaderUser) -> ReportListResponse:
    try:
        reports = repository.list_reports()
    except ReportPersistenceError as exc:
        raise HTTPException(
            status_code=503, detail="Report service is temporarily unavailable."
        ) from exc
    return ReportListResponse(items=reports, total=len(reports))


@router.post(
    "/generate",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
    responses={403: {"description": "User role cannot generate reports."}},
)
def generate_report(
    payload: ReportGenerateRequest,
    repository: Repository,
    current_user: GeneratorUser,
) -> ReportResponse:
    try:
        report = repository.generate_report(payload, current_user)
    except ReportScanNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Snapshot was not found.") from exc
    except ReportScanIneligibleError as exc:
        raise HTTPException(
            status_code=409, detail="Snapshot is not approved and complete."
        ) from exc
    except ReportPersistenceError as exc:
        raise HTTPException(
            status_code=503, detail="Report service is temporarily unavailable."
        ) from exc
    logger.info(
        "report_generated",
        extra={
            "event": "report_generated",
            "report_id": str(report["id"]),
            "status": report["status"],
        },
    )
    return report


@router.post("/{report_id}/review", response_model=ReportResponse)
def submit_report_for_review(
    report_id: str,
    payload: ReportStatusUpdate,
    repository: Repository,
    current_user: GeneratorUser,
) -> ReportResponse:
    try:
        report = repository.submit_for_review(report_id, current_user)
    except ReportPersistenceError as exc:
        raise HTTPException(
            status_code=503, detail="Report service is temporarily unavailable."
        ) from exc
    if report is None:
        raise HTTPException(status_code=400, detail="Report must be draft before review.")

    return report


@router.post("/{report_id}/approve", response_model=ReportResponse)
def approve_report(
    report_id: str,
    payload: ReportStatusUpdate,
    repository: Repository,
    current_user: ApproverUser,
) -> ReportResponse:
    try:
        report = repository.approve_report(report_id, current_user)
    except ReportPersistenceError as exc:
        raise HTTPException(
            status_code=503, detail="Report service is temporarily unavailable."
        ) from exc
    if report is None:
        raise HTTPException(status_code=400, detail="Report must be in review before approval.")

    return report


@router.post("/{report_id}/share", response_model=ReportResponse)
def share_report(
    report_id: str,
    payload: ReportStatusUpdate,
    repository: Repository,
    current_user: ApproverUser,
) -> ReportResponse:
    try:
        report = repository.share_report(report_id, current_user)
    except ReportPersistenceError as exc:
        raise HTTPException(
            status_code=503, detail="Report service is temporarily unavailable."
        ) from exc
    if report is None:
        raise HTTPException(status_code=400, detail="Report must be approved before sharing.")
    return report


@router.post("/{report_id}/archive", response_model=ReportResponse)
def archive_report(
    report_id: str,
    payload: ReportStatusUpdate,
    repository: Repository,
    current_user: ApproverUser,
) -> ReportResponse:
    try:
        report = repository.archive_report(report_id, current_user)
    except ReportPersistenceError as exc:
        raise HTTPException(
            status_code=503, detail="Report service is temporarily unavailable."
        ) from exc
    if report is None:
        raise HTTPException(status_code=400, detail="Report cannot be archived.")

    return report


@router.get("/{report_id}/download", response_model=ReportDownloadResponse)
def download_report(
    report_id: str,
    repository: Repository,
    current_user: ApproverUser,
) -> ReportDownloadResponse:
    try:
        download = repository.download_report(report_id, current_user)
    except ReportPersistenceError as exc:
        raise HTTPException(
            status_code=503, detail="Report service is temporarily unavailable."
        ) from exc
    if download is None:
        raise HTTPException(status_code=404, detail="Approved report PDF was not found.")

    return download
