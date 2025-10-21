from src.core.config import Settings

def test_cors_parse_and_defaults():
    s = Settings()
    assert s.APP_NAME == "Rebellis Infrastructure"
    assert isinstance(s.APP_PORT, int)
    assert s.JWT_ALGORITHM == "HS256"
    s2 = Settings(CORS_ORIGINS="http://a.com,http://b.com")
    assert s2.CORS_ORIGINS == ["http://a.com","http://b.com"]
