from datetime import UTC, datetime

from app.core.config import get_settings
from app.main import app
from app.schemas.users import CurrentUser, UserProfile
from app.services.user_repository import UserRepository
from fastapi.testclient import TestClient

client = TestClient(app)


def test_users_me_requires_bearer_token() -> None:
    response = client.get("/users/me")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"
    assert response.json()["detail"] == "Missing bearer token."


def test_users_me_rejects_invalid_local_token() -> None:
    response = client.get("/users/me", headers={"Authorization": "Bearer invalid-token"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"
    assert response.json()["detail"] == "Invalid local development token."


def test_users_me_returns_current_demo_user() -> None:
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer dev-business-development"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": "00000000-0000-4000-8000-000000000003",
        "email": "bd.demo@example.test",
        "full_name": "Business Development Demo",
        "role": "business_development",
    }


def test_openapi_documents_users_me() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/users/me" in response.json()["paths"]
    assert "/users/invitations" in response.json()["paths"]
    assert "/users/audit-logs" in response.json()["paths"]


def test_users_me_accepts_verified_supabase_session(monkeypatch) -> None:
    class Response:
        status_code = 200

        @staticmethod
        def json():
            return {"id": "00000000-0000-4000-8000-000000000003", "email": "staff@example.test"}

    settings = type(
        "Settings",
        (),
        {
            "auth_mode": "supabase",
            "supabase_url": "http://supabase.test",
            "supabase_anon_key": "anon-test",
            "database_url": "postgresql://test",
        },
    )()
    app.dependency_overrides[get_settings] = lambda: settings
    monkeypatch.setattr("app.core.auth.httpx.get", lambda *args, **kwargs: Response())
    monkeypatch.setattr(
        UserRepository,
        "get_profile",
        lambda self, user_id, email: CurrentUser(
            id=user_id,
            email=email,
            full_name="Synthetic Staff",
            role="business_development",
        ),
    )
    try:
        response = client.get("/users/me", headers={"Authorization": "Bearer verified-token"})
    finally:
        app.dependency_overrides.pop(get_settings, None)

    assert response.status_code == 200
    assert response.json()["full_name"] == "Synthetic Staff"


def test_users_me_rejects_expired_supabase_session(monkeypatch) -> None:
    class Response:
        status_code = 401

    settings = type(
        "Settings",
        (),
        {
            "auth_mode": "supabase",
            "supabase_url": "http://supabase.test",
            "supabase_anon_key": "anon-test",
            "database_url": "postgresql://test",
        },
    )()
    app.dependency_overrides[get_settings] = lambda: settings
    monkeypatch.setattr("app.core.auth.httpx.get", lambda *args, **kwargs: Response())
    try:
        response = client.get("/users/me", headers={"Authorization": "Bearer expired-token"})
    finally:
        app.dependency_overrides.pop(get_settings, None)

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired Supabase session."


def test_invitation_passes_redirect_as_supabase_query_parameter(monkeypatch) -> None:
    captured: dict = {}

    class Response:
        status_code = 200

        @staticmethod
        def json():
            return {"id": "00000000-0000-4000-8000-000000000099"}

    settings = type(
        "Settings",
        (),
        {
            "auth_mode": "local",
            "supabase_url": "http://supabase.test",
            "supabase_service_role_key": "service-test",
            "database_url": "postgresql://test",
        },
    )()
    now = datetime.now(UTC)
    profile = UserProfile(
        id="00000000-0000-4000-8000-000000000099",
        email="invited@example.test",
        full_name="Invited User",
        role="read_only",
        active=True,
        created_at=now,
        updated_at=now,
    )

    def post(url, **kwargs):
        captured.update(url=url, **kwargs)
        return Response()

    app.dependency_overrides[get_settings] = lambda: settings
    monkeypatch.setattr("app.api.users.httpx.post", post)
    monkeypatch.setattr(UserRepository, "update_profile", lambda *args: profile)
    try:
        response = client.post(
            "/users/invitations",
            headers={"Authorization": "Bearer dev-admin"},
            json={
                "email": "invited@example.test",
                "full_name": "Invited User",
                "redirect_to": "http://localhost:3002/accept-invite",
            },
        )
    finally:
        app.dependency_overrides.pop(get_settings, None)

    assert response.status_code == 201
    assert captured["url"].endswith("/auth/v1/invite")
    assert captured["params"] == {"redirect_to": "http://localhost:3002/accept-invite"}


def test_admin_cannot_delete_self() -> None:
    response = client.delete(
        "/users/00000000-0000-4000-8000-000000000001",
        headers={"Authorization": "Bearer dev-admin"},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Administrators cannot delete themselves."
