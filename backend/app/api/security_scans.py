from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import require_roles
from app.scanning.snapshot import snapshot_scanner
from app.schemas.security_scans import SnapshotRequest, SnapshotResponse
from app.schemas.users import CurrentUser
from app.services.snapshot_repository import (
    SnapshotPersistenceError,
    SupabaseSnapshotRepository,
    get_snapshot_repository,
)

router = APIRouter(prefix="/security-scans", tags=["security scans"])

AnalystUser = Annotated[
    CurrentUser,
    Depends(require_roles("admin", "management", "technical_analyst")),
]
Repository = Annotated[SupabaseSnapshotRepository, Depends(get_snapshot_repository)]


@router.post(
    "/snapshot",
    response_model=SnapshotResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"description": "Snapshot request failed validation."},
        403: {"description": "User role cannot run snapshot checks."},
        422: {"description": "Invalid snapshot payload."},
    },
)
def run_snapshot_check(
    payload: SnapshotRequest,
    current_user: AnalystUser,
    repository: Repository,
) -> SnapshotResponse:
    try:
        scan = snapshot_scanner.run(
            domain=payload.domain,
            approved=payload.approved,
            timeout_seconds=payload.timeout_seconds,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    try:
        return repository.persist(
            str(payload.company_id), payload.approval_note, scan, current_user
        )
    except SnapshotPersistenceError as exc:
        raise HTTPException(
            status_code=503, detail="Snapshot evidence could not be saved."
        ) from exc
