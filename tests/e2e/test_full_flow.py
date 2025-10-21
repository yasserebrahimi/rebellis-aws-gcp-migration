import io, pytest
from httpx import AsyncClient
from src.core.security import verify_token

@pytest.mark.asyncio
async def test_end_to_end_user_journey(client: AsyncClient):
    # 1) register
    user = {"email":"e2e@example.com","password":"E2ePass123!","full_name":"E2E User"}
    r = await client.post("/auth/register", json=user)
    assert r.status_code in (200,201)

    # 2) login
    r = await client.post("/auth/login", json={"email":user["email"],"password":user["password"]})
    assert r.status_code == 200
    token = r.json()["access_token"]
    verify_token(token)
    headers = {"Authorization": f"Bearer {token}"}

    # 3) upload audio
    audio = b"dummy"
    files = {"file": ("song.wav", io.BytesIO(audio), "audio/wav")}
    r = await client.post("/upload/audio", headers=headers, files=files)
    assert r.status_code == 200

    # 4) transcribe (stub)
    r = await client.post("/transcription/transcribe", headers=headers, files=files)
    assert r.status_code == 200
    assert "text" in r.json()

    # 5) generate motion
    r = await client.post("/motion/generate", headers=headers, json={"audio_path":"song.wav","parameters":{"style":"default"}})
    assert r.status_code == 200
    assert r.json()["status"] == "completed"
