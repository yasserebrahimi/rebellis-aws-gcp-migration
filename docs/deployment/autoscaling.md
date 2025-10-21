# 📈 Autoscaling (KEDA + HPA)

- Trigger on Redis queue length (`whisper_tasks`, `motion_tasks`)
- Scale GPU workers independently from API pods
- Define min/max replicas per environment

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata: { name: motion-queue }
spec:
  scaleTargetRef: { name: motion-deployment }
  triggers:
    - type: redis
      metadata:
        address: redis:6379
        listName: motion_tasks
        listLength: "10"
```
