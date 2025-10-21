import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_security_headers(client: AsyncClient):
    """Test that security headers are properly set"""
    response = await client.get("/")
    
    assert response.status_code == 200
    
    # Check security headers
    assert "X-Content-Type-Options" in response.headers
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    
    assert "X-Frame-Options" in response.headers
    assert response.headers["X-Frame-Options"] == "DENY"
    
    assert "X-XSS-Protection" in response.headers
    assert response.headers["X-XSS-Protection"] == "1; mode=block"
    
    assert "Strict-Transport-Security" in response.headers
    assert "max-age=31536000" in response.headers["Strict-Transport-Security"]


@pytest.mark.asyncio
async def test_rate_limiting(client: AsyncClient):
    """Test that rate limiting works"""
    # Make many requests quickly
    responses = []
    for _ in range(70):  # More than the default limit of 60
        response = await client.get("/")
        responses.append(response)
    
    # At least one should be rate limited
    rate_limited_responses = [r for r in responses if r.status_code == 429]
    assert len(rate_limited_responses) > 0
    
    # Check rate limit response
    if rate_limited_responses:
        rate_limited_response = rate_limited_responses[0]
        assert "Retry-After" in rate_limited_response.headers
        assert rate_limited_response.headers["Retry-After"] == "60"
        
        data = rate_limited_response.json()
        assert "error" in data
        assert "rate limit exceeded" in data["error"].lower()


@pytest.mark.asyncio
async def test_request_logging_middleware(client: AsyncClient):
    """Test that request logging middleware adds process time header"""
    response = await client.get("/")
    
    assert response.status_code == 200
    assert "X-Process-Time" in response.headers
    
    # Process time should be a valid float
    process_time = float(response.headers["X-Process-Time"])
    assert process_time >= 0


@pytest.mark.asyncio
async def test_cors_headers(client: AsyncClient):
    """Test that CORS headers are properly set"""
    response = await client.options("/", headers={"Origin": "http://localhost:3000"})
    
    assert "Access-Control-Allow-Origin" in response.headers
    assert "Access-Control-Allow-Methods" in response.headers
    assert "Access-Control-Allow-Headers" in response.headers


@pytest.mark.asyncio
async def test_error_handling_middleware(client: AsyncClient):
    """Test that error handling middleware works"""
    # Test 404 error
    response = await client.get("/nonexistent-endpoint")
    
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert "Not Found" in data["error"]
    assert "path" in data