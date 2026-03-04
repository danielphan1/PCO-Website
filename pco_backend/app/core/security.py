"""Security utilities — JWT helpers for Phase 2.

PyJWT is available (verified by INFRA-01). Phase 2 implements:
  - create_access_token(data: dict, expires_delta: timedelta) -> str
  - decode_access_token(token: str) -> dict
  - hash_password(plain: str) -> str
  - verify_password(plain: str, hashed: str) -> bool

Phase 1 stub — do not add business logic here.
"""
# PyJWT available: import jwt
# passlib[bcrypt] available: from passlib.context import CryptContext
