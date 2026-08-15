import pytest
import httpx
from fastapi import FastAPI

from backend.api.middleware.rate_limit_middleware import RateLimitMiddleware
from backend.api.routes.executions import executions_db
from backend.api.routes.pipelines import pipelines_db
from backend.main import app


@pytest.fixture(autouse=True)
def clear_in_memory_stores():
    pipelines_db.clear()
    executions_db.clear()


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


@pytest.mark.anyio
async def test_resource_isolation_by_user_id_for_pipelines_and_executions():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        admin_token = (
            await client.post("/api/auth/token", json={"username": "admin", "password": "admin123"})
        ).json()["access_token"]
        operator_token = (
            await client.post("/api/auth/token", json={"username": "operator", "password": "operator123"})
        ).json()["access_token"]

        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        operator_headers = {"Authorization": f"Bearer {operator_token}"}

        admin_pipeline = (
            await client.post(
                "/api/pipelines",
                json={
                    "name": "admin-pipeline",
                    "description": "owned by admin",
                    "stages": [
                        {"id": "s1", "name": "In", "type": "input", "config": {"source": "test", "data": [1]}},
                        {"id": "s2", "name": "Out", "type": "output", "config": {"destination": "sink"}, "dependencies": ["s1"]},
                    ],
                },
                headers=admin_headers,
            )
        ).json()

        operator_pipeline = (
            await client.post(
                "/api/pipelines",
                json={
                    "name": "operator-pipeline",
                    "description": "owned by operator",
                    "stages": [
                        {"id": "s1", "name": "In", "type": "input", "config": {"source": "test", "data": [2]}},
                        {"id": "s2", "name": "Out", "type": "output", "config": {"destination": "sink"}, "dependencies": ["s1"]},
                    ],
                },
                headers=operator_headers,
            )
        ).json()

        admin_pipelines = await client.get("/api/pipelines", headers=admin_headers)
        operator_pipelines = await client.get("/api/pipelines", headers=operator_headers)

        assert admin_pipelines.status_code == 200
        assert operator_pipelines.status_code == 200
        assert admin_pipelines.json()["total"] == 1
        assert operator_pipelines.json()["total"] == 1
        assert admin_pipelines.json()["pipelines"][0]["id"] == admin_pipeline["id"]
        assert operator_pipelines.json()["pipelines"][0]["id"] == operator_pipeline["id"]

        cross_read = await client.get(f"/api/pipelines/{admin_pipeline['id']}", headers=operator_headers)
        assert cross_read.status_code == 404

        admin_execution = (
            await client.post(
                "/api/executions",
                json={"pipeline_id": admin_pipeline["id"]},
                headers=admin_headers,
            )
        ).json()

        operator_execution = (
            await client.post(
                "/api/executions",
                json={"pipeline_id": operator_pipeline["id"]},
                headers=operator_headers,
            )
        ).json()

        admin_executions = await client.get("/api/executions", headers=admin_headers)
        operator_executions = await client.get("/api/executions", headers=operator_headers)

        assert admin_executions.status_code == 200
        assert operator_executions.status_code == 200
        assert admin_executions.json()["total"] == 1
        assert operator_executions.json()["total"] == 1
        assert admin_executions.json()["executions"][0]["id"] == admin_execution["id"]
        assert operator_executions.json()["executions"][0]["id"] == operator_execution["id"]

        cross_execution_read = await client.get(
            f"/api/executions/{admin_execution['id']}",
            headers=operator_headers,
        )
        assert cross_execution_read.status_code == 404
