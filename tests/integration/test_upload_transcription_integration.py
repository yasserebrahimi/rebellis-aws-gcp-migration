import io, pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_upload_and_transcribe_flow(client: AsyncClient, register_and_login):
    headers = await register_and_login(client)

    # Upload
    blob = b"dummy"
    files = {"file": ("demo.wav", io.BytesIO(blob), "audio/wav")}
    r = await client.post("/upload/audio", headers=headers, files=files)
    assert r.status_code == 200
    data = r.json()
    assert data["file_id"] == "demo.wav"
    assert data["file_size"] == len(blob)

    # Transcribe (stub)
    r = await client.post("/transcription/transcribe", headers=headers, files=files)
    assert r.status_code == 200
    t = r.json()
    assert "text" in t and "language" in t
