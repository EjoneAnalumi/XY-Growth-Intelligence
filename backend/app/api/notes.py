from fastapi import APIRouter, HTTPException, status

from app.schemas.notes import NoteCreate, NoteListResponse, NoteResponse, NoteUpdate
from app.services.crud_note import (
    create_note,
    delete_note,
    get_note,
    get_notes,
    update_note,
)

router = APIRouter(prefix="/notes", tags=["Notes"])


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create(data: NoteCreate):
    return create_note(data.model_dump(exclude_none=True, mode="json"))


@router.get("", response_model=NoteListResponse)
@router.get("/", response_model=NoteListResponse)
def get_all():
    notes = get_notes()
    return {"items": notes, "total": len(notes)}


@router.get("/{note_id}", response_model=NoteResponse)
def get_one(note_id: str):
    note = get_note(note_id)

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    return note


@router.patch("/{note_id}", response_model=NoteResponse)
@router.put("/{note_id}", response_model=NoteResponse)
def update(note_id: str, data: NoteUpdate):
    note = update_note(note_id, data.model_dump(exclude_none=True, mode="json"))

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    return note


@router.delete("/{note_id}")
def delete(note_id: str):
    return delete_note(note_id)
