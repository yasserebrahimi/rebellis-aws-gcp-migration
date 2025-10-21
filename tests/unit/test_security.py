

# ---- merged from test_security_unit.py ----
from src.core.security import create_token, verify_token

def test_token_roundtrip():
    tok = create_token({"sub":"123","email":"u@example.com"})
    payload = verify_token(tok)
    assert payload["sub"] == "123"
    assert payload["email"] == "u@example.com"
