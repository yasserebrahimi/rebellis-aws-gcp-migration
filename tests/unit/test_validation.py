import pytest
from pydantic import ValidationError
from src.api.schemas.auth import UserCreate, UserLogin
from src.api.schemas.transcription import TranscriptionRequest


def test_user_create_valid():
    """Test valid user creation"""
    user_data = UserCreate(
        email="test@example.com",
        password="TestPassword123!",
        full_name="Test User"
    )
    
    assert user_data.email == "test@example.com"
    assert user_data.password == "TestPassword123!"
    assert user_data.full_name == "Test User"


def test_user_create_invalid_password_no_uppercase():
    """Test user creation with password missing uppercase letter"""
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            email="test@example.com",
            password="testpassword123!",
            full_name="Test User"
        )
    
    assert "uppercase letter" in str(exc_info.value)


def test_user_create_invalid_password_no_lowercase():
    """Test user creation with password missing lowercase letter"""
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            email="test@example.com",
            password="TESTPASSWORD123!",
            full_name="Test User"
        )
    
    assert "lowercase letter" in str(exc_info.value)


def test_user_create_invalid_password_no_digit():
    """Test user creation with password missing digit"""
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            email="test@example.com",
            password="TestPassword!",
            full_name="Test User"
        )
    
    assert "digit" in str(exc_info.value)


def test_user_create_invalid_password_no_special_char():
    """Test user creation with password missing special character"""
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            email="test@example.com",
            password="TestPassword123",
            full_name="Test User"
        )
    
    assert "special character" in str(exc_info.value)


def test_user_create_invalid_password_too_short():
    """Test user creation with password too short"""
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            email="test@example.com",
            password="Test1!",
            full_name="Test User"
        )
    
    assert "at least 8 characters" in str(exc_info.value)


def test_user_create_invalid_full_name_empty():
    """Test user creation with empty full name"""
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            email="test@example.com",
            password="TestPassword123!",
            full_name=""
        )
    
    assert "cannot be empty" in str(exc_info.value)


def test_user_create_invalid_full_name_whitespace():
    """Test user creation with whitespace-only full name"""
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            email="test@example.com",
            password="TestPassword123!",
            full_name="   "
        )
    
    assert "cannot be empty" in str(exc_info.value)


def test_user_create_full_name_trimmed():
    """Test that full name is properly trimmed"""
    user_data = UserCreate(
        email="test@example.com",
        password="TestPassword123!",
        full_name="  Test User  "
    )
    
    assert user_data.full_name == "Test User"


def test_user_login_valid():
    """Test valid user login"""
    login_data = UserLogin(
        email="test@example.com",
        password="TestPassword123!"
    )
    
    assert login_data.email == "test@example.com"
    assert login_data.password == "TestPassword123!"


def test_transcription_request_valid():
    """Test valid transcription request"""
    request = TranscriptionRequest(
        language="en",
        return_timestamps=True,
        return_segments=True
    )
    
    assert request.language == "en"
    assert request.return_timestamps is True
    assert request.return_segments is True


def test_transcription_request_auto_language():
    """Test transcription request with auto language"""
    request = TranscriptionRequest(language="auto")
    
    assert request.language == "auto"


def test_transcription_request_invalid_language():
    """Test transcription request with invalid language code"""
    with pytest.raises(ValidationError) as exc_info:
        TranscriptionRequest(language="english")
    
    assert "2-letter language code" in str(exc_info.value)