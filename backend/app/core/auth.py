from typing import Annotated, NoReturn

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import Settings, get_settings
from app.schemas.users import CurrentUser, UserRole
from app.services.user_repository import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)

LOCAL_DEMO_TOKENS: dict[str, CurrentUser] = {
    "dev-admin": CurrentUser(
        id="00000000-0000-4000-8000-000000000001",
        email="admin.demo@example.test",
        full_name="Admin Demo",
        role="admin",
    ),
    "dev-management": CurrentUser(
        id="00000000-0000-4000-8000-000000000002",
        email="management.demo@example.test",
        full_name="Management Demo",
        role="management",
    ),
    "dev-business-development": CurrentUser(
        id="00000000-0000-4000-8000-000000000003",
        email="bd.demo@example.test",
        full_name="Business Development Demo",
        role="business_development",
    ),
    "dev-technical-analyst": CurrentUser(
        id="00000000-0000-4000-8000-000000000004",
        email="analyst.demo@example.test",
        full_name="Technical Analyst Demo",
        role="technical_analyst",
    ),
    "dev-read-only": CurrentUser(
        id="00000000-0000-4000-8000-000000000005",
        email="readonly.demo@example.test",
        full_name="Read Only Demo",
        role="read_only",
    ),
}


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> CurrentUser:
    if credentials is None:
        raise_auth_error("Missing bearer token.")

    if settings.auth_mode == "local":
        user = LOCAL_DEMO_TOKENS.get(credentials.credentials)

        if user is None:
            raise_auth_error("Invalid local development token.")

        return user

    if not all((settings.supabase_url, settings.supabase_anon_key, settings.database_url)):
        raise_auth_error("Supabase authentication is not configured.")

    try:
        response = httpx.get(
            f"{settings.supabase_url}/auth/v1/user",
            headers={
                "apikey": settings.supabase_anon_key,
                "Authorization": f"Bearer {credentials.credentials}",
            },
            timeout=5,
        )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication service is unavailable.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    if response.status_code != 200:
        raise_auth_error("Invalid or expired Supabase session.")
    auth_user = response.json()
    user = UserRepository(settings.database_url).get_profile(
        auth_user["id"], auth_user.get("email") or ""
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User profile is inactive or unavailable.",
        )
    return user


def require_roles(*allowed_roles: UserRole):
    def dependency(current_user: Annotated[CurrentUser, Depends(get_current_user)]) -> CurrentUser:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to perform this action.",
            )

        return current_user

    return dependency


def raise_auth_error(detail: str) -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )
