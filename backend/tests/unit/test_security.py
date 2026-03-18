import pytest
from datetime import timedelta
from jose import jwt

from app.core.config import settings
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token
)

class TestSecurityFunctions:
    def test_hash_is_not_plain_password(self):
        hashed = get_password_hash("mysecretpassword")
        assert hashed != "mysecretpassword"
    
    def test_same_password_gives_different_hashes(self):
        hash1 = get_password_hash("password123")
        hash2 = get_password_hash("password123")
        assert hash1 != hash2
    
    def test_hash_starts_with_argon2_prefix(self):
        hashed = get_password_hash("anypassword")
        assert hashed.startswith("$argon2")

    def test_correct_password_verifies(self):
        hashed = get_password_hash("correct_horse_battery_staple")
        assert verify_password("correct_horse_battery_staple", hashed) is True
    
    def test_wrong_password_fails(self):
        hashed = get_password_hash("correct_password")
        assert verify_password("wrong_password", hashed) is False
    
    def test_empty_string_fails(self):
        hashed = get_password_hash("real_password")
        assert verify_password("", hashed) is False
    
    def test_similar_password_fails(self):
        hashed = get_password_hash("Password123")
        assert verify_password("password123", hashed) is False

    def test_token_has_correct_subject(self):
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        token = create_access_token(subject=user_id)
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        assert payload["sub"] == user_id
    
    def test_token_has_expiry(self):
        token = create_access_token(subject="user-123")
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        assert "exp" in payload