from fastapi import APIRouter, HTTPException, status

from app.services.crud_activity import (
    create_activity,
    get_activities,
    get_activity,
    update_activity,
    delete_activity,
)

from app.schemas.activities import ActivityCreate, ActivityListResponse, ActivityResponse, ActivityUpdate


router = APIRouter(
    prefix="/activities",
    tags=["Activities"]
)


@router.post("", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
def create(data: ActivityCreate):
    return create_activity(data.model_dump(exclude_none=True, mode="json"))


@router.get("", response_model=ActivityListResponse)
@router.get("/", response_model=ActivityListResponse)
def get_all():
    activities = get_activities()
    return {"items": activities, "total": len(activities)}


@router.get("/{activity_id}", response_model=ActivityResponse)
def get_one(activity_id: str):
    activity = get_activity(activity_id)

    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    return activity


@router.patch("/{activity_id}", response_model=ActivityResponse)
@router.put("/{activity_id}", response_model=ActivityResponse)
def update(activity_id: str, data: ActivityUpdate):
    activity = update_activity(
        activity_id,
        data.model_dump(exclude_none=True, mode="json")
    )

    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    return activity


@router.delete("/{activity_id}")
def delete(activity_id: str):
    return delete_activity(activity_id)
