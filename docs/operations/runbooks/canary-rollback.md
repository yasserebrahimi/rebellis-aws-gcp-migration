# 🔁 Runbook — Canary Rollback

1. `helm rollback rebellis <revision> -n rebellis`
2. Pause HPA autoscaling during rollback
3. Confirm p95 latency < 100 ms; resume traffic
