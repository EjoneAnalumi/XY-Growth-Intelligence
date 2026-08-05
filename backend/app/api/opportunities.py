from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import get_current_user, require_roles
from app.schemas.opportunities import (
    OpportunityCreate,
    OpportunityListResponse,
    OpportunityResponse,
    OpportunityStageHistoryResponse,
    OpportunityStageMove,
    OpportunityUpdate,
)
from app.schemas.users import CurrentUser
from app.services.pipeline_repository import (
    InMemoryPipelineRepository,
    get_pipeline_repository,
)

router = APIRouter(prefix="/opportunities", tags=["opportunities"])

WriterUser = Annotated[
    CurrentUser,
    Depends(require_roles("admin", "management", "business_development")),
]
ReaderUser = Annotated[CurrentUser, Depends(get_current_user)]
Repository = Annotated[InMemoryPipelineRepository, Depends(get_pipeline_repository)]


@router.post("", response_model=OpportunityResponse, status_code=status.HTTP_201_CREATED)
def create_opportunity(
    data: OpportunityCreate,
    repository: Repository,
    current_user: WriterUser,
) -> OpportunityResponse:
    if not repository.stage_exists(data.stage_id):
        raise HTTPException(status_code=404, detail="Pipeline stage not found.")

    return repository.create_record("opportunities", data.model_dump(mode="json"), current_user)


@router.get("", response_model=OpportunityListResponse)
def list_opportunities(
    repository: Repository,
    current_user: ReaderUser,
) -> OpportunityListResponse:
    opportunities = repository.list_records("opportunities")
    return OpportunityListResponse(items=opportunities, total=len(opportunities))


@router.get("/{opportunity_id}", response_model=OpportunityResponse)
def get_opportunity(
    opportunity_id: str,
    repository: Repository,
    current_user: ReaderUser,
) -> OpportunityResponse:
    opportunity = repository.get_record("opportunities", opportunity_id)

    if opportunity is None:
        raise HTTPException(status_code=404, detail="Opportunity not found.")

    return opportunity


@router.patch("/{opportunity_id}", response_model=OpportunityResponse)
def update_opportunity(
    opportunity_id: str,
    data: OpportunityUpdate,
    repository: Repository,
    current_user: WriterUser,
) -> OpportunityResponse:
    payload = data.model_dump(exclude_none=True, mode="json")
    current = repository.get_record("opportunities", opportunity_id)

    if current is None:
        raise HTTPException(status_code=404, detail="Opportunity not found.")

    if payload.get("stage_id") and not repository.stage_exists(payload["stage_id"]):
        raise HTTPException(status_code=404, detail="Pipeline stage not found.")

    opportunity = repository.update_record("opportunities", opportunity_id, payload, current_user)

    if opportunity is None:
        raise HTTPException(status_code=404, detail="Opportunity not found.")

    if payload.get("stage_id") and payload["stage_id"] != current["stage_id"]:
        repository.create_stage_history(
            {
                "opportunity_id": opportunity_id,
                "from_stage_id": current["stage_id"],
                "to_stage_id": payload["stage_id"],
                "note": None,
            },
            current_user,
        )

    return opportunity


@router.delete("/{opportunity_id}", response_model=OpportunityResponse)
def archive_opportunity(
    opportunity_id: str,
    repository: Repository,
    current_user: WriterUser,
) -> OpportunityResponse:
    opportunity = repository.archive_record("opportunities", opportunity_id, current_user)

    if opportunity is None:
        raise HTTPException(status_code=404, detail="Opportunity not found.")

    return opportunity


@router.patch("/{opportunity_id}/move-stage")
def move_opportunity_stage(
    opportunity_id: str,
    body: OpportunityStageMove,
    repository: Repository,
    current_user: WriterUser,
) -> dict:
    if not repository.stage_exists(body.to_stage_id):
        raise HTTPException(status_code=404, detail="Pipeline stage not found.")

    opportunity = repository.get_record("opportunities", opportunity_id)

    if opportunity is None:
        raise HTTPException(status_code=404, detail="Opportunity not found.")

    to_stage_id = str(body.to_stage_id)

    if opportunity["stage_id"] == to_stage_id:
        raise HTTPException(status_code=400, detail="Opportunity already has this stage.")

    result = repository.move_opportunity_stage(
        opportunity_id,
        to_stage_id,
        body.note,
        current_user,
    )

    if result is None:
        raise HTTPException(status_code=404, detail="Opportunity not found.")

    updated, history = result
    return {
        "message": "Opportunity stage updated successfully.",
        "opportunity": updated,
        "history": history,
    }


@router.get(
    "/{opportunity_id}/stage-history",
    response_model=list[OpportunityStageHistoryResponse],
)
def list_opportunity_stage_history(
    opportunity_id: str,
    repository: Repository,
    current_user: ReaderUser,
) -> list[OpportunityStageHistoryResponse]:
    if repository.get_record("opportunities", opportunity_id) is None:
        raise HTTPException(status_code=404, detail="Opportunity not found.")

    return repository.list_stage_history(opportunity_id)
