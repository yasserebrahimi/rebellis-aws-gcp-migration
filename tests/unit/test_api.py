"""Unit tests for API endpoints"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from datetime import datetime
from src.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_root_endpoint(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "rebellis" in r.json().get("name","").lower()

def test_health_check(client):
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data and "version" in data

@patch("src.api.routers.auth.authenticate_user")
def test_login_success(mock_auth, client):
    mock_auth.return_value = {"id":1,"email":"test@example.com","is_active":True}
    r = client.post("/api/v1/auth/login", json={"email":"test@example.com","password":"password123"})
    assert r.status_code == 200
    body = r.json()
    assert "access_token" in body and body["token_type"] == "bearer"
