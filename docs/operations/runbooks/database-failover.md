# 💾 Runbook — Database Failover

Cloud SQL HA auto‑failover ≈ 30 s.
Manual:
```bash
gcloud sql instances failover rebellis-postgres
```
Validate app connections; run smoke tests.
