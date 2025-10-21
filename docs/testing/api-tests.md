# 🧪 API Tests (pytest + httpx)

```python
import httpx, pytest

def test_health():
    r = httpx.get("http://localhost:8000/health", timeout=5.0)
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
```
