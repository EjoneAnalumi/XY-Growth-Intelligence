from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import get_current_user, require_roles
from app.schemas.notes import NoteCreate, NoteListResponse, NoteResponse, NoteUpdate
from app.schemas.users import CurrentUser
from app.services.pipeline_repository import (
    InMemoryPipelineRepository,
    get_pipeline_repository,
)

router = APIRouter(prefix="/notes", tags=["notes"])

WriterUser = Annotated[
    CurrentUser,
    Depends(require_roles("admin", "management", "business_development")),
]
ReaderUser = Annotated[CurrentUser, Depends(get_current_user)]
Repository = Annotated[InMemoryPipelineRepository, Depends(get_pipeline_repository)]


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(
    data: NoteCreate,
    repository: Repository,
    current_user: WriterUser,
) -> NoteResponse:
    return repository.create_record(
        "notes",
        data.model_dump(exclude_none=True, mode="json"),
        current_user,
    )


@router.get("", response_model=NoteListResponse)
def list_notes(
    repository: Repository,
    current_user: ReaderUser,
) -> NoteListResponse:
    notes = repository.list_records("notes")
    return NoteListResponse(items=notes, total=len(notes))


@router.get("/{note_id}", response_model=NoteResponse)
def get_note(
    note_id: str,
    repository: Repository,
    current_user: ReaderUser,
) -> NoteResponse:
    note = repository.get_record("notes", note_id)

    if note is None:
        raise HTTPException(status_code=404, detail="Note not found.")

    return note


@router.patch("/{note_id}", response_model=NoteResponse)
def update_note(
    note_id: str,
    data: NoteUpdate,
    repository: Repository,
    current_user: WriterUser,
) -> NoteResponse:
    note = repository.update_record(
        "notes",
        note_id,
        data.model_dump(exclude_none=True, mode="json"),
        current_user,
    )

    if note is None:
        raise HTTPException(status_code=404, detail="Note not found.")

    return note


@router.delete("/{note_id}", response_model=NoteResponse)
def archive_note(
    note_id: str,
    repository: Repository,
    current_user: WriterUser,
) -> NoteResponse:
    note = repository.archive_record("notes", note_id, current_user)

    if note is None:
        raise HTTPException(status_code=404, detail="Note not found.")

    return note
