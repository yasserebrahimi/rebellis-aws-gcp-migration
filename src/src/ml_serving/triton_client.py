class TritonClient:
    def __init__(self, url: str):
        self.url = url
    async def infer(self, model_name: str, inputs):
        return {"ok": True, "model": model_name}
