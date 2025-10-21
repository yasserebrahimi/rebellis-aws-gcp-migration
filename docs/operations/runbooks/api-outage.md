# 🧩 Runbook — API Outage

1. `kubectl get pods -n rebellis`
2. Inspect logs: `kubectl logs deploy/api -n rebellis`
3. Check DB/Redis connectivity
4. If unhealthy > 5 min → `kubectl rollout restart deployment/api -n rebellis`
5. Verify SLOs; open incident; communicate status
