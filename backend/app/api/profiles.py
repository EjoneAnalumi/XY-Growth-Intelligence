from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import get_current_user
from app.schemas.users import CurrentUser
from app.services.growth_repository import get_growth_repository
from app.services.note_visibility import hidden_note_ids
from app.services.pipeline_repository import get_pipeline_repository

router = APIRouter(tags=["relationship profiles"])
Reader = Annotated[CurrentUser, Depends(get_current_user)]


@router.get("/companies/{company_id}/timeline")
def company_timeline(company_id: UUID, user: Reader):
    growth = get_growth_repository()
    if growth.get_company(company_id) is None:
        raise HTTPException(404, "Company not found.")
    return related_records("company_id", str(company_id), user.id)


@router.get("/contacts/{contact_id}/timeline")
def contact_timeline(contact_id: UUID, user: Reader):
    if get_growth_repository().get_contact(contact_id) is None:
        raise HTTPException(404, "Contact not found.")
    return related_records("contact_id", str(contact_id), user.id)


def related_records(key, record_id, user_id):
    pipeline = get_pipeline_repository()
    result = {}
    events = []
    hidden = hidden_note_ids(user_id)
    for collection in ("opportunities", "activities", "tasks", "notes"):
        records = [r for r in pipeline.list_records(collection) if str(r.get(key)) == record_id]
        if collection == "notes":
            records = [r for r in records if str(r["id"]) not in hidden]
        result[collection] = records
        for record in records:
            events.append(
                {
                    "id": record["id"],
                    "kind": collection,
                    "at": record.get("occurred_at") or record["created_at"],
                    "title": record.get("subject")
                    or record.get("title")
                    or record.get("name")
                    or record.get("body", ""),
                }
            )
    result["timeline"] = sorted(events, key=lambda e: str(e["at"]), reverse=True)
    if key == "company_id":
        growth = get_growth_repository()
        result["contacts"] = growth.list_contacts(
            UUID(record_id), growth.count_contacts(UUID(record_id)), 0
        )
        result["score"] = growth.get_latest_icp_score(UUID(record_id))
    return result
