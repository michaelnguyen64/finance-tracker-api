from __future__ import annotations

import uuid

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.middleware import RequestLoggingMiddleware


def _make_app() -> FastAPI:
    """Minimal app with only the logging middleware attached."""
    app = FastAPI()
    app.add_middleware(RequestLoggingMiddleware)

    @app.get("/ping")
    async def ping() -> dict[str, str]:
        return {"ok": "true"}

    return app


def test_middleware_adds_x_request_id_header() -> None:
    client = TestClient(_make_app())
    response = client.get("/ping")
    assert response.status_code == 200
    assert "x-request-id" in response.headers


def test_middleware_request_id_is_valid_uuid() -> None:
    client = TestClient(_make_app())
    response = client.get("/ping")
    request_id = response.headers["x-request-id"]
    # Raises ValueError if not a valid UUID
    parsed = uuid.UUID(request_id)
    assert str(parsed) == request_id


def test_middleware_generates_unique_request_id_per_request() -> None:
    client = TestClient(_make_app())
    id_1 = client.get("/ping").headers["x-request-id"]
    id_2 = client.get("/ping").headers["x-request-id"]
    assert id_1 != id_2
