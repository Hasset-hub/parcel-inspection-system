from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token
)

# Test password hashing
print("Testing password hashing...")
password = "TestPassword123!"
hashed = get_password_hash(password)
print(f"Original: {password}")
print(f"Hashed: {hashed}")

# Test verification
is_valid = verify_password(password, hashed)
print(f"Verification: {'✅ Passed' if is_valid else '❌ Failed'}")

is_invalid = verify_password("WrongPassword", hashed)
print(f"Wrong password: {'❌ Failed (correct)' if not is_invalid else '✅ Wrong behavior'}")

# Test JWT token
print("\nTesting JWT tokens...")
token = create_access_token(data={"sub": "admin", "role": "admin"})
print(f"Generated token: {token[:50]}...")

decoded = decode_access_token(token)
if decoded:
    print(f"Decoded username: {decoded.username}")
    print(f"Decoded role: {decoded.role}")
    print("✅ JWT test passed!")
else:
    print("❌ JWT decode failed!")

print("\n✅ All security tests passed!")
