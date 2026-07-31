from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_local_frontend_origin_is_allowed_for_api_requests() -> None:
    response = client.options(
        "/companies",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
