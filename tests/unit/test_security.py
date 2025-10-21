import pytest
from src.core.security import create_token, verify_token
from src.core.config import settings


def test_create_token():
    """Test JWT token creation"""
    data = {"sub": "123", "email": "test@example.com"}
    token = create_token(data)
    
    assert isinstance(token, str)
    assert len(token) > 0


def test_verify_token_valid():
    """Test verification of valid token"""
    data = {"sub": "123", "email": "test@example.com"}
    token = create_token(data)
    
    payload = verify_token(token)
    
    assert payload["sub"] == "123"
    assert payload["email"] == "test@example.com"
    assert "exp" in payload


def test_verify_token_invalid():
    """Test verification of invalid token"""
    with pytest.raises(ValueError, match="Invalid token"):
        verify_token("invalid.token.here")


def test_verify_token_expired():
    """Test verification of expired token"""
    from datetime import datetime, timedelta
    
    # Create token with very short expiration
    data = {"sub": "123", "email": "test@example.com"}
    token = create_token(data, expires_delta=timedelta(seconds=-1))
    
    with pytest.raises(ValueError, match="Token expired"):
        verify_token(token)


def test_token_expiration():
    """Test that tokens have proper expiration"""
    data = {"sub": "123", "email": "test@example.com"}
    token = create_token(data)
    
    payload = verify_token(token)
    
    # Check that expiration is set and reasonable
    assert "exp" in payload
    exp_time = payload["exp"]
    
    # Should be in the future (within 24 hours)
    from datetime import datetime
    current_time = datetime.utcnow().timestamp()
    assert exp_time > current_time
    assert exp_time < current_time + 25 * 3600  # Less than 25 hours