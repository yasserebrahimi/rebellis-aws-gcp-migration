# 🧩 CI/CD Pipelines

Workflows:
- `ci.yml`: Lint, type‑check, unit tests, coverage ≥ 80%
- `security.yml`: SAST, dependency audit, container scan
- `cd.yml`: Build, push, Helm upgrade; gated by smoke tests
- `performance.yml`: k6 perf gates

Canary rollout 10% → 50% → 100% with automatic rollback on SLO breach.
