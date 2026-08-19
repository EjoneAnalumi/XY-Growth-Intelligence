from app.main import app
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
