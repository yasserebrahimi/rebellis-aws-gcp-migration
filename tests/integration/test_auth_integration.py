import pytest
from httpx import AsyncClient
from src.core.security import verify_token

@pytest.mark.asyncio
async def test_register_login_me(client: AsyncClient):
    payload = {"email":"u1@example.com","password":"Pass123!","full_name":"U1"}
    r = await client.post("/auth/register", json=payload)
    assert r.status_code in (200,201)

    r = await client.post("/auth/login", json={"email":payload["email"],"password":payload["password"]})
    assert r.status_code == 200
    data = r.json()
    decoded = verify_token(data["access_token"])
    assert decoded["email"] == payload["email"]

    headers = {"Authorization": f"Bearer {data['access_token']}"}
    r = await client.get("/auth/me", headers=headers)
    assert r.status_code == 200
    assert r.json()["email"] == payload["email"]
