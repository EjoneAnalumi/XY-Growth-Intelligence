from fastapi import APIRouter, HTTPException, status

from app.schemas.pipeline_stages import (
    PipelineStageCreate,
    PipelineStageListResponse,
    PipelineStageResponse,
    PipelineStageUpdate,
)
from app.services.crud_pipeline_stage import (
    create_pipeline_stage,
    delete_pipeline_stage,
    get_pipeline_stage,
    get_pipeline_stages,
    update_pipeline_stage,
)

router = APIRouter(prefix="/pipeline-stages", tags=["Pipeline Stages"])


@router.post("", response_model=PipelineStageResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=PipelineStageResponse, status_code=status.HTTP_201_CREATED)
def create(data: PipelineStageCreate):
    return create_pipeline_stage(data.model_dump(mode="json"))


@router.get("", response_model=PipelineStageListResponse)
@router.get("/", response_model=PipelineStageListResponse)
def get_all():
    stages = get_pipeline_stages()
    return {"items": stages, "total": len(stages)}


@router.get("/{stage_id}", response_model=PipelineStageResponse)
def get_one(stage_id: str):
    stage = get_pipeline_stage(stage_id)

    if not stage:
        raise HTTPException(status_code=404, detail="Pipeline stage not found")

    return stage


@router.patch("/{stage_id}", response_model=PipelineStageResponse)
def update(stage_id: str, data: PipelineStageUpdate):
    stage = update_pipeline_stage(stage_id, data.model_dump(exclude_none=True, mode="json"))

    if not stage:
        raise HTTPException(status_code=404, detail="Pipeline stage not found")

    return stage


@router.delete("/{stage_id}")
def delete(stage_id: str):
    return delete_pipeline_stage(stage_id)
