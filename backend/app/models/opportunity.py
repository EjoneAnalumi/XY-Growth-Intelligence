from fastapi import APIRouter, HTTPException

from app.schemas.opportunities import (
    OpportunityCreate,
    OpportunityStageMove,
    OpportunityUpdate,
)
from app.services.crud_opportunity import (
    create_opportunity,
    delete_opportunity,
    get_opportunities,
    get_opportunity_by_id,
    update_opportunity,
)
from app.services.stage_history_service import create_stage_history

router = APIRouter(prefix="/opportunities", tags=["Opportunities"])


@router.post("/")
def create(data: OpportunityCreate):
    return create_opportunity(data.model_dump(mode="json"))


@router.get("/")
def get_all():
    return get_opportunities()


@router.get("/{opportunity_id}")
def get_by_id(opportunity_id: str):
    opportunity = get_opportunity_by_id(opportunity_id)

    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    return opportunity


@router.patch("/{opportunity_id}")
def update(opportunity_id: str, data: OpportunityUpdate):
    return update_opportunity(opportunity_id, data.model_dump(exclude_none=True, mode="json"))


@router.delete("/{opportunity_id}")
def delete(opportunity_id: str):
    return delete_opportunity(opportunity_id)


@router.patch("/{opportunity_id}/stage")
def move_stage(opportunity_id: str, body: OpportunityStageMove):
    opportunity = get_opportunity_by_id(opportunity_id)

    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    old_stage = opportunity["stage_id"]

    new_stage = str(body.to_stage_id)

    if old_stage == new_stage:
        raise HTTPException(status_code=400, detail="Opportunity already has this stage")

    updated = update_opportunity(opportunity_id, {"stage_id": new_stage})

    history = create_stage_history(
        {
            "opportunity_id": opportunity_id,
            "from_stage_id": old_stage,
            "to_stage_id": new_stage,
            "note": body.note,
        }
    )

    return {
        "message": "Opportunity stage updated successfully",
        "opportunity": updated,
        "history": history,
    }
