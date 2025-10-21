# 🎯 Service Level Objectives

| Metric | Target | Window | Notes |
|-------|--------|--------|-------|
| Availability | ≥ 99.95 % | 30 days | Multi‑AZ where applicable |
| API p95 latency | ≤ 100 ms | 7 days | Under nominal RPS |
| Whisper p95 (30 s audio) | ≤ 3 s | 7 days | GPU pool not saturated |
| Motion p95 | ≤ 2 s | 7 days | Depends on model size |
| Error rate | ≤ 0.1 % | 7 days | 5xx only |

**Budget**: Error budget = 0.05% unavailability ≈ 21.6 min/month.
