# 🐛 Troubleshooting

| Symptom | Likely Cause | Fix |
|--------|--------------|-----|
| 503 at ingress | Pod crashloop | Rollout restart; check config |
| High p95 latency | GPU saturation | Scale GPU workers; tune batch |
| DB timeouts | Pool exhaustion | Increase pool; add index; analyze |
| Wrong JWT audience | Misconfig | Align issuer/audience; rotate keys |
