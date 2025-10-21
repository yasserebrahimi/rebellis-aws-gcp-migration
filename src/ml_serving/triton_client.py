import asyncio, logging, numpy as np, pickle, hashlib
from typing import Optional, Dict, Any
import pybreaker
from prometheus_client import Histogram, Counter

try:
    import tritonclient.grpc.aio as grpcclient
    from tritonclient.utils import InferenceServerException
except Exception:
    grpcclient = None
    InferenceServerException = Exception

inference_duration = Histogram('triton_inference_duration_seconds','Time spent in Triton inference',['model','version'])
inference_errors = Counter('triton_inference_errors_total','Triton inference errors',['model'])
cache_hits = Counter('triton_cache_hits_total','Cache hits',['model'])

class RedisCache:
    def __init__(self, client=None): self.client = client
    @classmethod
    def from_url(cls, url: str):
        try:
            import redis.asyncio as redis
            return cls(redis.from_url(url, decode_responses=False))
        except Exception:
            return cls(None)
    async def get(self, k: str):
        return await self.client.get(k) if self.client else None
    async def set(self, k: str, v: bytes, ex: int = 3600):
        if self.client: await self.client.set(k, v, ex=ex)

class TritonInferenceClient:
    def __init__(self, url: str, cache: Optional[RedisCache] = None):
        self.url = url
        self.cache = cache
        self._sem = asyncio.Semaphore(8)
        self._breaker = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=30)

    def _ck(self, model: str, arr: np.ndarray) -> str:
        return f"triton:{model}:{hashlib.sha256(arr.tobytes()).hexdigest()}"

    async def transcribe(self, mel: np.ndarray, model="whisper_large_v3"):
        if grpcclient is None:
            raise RuntimeError("tritonclient not installed")
        ckey = self._ck(model, mel)
        if self.cache:
            c = await self.cache.get(ckey)
            if c:
                cache_hits.labels(model=model).inc()
                return pickle.loads(c)
        async with self._sem:
            try:
                client = grpcclient.InferenceServerClient(url=self.url, ssl=True)
                with inference_duration.labels(model=model, version="latest").time():
                    inp = grpcclient.InferInput("audio_input", mel.shape, "FP32")
                    inp.set_data_from_numpy(mel)
                    out = [grpcclient.InferRequestedOutput("transcription"),
                           grpcclient.InferRequestedOutput("confidence")]
                    res = await self._breaker.call_async(client.infer)(model_name=model, model_version="latest", inputs=[inp], outputs=out)
                tr = res.as_numpy("transcription")[0].decode("utf-8")
                conf = float(res.as_numpy("confidence")[0])
                payload = {"text": tr, "confidence": conf}
                if self.cache:
                    await self.cache.set(ckey, pickle.dumps(payload), ex=1800)
                return payload
            except Exception as e:
                inference_errors.labels(model=model).inc()
                logging.exception("Triton error")
                raise
