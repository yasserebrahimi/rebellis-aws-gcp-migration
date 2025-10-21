from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time

app = FastAPI(title="Rebellis Motion Service")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/health")
async def health():
    return {"status": "ok", "service": "motion"}

class MotionRequest(BaseModel):
    prompt: str

class MotionResponse(BaseModel):
    file_url: str
    latency_ms: float

@app.post("/infer", response_model=MotionResponse)
async def infer(req: MotionRequest):
    t0 = time.perf_counter()
    time.sleep(0.1)
    dt = (time.perf_counter() - t0) * 1000
    return MotionResponse(file_url="s3://bucket/out/demo.bvh", latency_ms=dt)

# Prometheus metrics
try:
    from prometheus_fastapi_instrumentator import Instrumentator
    from prometheus_client import Counter, Histogram, Gauge
    Instrumentator().instrument(app).expose(app, include_in_schema=False, endpoint="/metrics", should_gzip=True)
    INF_HIST = Histogram('rebellis_inference_seconds', 'Time spent in inference', buckets=[0.05,0.1,0.25,0.5,1,2,4,8], labelnames=['service','operation'])
    INF_REQS = Counter('rebellis_inference_requests_total','Total inference requests',['service','operation'])
    INF_INPROG = Gauge('rebellis_inference_in_progress','In-progress inference requests',['service'])
    @app.middleware("http")
    async def _mw(request, call_next):
        path = request.url.path
        op = 'infer' if path.startswith('/infer') else 'other'
        if op == 'infer':
            INF_REQS.labels('motion', op).inc()
            INF_INPROG.labels('motion').inc()
            start = time.perf_counter()
            try:
                resp = await call_next(request)
                return resp
            finally:
                INF_HIST.labels('motion', op).observe(time.perf_counter()-start)
                INF_INPROG.labels('motion').dec()
        else:
            return await call_next(request)
except Exception as e:
    import logging
    logging.getLogger("uvicorn.error").warning("Motion metrics disabled: %s", e)
