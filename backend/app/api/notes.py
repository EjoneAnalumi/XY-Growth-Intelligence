from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import get_current_user, require_roles
from app.schemas.notes import NoteCreate, NoteListResponse, NoteResponse, NoteUpdate
from app.schemas.users import CurrentUser
from app.services.note_visibility import hidden_note_ids, hide_note
from app.services.pipeline_repository import (
    InMemoryPipelineRepository,
    get_pipeline_repository,
)

router = APIRouter(prefix="/notes", tags=["notes"])

WriterUser = Annotated[
    CurrentUser,
    Depends(require_roles("admin", "management", "business_development", "technical_analyst")),
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
    hidden = hidden_note_ids(current_user.id)
    notes = [n for n in repository.list_records("notes") if str(n["id"]) not in hidden]
    return NoteListResponse(items=notes, total=len(notes))


@router.get("/{note_id}", response_model=NoteResponse)
def get_note(
    note_id: str,
    repository: Repository,
    current_user: ReaderUser,
) -> NoteResponse:
    note = repository.get_record("notes", note_id)

    if note is None or note_id in hidden_note_ids(current_user.id):
        raise HTTPException(status_code=404, detail="Note not found.")

    return note


@router.patch("/{note_id}", response_model=NoteResponse)
def update_note(
    note_id: str,
    data: NoteUpdate,
    repository: Repository,
    current_user: WriterUser,
) -> NoteResponse:
    require_note_author(repository, note_id, current_user)
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
def delete_note(
    note_id: str,
    repository: Repository,
    current_user: ReaderUser,
) -> NoteResponse:
    existing = repository.get_record("notes", note_id)
    if existing is None:
        raise HTTPException(404, "Note not found.")
    if current_user.role != "admin" and str(existing.get("created_by")) != str(current_user.id):
        raise HTTPException(403, "Only the author or an admin can delete this note for everyone.")
    note = repository.archive_record("notes", note_id, current_user)

    if note is None:
        raise HTTPException(status_code=404, detail="Note not found.")

    return note


@router.delete("/{note_id}/for-me")
def delete_note_for_me(note_id: UUID, repository: Repository, current_user: ReaderUser):
    if repository.get_record("notes", str(note_id)) is None:
        raise HTTPException(404, "Note not found.")
    hide_note(current_user.id, note_id)
    return {"deleted_for_me": True}


def require_note_author(repository, note_id, user):
    note = repository.get_record("notes", note_id)
    if note is None:
        raise HTTPException(404, "Note not found.")
    if user.role == "technical_analyst" and str(note.get("created_by")) != str(user.id):
        raise HTTPException(403, "Analysts may edit only their own notes.")
