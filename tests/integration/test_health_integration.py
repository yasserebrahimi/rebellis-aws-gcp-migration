import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health_and_ready(client: AsyncClient):
    r = await client.get("/health/")
    assert r.status_code == 200
    assert r.json()["status"] in ("healthy","alive","ok")

    r2 = await client.get("/health/ready")
    assert r2.status_code == 200
    checks = r2.json()["checks"]
    assert "database" in checks and "redis" in checks
