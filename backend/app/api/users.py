from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import get_current_user, require_roles
from app.core.config import Settings, get_settings
from app.schemas.users import (
    AuditLogListResponse,
    CurrentUser,
    InvitationResponse,
    UserAdminUpdate,
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
    body: dict[str, object] = {
        "email": payload.email,
        "data": {"full_name": payload.full_name},
    }
    params = {"redirect_to": payload.redirect_to} if payload.redirect_to else None
    try:
        response = httpx.post(
            f"{settings.supabase_url}/auth/v1/invite",
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
    payload: UserAdminUpdate,
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
    repository = UserRepository(settings.database_url)
    if payload.email:
        try:
            response = httpx.put(
                f"{settings.supabase_url}/auth/v1/admin/users/{user_id}",
                headers={
                    "apikey": settings.supabase_service_role_key,
                    "Authorization": f"Bearer {settings.supabase_service_role_key}",
                },
                json={"email": payload.email, "email_confirm": True},
                timeout=10,
            )
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail="Supabase user update failed.") from exc
        if response.status_code >= 400:
            raise HTTPException(status_code=502, detail="Supabase could not update the user email.")
    profile_payload = UserRoleUpdate.model_validate(
        payload.model_dump(exclude={"email"}, exclude_unset=True)
    )
    profile = repository.update_profile(user_id, profile_payload)
    if profile is None:
        raise HTTPException(status_code=404, detail="User not found.")
    repository.record_audit(current_user.id, user_id, "updated")
    return profile


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    current_user: Annotated[CurrentUser, Depends(require_roles("admin"))],
    settings: Annotated[Settings, Depends(get_settings)],
) -> None:
    if user_id == current_user.id:
        raise HTTPException(status_code=422, detail="Administrators cannot delete themselves.")
    if not all((settings.supabase_url, settings.supabase_service_role_key, settings.database_url)):
        raise HTTPException(
            status_code=503,
            detail="Supabase user administration is not configured.",
        )
    try:
        response = httpx.delete(
            f"{settings.supabase_url}/auth/v1/admin/users/{user_id}",
            headers={
                "apikey": settings.supabase_service_role_key,
                "Authorization": f"Bearer {settings.supabase_service_role_key}",
            },
            timeout=10,
        )
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Supabase user deletion failed.") from exc
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="User not found.")
    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail="Supabase could not delete the user.")
    UserRepository(settings.database_url).record_audit(current_user.id, user_id, "deleted")
