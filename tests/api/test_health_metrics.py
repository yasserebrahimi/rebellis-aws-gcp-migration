import os, pytest, httpx

BASE = os.getenv("BASE_URL","http://localhost:8000")

@pytest.mark.asyncio
async def test_health():
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{BASE}/health")
        assert r.status_code == 200

@pytest.mark.asyncio
async def test_metrics():
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{BASE}/metrics")
        assert r.status_code == 200
        assert "http_requests_total" in r.text or "process_cpu_seconds_total" in r.text
