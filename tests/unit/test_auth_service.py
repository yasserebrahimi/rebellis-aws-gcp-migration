import pytest
from unittest.mock import AsyncMock, MagicMock
from src.services.auth_service import AuthService
from src.api.schemas.auth import UserCreate
from src.models.user import User


@pytest.mark.asyncio
async def test_password_hashing():
    """Test that passwords are properly hashed with bcrypt"""
    service = AuthService(AsyncMock())
    
    password = "TestPassword123!"
    hashed = service._hash(password)
    
    # Hash should be different from original password
    assert hashed != password
    assert len(hashed) > 50  # bcrypt hashes are longer than SHA256
    
    # Should be able to verify the password
    assert service.verify_password(password, hashed)
    assert not service.verify_password("wrong_password", hashed)


@pytest.mark.asyncio
async def test_create_user():
    """Test user creation with proper password hashing"""
    mock_db = AsyncMock()
    service = AuthService(mock_db)
    
    user_data = UserCreate(
        email="test@example.com",
        password="TestPassword123!",
        full_name="Test User"
    )
    
    user = await service.create_user(user_data)
    
    # Check that password was hashed
    assert user.hashed_password != user_data.password
    assert service.verify_password(user_data.password, user.hashed_password)
    assert user.email == user_data.email
    assert user.full_name == user_data.full_name


@pytest.mark.asyncio
async def test_authenticate_user_success():
    """Test successful user authentication"""
    mock_db = AsyncMock()
    service = AuthService(mock_db)
    
    # Create a user with hashed password
    password = "TestPassword123!"
    hashed_password = service._hash(password)
    
    mock_user = User(
        id=1,
        email="test@example.com",
        hashed_password=hashed_password,
        full_name="Test User"
    )
    
    # Mock database query
    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_user
    
    # Test authentication
    result = await service.authenticate_user("test@example.com", password)
    
    assert result is not None
    assert result.email == "test@example.com"


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password():
    """Test authentication with wrong password"""
    mock_db = AsyncMock()
    service = AuthService(mock_db)
    
    password = "TestPassword123!"
    wrong_password = "WrongPassword123!"
    hashed_password = service._hash(password)
    
    mock_user = User(
        id=1,
        email="test@example.com",
        hashed_password=hashed_password,
        full_name="Test User"
    )
    
    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_user
    
    # Test with wrong password
    result = await service.authenticate_user("test@example.com", wrong_password)
    
    assert result is None


@pytest.mark.asyncio
async def test_authenticate_user_not_found():
    """Test authentication with non-existent user"""
    mock_db = AsyncMock()
    service = AuthService(mock_db)
    
    # Mock database query to return None
    mock_db.execute.return_value.scalar_one_or_none.return_value = None
    
    result = await service.authenticate_user("nonexistent@example.com", "password")
    
    assert result is None


@pytest.mark.asyncio
async def test_get_user_by_email():
    """Test getting user by email"""
    mock_db = AsyncMock()
    service = AuthService(mock_db)
    
    mock_user = User(
        id=1,
        email="test@example.com",
        hashed_password="hashed",
        full_name="Test User"
    )
    
    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_user
    
    result = await service.get_user_by_email("test@example.com")
    
    assert result is not None
    assert result.email == "test@example.com"


@pytest.mark.asyncio
async def test_get_user_by_id():
    """Test getting user by ID"""
    mock_db = AsyncMock()
    service = AuthService(mock_db)
    
    mock_user = User(
        id=1,
        email="test@example.com",
        hashed_password="hashed",
        full_name="Test User"
    )
    
    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_user
    
    result = await service.get_user_by_id(1)
    
    assert result is not None
    assert result.id == 1