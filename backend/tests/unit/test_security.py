"""Test security functions"""
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token
)

def test_password_hashing():
    """Test password hashing works"""
    password = "TestPassword123!"
    hashed = get_password_hash(password)
    
    # Hash should be different from password
    assert hashed != password
    
    # Verification should succeed
    assert verify_password(password, hashed) is True
    
    # Wrong password should fail
    assert verify_password("WrongPassword", hashed) is False

def test_jwt_token_creation_and_decoding():
    """Test JWT token creation and decoding"""
    token_data = {"sub": "testuser", "role": "ADMIN"}
    token = create_access_token(data=token_data)
    
    # Token should be a string
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Decode token
    decoded = decode_access_token(token)
    
    # Data should match
    assert decoded is not None
    assert decoded.username == "testuser"
    assert decoded.role == "ADMIN"

def test_invalid_token_decoding():
    """Test decoding invalid token returns None"""
    invalid_token = "invalid.token.here"
    decoded = decode_access_token(invalid_token)
    
    # Should return None for invalid token
    assert decoded is None
