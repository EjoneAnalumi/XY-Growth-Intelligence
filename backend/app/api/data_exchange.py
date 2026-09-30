"""Bounded CSV import/export for synthetic core CRM records."""

import csv
import io
from contextlib import closing
from datetime import UTC, datetime
from os import getenv
from typing import Annotated, Literal

import psycopg
from fastapi import APIRouter, Body, Depends, HTTPException, Response
from pydantic import ValidationError

from app.core.auth import get_current_user, require_roles
from app.schemas.activities import ActivityCreate
from app.schemas.contacts import ContactCreate
from app.schemas.opportunities import OpportunityCreate
from app.schemas.tasks import TaskCreate
from app.schemas.users import CurrentUser
from app.services.growth_repository import get_growth_repository
from app.services.pipeline_repository import get_pipeline_repository

router = APIRouter(prefix="/data", tags=["CSV data exchange"])
Entity = Literal["contacts", "opportunities", "activities", "tasks"]
MODELS = {
    "contacts": ContactCreate,
    "opportunities": OpportunityCreate,
    "activities": ActivityCreate,
    "tasks": TaskCreate,
}
Reader = Annotated[CurrentUser, Depends(get_current_user)]
Writer = Annotated[
    CurrentUser, Depends(require_roles("admin", "management", "business_development"))
]


def fields_for(entity):
    return [f for f in MODELS[entity].model_fields if f not in {"owner_id"}]


def safe_cell(value):
    if value is None:
        return ""
    if isinstance(value, list):
        value = "|".join(value)
    if isinstance(value, bool):
        value = "true" if value else "false"
    text = str(value)
    return "'" + text if text.lstrip().startswith(("=", "+", "-", "@")) else text


@router.get("/{entity}/export")
def export_records(entity: Entity, user: Reader):
    if entity == "contacts":
        growth = get_growth_repository()
        records = [
            r.model_dump(mode="json")
            for r in growth.list_contacts(None, growth.count_contacts(None), 0)
        ]
    else:
        records = get_pipeline_repository().list_records(entity)
    fields = fields_for(entity)
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    for record in records:
        writer.writerow({key: safe_cell(record.get(key)) for key in fields})
    return Response(
        output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{entity}.csv"'},
    )


@router.post("/{entity}/import", status_code=201)
def import_records(
    entity: Entity, payload: Annotated[bytes, Body(media_type="text/csv")], user: Writer
):
    if len(payload) > 1_000_000:
        raise HTTPException(413, "CSV must be at most 1 MB.")
    try:
        reader = csv.DictReader(io.StringIO(payload.decode("utf-8-sig")))
        headers = reader.fieldnames or []
        if (
            not headers
            or len(headers) != len(set(headers))
            or set(headers) - set(fields_for(entity))
        ):
            raise ValueError("Unexpected or duplicate CSV headers.")
        rows = []
        for row in reader:
            if len(rows) >= 1000 or None in row:
                raise ValueError("CSV supports at most 1000 complete rows.")
            values = {}
            for key, value in row.items():
                if value is None:
                    raise ValueError("Incomplete CSV row.")
                value = value.strip()
                if value.startswith("'") and value[1:].lstrip().startswith(("=", "+", "-", "@")):
                    value = value[1:]
                if value:
                    values[key] = value.split("|") if key == "channels" else value
            rows.append(MODELS[entity].model_validate(values))
        if not rows:
            raise ValueError("CSV contains no records.")
    except (ValueError, UnicodeError, csv.Error, ValidationError) as exc:
        raise HTTPException(422, "Invalid CSV headers, field values, or row count.") from exc
    growth = get_growth_repository()
    pipeline = get_pipeline_repository()
    for row in rows:
        if row.company_id and growth.get_company(row.company_id) is None:
            raise HTTPException(422, "CSV company does not exist; no rows imported.")
        if entity == "opportunities" and not pipeline.stage_exists(row.stage_id):
            raise HTTPException(422, "CSV stage does not exist; no rows imported.")
        contact_id = getattr(row, "contact_id", None)
        if contact_id:
            contact = growth.get_contact(contact_id)
            if contact is None or contact.company_id != row.company_id:
                raise HTTPException(
                    422, "CSV contact must belong to its company; no rows imported."
                )
        opportunity_id = getattr(row, "opportunity_id", None)
        if opportunity_id:
            opportunity = pipeline.get_record("opportunities", str(opportunity_id))
            if opportunity is None or str(row.company_id) != str(opportunity["company_id"]):
                raise HTTPException(
                    422, "CSV opportunity must belong to its company; no rows imported."
                )
    url = getenv("DATABASE_URL")
    if url:
        try:
            with closing(psycopg.connect(url)) as conn:
                for row in rows:
                    values = row.model_dump(mode="json", exclude_none=True)
                    if entity == "contacts" and "channels" not in values:
                        values["channels"] = []
                    values.update(created_by=user.id, updated_by=user.id, owner_id=user.id)
                    if entity == "opportunities":
                        values["weighted_value_eur"] = round(
                            float(values.get("value_eur") or 0)
                            * int(values.get("probability") or 0)
                            / 100,
                            2,
                        )
                    if entity == "tasks" and values.get("status") == "completed":
                        values["completed_at"] = datetime.now(UTC)
                    columns = list(values)
                    conn.execute(
                        f"insert into public.{entity} ({', '.join(columns)}) values "
                        f"({', '.join(['%s'] * len(columns))})",
                        list(values.values()),
                    )
                conn.commit()
        except psycopg.IntegrityError as exc:
            raise HTTPException(
                422,
                "CSV references invalid records or violates data constraints; no rows imported.",
            ) from exc
    else:
        for row in rows:
            if entity == "contacts":
                growth.create_contact(row, user)
            else:
                values = row.model_dump(mode="json", exclude_none=True)
                values["owner_id"] = user.id
                if entity == "tasks" and values.get("status") == "completed":
                    values["completed_at"] = datetime.now(UTC)
                pipeline.create_record(entity, values, user)
    return {"created": len(rows)}
