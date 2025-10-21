# 🔧 Configuration & Environment Variables

| Variable | Required | Default | Description |
|---------|----------|---------|-------------|
| APP_ENV | yes | - | Environment: local/staging/production |
| LOG_LEVEL | no | info | Logging level |
| DB_POOL_SIZE | no | 10 | SQLAlchemy pool size |
| REDIS_URL | yes | - | redis://host:port/0 |
| JWT_ISSUER | yes | - | JWT issuer |
| JWT_AUDIENCE | yes | - | JWT audience |
| JWKS_URL | no | - | JWKS endpoint (if external) |
| TRITON_URL | yes | - | Triton gRPC endpoint |
| MAX_CONCURRENCY | no | 64 | Worker concurrency |
