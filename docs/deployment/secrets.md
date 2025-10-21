# 🔑 Secrets Management

- Use **Google Secret Manager** with **External Secrets Operator**
- No plaintext secrets in Helm values or CI logs
- Rotate DB and JWT keys every 90 days

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata: { name: api-secrets }
spec:
  secretStoreRef: { name: gsm, kind: ClusterSecretStore }
  target: { name: api-env }
  data:
    - secretKey: POSTGRES_PASSWORD
      remoteRef: { key: projects/<id>/secrets/POSTGRES_PASSWORD/latest }
```
