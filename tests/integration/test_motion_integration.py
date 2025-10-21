import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_motion_generate(client: AsyncClient, register_and_login):
    headers = await register_and_login(client)
    payload = {"audio_path":"demo.wav","parameters":{"speed":1.0}}
    r = await client.post("/motion/generate", headers=headers, json=payload)
    assert r.status_code == 200
    out = r.json()
    assert out["status"] == "completed"
    assert out["motion_path"].endswith(".bin")
