from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.auth import get_current_user
from app.schemas.users import CurrentUser

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/me",
    response_model=CurrentUser,
    responses={
        401: {
            "description": "Missing or invalid bearer token.",
            "content": {"application/json": {"example": {"detail": "Missing bearer token."}}},
        }
    },
)
def read_current_user(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> CurrentUser:
    return current_user
