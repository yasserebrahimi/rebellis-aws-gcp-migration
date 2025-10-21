# ⚓ Helm Deployment

```bash
helm upgrade --install rebellis ./infrastructure/helm/rebellis   --namespace rebellis --create-namespace   -f values/values-staging.yaml
```

### Values keys (excerpt)
```yaml
api:
  image: gcr.io/<project>/api:{{ .Chart.AppVersion }}
  replicas: 3
  resources:
    requests: {{ cpu: "200m", memory: "256Mi" }}
    limits: {{ cpu: "1", memory: "512Mi" }}
whisper:
  gpu: true
  replicas: 2
motion:
  gpu: true
  replicas: 2
ingress:
  enabled: true
  hosts: [api.rebellis.example.com]
```
