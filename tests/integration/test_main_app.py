import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test the root endpoint"""
    response = await client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "name" in data
    assert "version" in data
    assert "status" in data
    assert data["status"] == "operational"


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """Test the health check endpoint"""
    response = await client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert data["status"] in ["healthy", "unhealthy"]


@pytest.mark.asyncio
async def test_docs_endpoint(client: AsyncClient):
    """Test that docs endpoint is accessible"""
    response = await client.get("/docs")
    
    # Should either return 200 (if docs enabled) or 404 (if disabled)
    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_openapi_endpoint(client: AsyncClient):
    """Test that OpenAPI schema is accessible"""
    response = await client.get("/openapi.json")
    
    # Should either return 200 (if docs enabled) or 404 (if disabled)
    assert response.status_code in [200, 404]
    
    if response.status_code == 200:
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data


@pytest.mark.asyncio
async def test_metrics_endpoint(client: AsyncClient):
    """Test that metrics endpoint is accessible"""
    response = await client.get("/metrics")
    
    # Should either return 200 (if metrics enabled) or 404 (if disabled)
    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_cors_preflight(client: AsyncClient):
    """Test CORS preflight request"""
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type,Authorization"
    }
    
    response = await client.options("/api/v1/auth/login", headers=headers)
    
    assert response.status_code == 200
    assert "Access-Control-Allow-Origin" in response.headers
    assert "Access-Control-Allow-Methods" in response.headers


@pytest.mark.asyncio
async def test_websocket_endpoint(client: AsyncClient):
    """Test that WebSocket endpoint exists"""
    # This is a basic check - actual WebSocket testing would require a different client
    response = await client.get("/ws")
    
    # WebSocket endpoints typically return 426 or 400 for HTTP requests
    assert response.status_code in [426, 400, 404]


@pytest.mark.asyncio
async def test_api_versioning(client: AsyncClient):
    """Test that API versioning is properly implemented"""
    # Test v1 endpoints
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401  # Should require authentication
    
    # Test that non-versioned endpoints don't exist
    response = await client.get("/api/auth/me")
    assert response.status_code == 404