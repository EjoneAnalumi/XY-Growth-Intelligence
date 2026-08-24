from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import get_current_user, require_roles
from app.core.config import Settings, get_settings
from app.schemas.users import (
    AuditLogListResponse,
    CurrentUser,
    InvitationResponse,
    UserInvitationCreate,
    UserListResponse,
    UserProfile,
    UserRoleUpdate,
)
from app.services.user_repository import UserRepository

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


@router.get("", response_model=UserListResponse)
def list_users(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> UserListResponse:
    if not settings.database_url:
        return UserListResponse(items=[], total=0)
    profiles = UserRepository(settings.database_url).list_profiles()
    return UserListResponse(items=profiles, total=len(profiles))


@router.get("/audit-logs", response_model=AuditLogListResponse)
def list_audit_logs(
    current_user: Annotated[CurrentUser, Depends(require_roles("admin", "management"))],
    settings: Annotated[Settings, Depends(get_settings)],
) -> AuditLogListResponse:
    if not settings.database_url:
        return AuditLogListResponse(items=[], total=0)
    logs = UserRepository(settings.database_url).list_audit_logs()
    return AuditLogListResponse(items=logs, total=len(logs))


@router.post("/invitations", response_model=InvitationResponse, status_code=201)
def invite_user(
    payload: UserInvitationCreate,
    current_user: Annotated[CurrentUser, Depends(require_roles("admin"))],
    settings: Annotated[Settings, Depends(get_settings)],
) -> InvitationResponse:
    if not all((settings.supabase_url, settings.supabase_service_role_key, settings.database_url)):
        raise HTTPException(status_code=503, detail="Supabase invitations are not configured.")
    if payload.temporary_password:
        auth_path = "/auth/v1/admin/users"
        body: dict[str, object] = {
            "email": payload.email,
            "password": payload.temporary_password,
            "email_confirm": True,
            "user_metadata": {"full_name": payload.full_name},
        }
        params = None
    else:
        auth_path = "/auth/v1/invite"
        body = {"email": payload.email, "data": {"full_name": payload.full_name}}
        params = {"redirect_to": payload.redirect_to} if payload.redirect_to else None
    try:
        response = httpx.post(
            f"{settings.supabase_url}{auth_path}",
            headers={
                "apikey": settings.supabase_service_role_key,
                "Authorization": f"Bearer {settings.supabase_service_role_key}",
            },
            json=body,
            params=params,
            timeout=10,
        )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Supabase invitation service is unavailable.",
        ) from exc
    if response.status_code >= 400:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Supabase could not create the invitation.",
        )
    auth_user = response.json()
    profile = UserRepository(settings.database_url).update_profile(
        auth_user["id"], UserRoleUpdate(role=payload.role)
    )
    if profile is None:
        raise HTTPException(status_code=500, detail="Invited user profile was not created.")
    return InvitationResponse(
        id=profile.id,
        email=profile.email,
        full_name=profile.full_name,
        role=profile.role,
    )


@router.patch("/{user_id}", response_model=UserProfile)
def update_user(
    user_id: str,
    payload: UserRoleUpdate,
    current_user: Annotated[CurrentUser, Depends(require_roles("admin"))],
    settings: Annotated[Settings, Depends(get_settings)],
) -> UserProfile:
    if not settings.database_url:
        raise HTTPException(status_code=503, detail="User storage is not configured.")
    removes_own_access = payload.active is False or payload.role not in (None, "admin")
    if user_id == current_user.id and removes_own_access:
        raise HTTPException(
            status_code=422,
            detail="Administrators cannot remove their own administrator access.",
        )
    profile = UserRepository(settings.database_url).update_profile(user_id, payload)
    if profile is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return profile
