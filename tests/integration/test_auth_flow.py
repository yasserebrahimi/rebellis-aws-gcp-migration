import pytest
from httpx import AsyncClient
from src.core.security import verify_token


@pytest.mark.asyncio
async def test_register_login_flow(client: AsyncClient):
    """Test complete registration and login flow"""
    # Register new user
    user_data = {
        "email": "newuser@example.com",
        "password": "TestPassword123!",
        "full_name": "New User"
    }
    
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code in [200, 201]
    
    # Login with registered user
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    # Verify token
    token = data["access_token"]
    payload = verify_token(token)
    assert payload["email"] == user_data["email"]


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Test registration with duplicate email"""
    user_data = {
        "email": "duplicate@example.com",
        "password": "TestPassword123!",
        "full_name": "First User"
    }
    
    # First registration should succeed
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code in [200, 201]
    
    # Second registration with same email should fail
    user_data["full_name"] = "Second User"
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Test login with invalid credentials"""
    # Register user first
    user_data = {
        "email": "testuser@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User"
    }
    
    await client.post("/api/v1/auth/register", json=user_data)
    
    # Try login with wrong password
    login_data = {
        "email": user_data["email"],
        "password": "WrongPassword123!"
    }
    
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_me_endpoint_with_valid_token(client: AsyncClient, register_and_login):
    """Test /me endpoint with valid token"""
    headers = await register_and_login(client)
    
    response = await client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "email" in data
    assert "full_name" in data
    assert "is_active" in data
    assert "is_admin" in data


@pytest.mark.asyncio
async def test_me_endpoint_without_token(client: AsyncClient):
    """Test /me endpoint without token"""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_endpoint_with_invalid_token(client: AsyncClient):
    """Test /me endpoint with invalid token"""
    headers = {"Authorization": "Bearer invalid_token"}
    
    response = await client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_register_validation_errors(client: AsyncClient):
    """Test registration with validation errors"""
    # Test with invalid email
    user_data = {
        "email": "invalid-email",
        "password": "TestPassword123!",
        "full_name": "Test User"
    }
    
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 422
    
    # Test with weak password
    user_data = {
        "email": "test@example.com",
        "password": "weak",
        "full_name": "Test User"
    }
    
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 422
    
    # Test with empty full name
    user_data = {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "full_name": ""
    }
    
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 422