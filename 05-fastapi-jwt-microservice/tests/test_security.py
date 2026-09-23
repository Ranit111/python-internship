"""
Unit tests for cryptographic security utilities.
"""

from datetime import timedelta
from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)


def test_password_hashing_and_verification():
    raw_pass = "SecureP@ssw0rd!2026"
    hashed = get_password_hash(raw_pass)

    assert hashed != raw_pass
    assert verify_password(raw_pass, hashed) is True
    assert verify_password("WrongPassword", hashed) is False
    assert verify_password("", hashed) is False


def test_jwt_token_lifecycle():
    user_id = 42
    token = create_access_token(user_id)
    assert isinstance(token, str)

    decoded_id = decode_access_token(token)
    assert decoded_id == str(user_id)


def test_expired_token_handling():
    user_id = 99
    # Create token expired 1 minute ago
    expired_token = create_access_token(user_id, expires_delta=timedelta(minutes=-1))
    decoded = decode_access_token(expired_token)
    assert decoded is None
