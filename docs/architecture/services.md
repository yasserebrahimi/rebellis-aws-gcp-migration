# ⚙️ Service Catalog

| Service | Language | Interfaces | Dependencies | Responsibility |
|--------|----------|------------|--------------|----------------|
| api | Python / FastAPI | REST, WebSocket, /metrics | Redis, Postgres, Triton | Request validation, auth, orchestration |
| whisper | Python + Triton | gRPC | GPU, Model weights | Speech→Text inference |
| motion | Python + TensorRT | gRPC | GPU, Model weights | Text→Motion generation |
| websocket | Python | WebSocket | Redis | Realtime events |
| auth | Python | REST | JWKS/Keys | OAuth2/JWT issuance & validation |
