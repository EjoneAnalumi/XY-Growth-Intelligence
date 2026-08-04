from fastapi import APIRouter, HTTPException, status

from app.services.stage_history_service import create_stage_history

from app.services.crud_opportunity import (
    create_opportunity,
    get_opportunities,
    get_opportunity_by_id,
    update_opportunity,
    delete_opportunity,
)

from app.schemas.opportunities import (
    OpportunityCreate,
    OpportunityListResponse,
    OpportunityResponse,
    OpportunityUpdate,
    OpportunityStageMove,
)


router = APIRouter(
    prefix="/opportunities",
    tags=["Opportunities"]
)


@router.post("", response_model=OpportunityResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=OpportunityResponse, status_code=status.HTTP_201_CREATED)
def create(data: OpportunityCreate):

    return create_opportunity(
        data.model_dump(
            mode="json"
        )
    )


@router.get("", response_model=OpportunityListResponse)
@router.get("/", response_model=OpportunityListResponse)
def get_all():
    opportunities = get_opportunities()

    return {
        "items": opportunities,
        "total": len(opportunities)
    }


@router.get("/{opportunity_id}", response_model=OpportunityResponse)
def get_by_id(
    opportunity_id: str
):

    opportunity = get_opportunity_by_id(
        opportunity_id
    )

    if not opportunity:
        raise HTTPException(
            status_code=404,
            detail="Opportunity not found"
        )

    return opportunity


@router.patch("/{opportunity_id}", response_model=OpportunityResponse)
def update(
    opportunity_id: str,
    data: OpportunityUpdate
):
    current = get_opportunity_by_id(
        opportunity_id
    )

    if not current:
        raise HTTPException(
            status_code=404,
            detail="Opportunity not found"
        )

    payload = data.model_dump(
        exclude_none=True,
        mode="json"
    )

    opportunity = update_opportunity(
        opportunity_id,
        payload
    )

    if not opportunity:
        raise HTTPException(
            status_code=404,
            detail="Opportunity not found"
        )

    if payload.get("stage_id") and payload["stage_id"] != current["stage_id"]:
        create_stage_history(
            {
                "opportunity_id": opportunity_id,
                "from_stage_id": current["stage_id"],
                "to_stage_id": payload["stage_id"],
            }
        )

    return opportunity


@router.delete("/{opportunity_id}")
def delete(
    opportunity_id: str
):

    return delete_opportunity(
        opportunity_id
    )


@router.patch("/{opportunity_id}/move-stage")
@router.patch("/{opportunity_id}/stage")
def move_stage(
    opportunity_id: str,
    body: OpportunityStageMove
):

    opportunity = get_opportunity_by_id(
        opportunity_id
    )

    if not opportunity:
        raise HTTPException(
            status_code=404,
            detail="Opportunity not found"
        )


    old_stage = opportunity["stage_id"]

    new_stage = str(
        body.to_stage_id
    )


    if old_stage == new_stage:
        raise HTTPException(
            status_code=400,
            detail="Opportunity already has this stage"
        )


    updated = update_opportunity(
        opportunity_id,
        {
            "stage_id": new_stage
        }
    )


    history = create_stage_history(
        {
            "opportunity_id": opportunity_id,
            "from_stage_id": old_stage,
            "to_stage_id": new_stage,
            "note": body.note
        }
    )


    return {
        "message": "Opportunity stage updated successfully",
        "opportunity": updated,
        "history": history
    }
