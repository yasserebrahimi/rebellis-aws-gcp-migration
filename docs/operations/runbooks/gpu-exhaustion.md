# 🧠 Runbook — GPU Exhaustion

- Symptoms: queue depth ↑, p95 ↑, DCGM util 95%+
- Actions: increase replicas; adjust batch size; enable preemption on low‑priority jobs; scale node pool
