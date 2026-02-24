import pytest
import httpx
from fastapi import FastAPI

from backend.api.middleware.rate_limit_middleware import RateLimitMiddleware
from backend.main import app

@pytest.fixture
def anyio_backend():
    return "asyncio"



@pytest.mark.anyio
async def test_protected_route_requires_jwt_token():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/pipelines")
    assert response.status_code == 401


@pytest.mark.anyio
async def test_jwt_allows_access_to_protected_route():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        token_response = await client.post("/api/auth/token", json={"username": "admin", "password": "admin123"})
        token = token_response.json()["access_token"]
        response = await client.get("/api/pipelines", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


@pytest.mark.anyio
async def test_rbac_blocks_insufficient_roles():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        token_response = await client.post("/api/auth/token", json={"username": "viewer", "password": "viewer123"})
        token = token_response.json()["access_token"]
        response = await client.post(
            "/api/airflow/trigger",
            json={"pipeline_id": "x", "dag_id": "d", "dag_run_id": "r"},
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 403


@pytest.mark.anyio
async def test_rate_limiting_middleware_blocks_second_request_with_limit_one():
    mini_app = FastAPI()
    mini_app.add_middleware(RateLimitMiddleware, requests_per_minute=1)

    @mini_app.get("/ping")
    async def ping():
        return {"ok": True}

    transport = httpx.ASGITransport(app=mini_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        first = await client.get("/ping")
        second = await client.get("/ping")
    assert first.status_code == 200
    assert second.status_code == 429
