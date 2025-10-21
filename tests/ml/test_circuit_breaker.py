import asyncio, numpy as np, pytest
from src.ml_serving.triton_client import TritonInferenceClient, RedisCache

@pytest.mark.asyncio
async def test_circuit_breaker_trips(monkeypatch):
    cli = TritonInferenceClient(url="grpc://invalid:443", cache=RedisCache(None))

    class DummyClient:
        async def infer(self, *a, **kw):
            raise RuntimeError("boom")

    # Monkeypatch inside client call path
    import tritonclient.grpc.aio as grpcclient
    grpcclient.InferenceServerClient = lambda url, ssl=True: DummyClient()

    mel = np.zeros((80, 3000), dtype=np.float32)
    # trip breaker by repeated failures
    for _ in range(6):
        with pytest.raises(Exception):
            await cli.transcribe(mel)
