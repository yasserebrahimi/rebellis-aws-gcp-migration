# 🛡️ Threat Model (STRIDE)

| Threat | Vector | Impact | Mitigation |
|--------|--------|--------|------------|
| Spoofing | Stolen tokens | Unauthorized access | Short‑lived JWTs, mTLS, IPS |
| Tampering | Image or config changes | Supply‑chain risk | Sigstore/BinAuthZ, Git‑signed commits |
| Repudiation | Missing logs | No audit trail | Structured logs, retention, access logs |
| Info Disclosure | Misconfigured buckets | Data leak | VPC‑SC, CMEK, least privilege |
| DoS | GPU exhaustion | Latency spikes | KEDA, quotas, rate limits, WAF |
| Elevation | Privileged pod | Cluster takeover | PSP replacement/OPA, minimal caps |
