from prometheus_client import Counter, Histogram, Gauge, generate_latest

class MetricsCollector:
    def __init__(self):
        self.request_count = Counter("http_requests_total","Total HTTP requests",["method","endpoint","status"])
        self.request_duration = Histogram("http_request_duration_seconds","HTTP request duration seconds",["method","endpoint"])
        self.model_inference_count = Counter("ml_model_inference_total","Total ML inferences",["model","status"])
        self.model_inference_duration = Histogram("ml_model_inference_duration_seconds","ML inference duration",["model"])
        self.cache_hits = Counter("cache_hits_total","Cache hits",["cache_type"])
        self.cache_misses = Counter("cache_misses_total","Cache misses",["cache_type"])
        self.active_connections = Gauge("active_connections","Active connections")
        self.queue_size = Gauge("queue_size","Processing queue size",["queue_name"])

    def record_request(self, method:str, path:str, status_code:int, duration:float):
        self.request_count.labels(method=method, endpoint=path, status=str(status_code)).inc()
        self.request_duration.labels(method=method, endpoint=path).observe(duration)

    def record_inference(self, model:str, status:str, duration:float):
        self.model_inference_count.labels(model=model, status=status).inc()
        self.model_inference_duration.labels(model=model).observe(duration)

    def record_cache(self, cache_type:str, hit:bool):
        (self.cache_hits if hit else self.cache_misses).labels(cache_type=cache_type).inc()

    def update_gauge(self, name:str, value:float, label:str=None):
        if name == "queue_size" and label:
            self.queue_size.labels(queue_name=label).set(value)
        elif name == "active_connections":
            self.active_connections.set(value)

    def get_metrics(self):
        return generate_latest()

metrics = MetricsCollector()
