from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import Settings, get_settings
from app.schemas.users import CurrentUser, UserRole

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

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Supabase JWT verification is not configured yet.",
    )


def require_roles(*allowed_roles: UserRole):
    def dependency(current_user: Annotated[CurrentUser, Depends(get_current_user)]) -> CurrentUser:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to perform this action.",
            )

        return current_user

    return dependency


def raise_auth_error(detail: str) -> None:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )
