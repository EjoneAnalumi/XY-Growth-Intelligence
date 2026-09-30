"""Per-user read receipts, refreshed on navigation rather than pushed live."""

from contextlib import closing
from datetime import UTC, datetime, timedelta
from os import getenv
from typing import Annotated, Literal
from uuid import UUID

import psycopg
from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import get_current_user
from app.schemas.users import CurrentUser
from app.services.note_visibility import hidden_note_ids
from app.services.pipeline_repository import get_pipeline_repository

router = APIRouter(prefix="/inbox", tags=["personal inbox"])
Reader = Annotated[CurrentUser, Depends(get_current_user)]
memory_reads: dict[tuple[str, str, str], datetime] = {}


def receipts(user_id):
    url = getenv("DATABASE_URL")
    if not url:
        return {
            (kind, record): at
            for (uid, kind, record), at in memory_reads.items()
            if uid == str(user_id)
        }
    with closing(psycopg.connect(url)) as conn:
        return {
            (kind, str(record)): at
            for kind, record, at in conn.execute(
                "select kind,record_id,read_at from public.inbox_reads where user_id=%s",
                (str(user_id),),
            ).fetchall()
        }


@router.get("")
def get_inbox(user: Reader):
    pipeline = get_pipeline_repository()
    reads = receipts(user.id)
    now = datetime.now(UTC)
    tasks = [
        t
        for t in pipeline.list_records("tasks")
        if str(t.get("owner_id")) == str(user.id) and t["status"] not in {"completed", "cancelled"}
    ]
    hidden = hidden_note_ids(user.id)
    notes = [
        n
        for n in pipeline.list_records("notes")
        if str(n.get("created_by")) != str(user.id) and str(n["id"]) not in hidden
    ]

    def unread(kind, record, timestamp):
        seen = reads.get((kind, str(record["id"])))
        version = pipeline._parse_datetime(record.get(timestamp) or record["created_at"])
        return seen is None or seen < version

    return {
        "unread_task_ids": [t["id"] for t in tasks if unread("tasks", t, "assigned_at")],
        "unread_note_ids": [n["id"] for n in notes if unread("notes", n, "updated_at")],
        "overdue_tasks": sum(
            bool(t.get("due_at")) and pipeline._parse_datetime(t["due_at"]) < now for t in tasks
        ),
        "due_soon_tasks": sum(
            bool(t.get("due_at"))
            and now <= pipeline._parse_datetime(t["due_at"]) <= now + timedelta(days=1)
            for t in tasks
        ),
    }


@router.post("/{kind}/{record_id}/read")
def mark_read(kind: Literal["tasks", "notes"], record_id: UUID, user: Reader):
    record = get_pipeline_repository().get_record(kind, str(record_id))
    if record is None:
        raise HTTPException(404, "Record not found.")
    if kind == "tasks" and str(record.get("owner_id")) != str(user.id):
        raise HTTPException(403, "Only the assignee can acknowledge a task.")
    url = getenv("DATABASE_URL")
    if url:
        with closing(psycopg.connect(url)) as conn:
            conn.execute(
                "insert into public.inbox_reads(user_id,kind,record_id) values(%s,%s,%s) "
                "on conflict(user_id,kind,record_id) do update set read_at=clock_timestamp()",
                (str(user.id), kind, str(record_id)),
            )
            conn.commit()
    else:
        memory_reads[(str(user.id), kind, str(record_id))] = datetime.now(UTC)
    return {"read": True}
