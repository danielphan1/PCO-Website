"""Security utilities — JWT and bcrypt helpers.

Uses PyJWT (pyjwt>=2.8) for JWT encode/decode.
Uses bcrypt directly (NOT passlib — passlib 1.7.4 + bcrypt 5.0.0 is broken).
"""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from jwt.exceptions import InvalidTokenError  # noqa: F401 — re-exported for deps.py

from app.core.config import settings

# Precomputed dummy hash to prevent timing attacks on login when user is not found.
# Computed once at module load time; bcrypt.gensalt() is intentionally slow.
_DUMMY_HASH: str = bcrypt.hashpw(b"dummy-timing-padding", bcrypt.gensalt()).decode("utf-8")


# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------


def create_access_token(subject: str, role: str) -> str:
    """Encode a short-lived access JWT. subject must be the user UUID as a str."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": subject,
        "role": role,
        "exp": expire,
        "iat": now,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_alg)


def decode_access_token(token: str) -> dict:
    """Decode and verify an access JWT.

    Raises jwt.ExpiredSignatureError or jwt.InvalidTokenError on failure.
    Callers should catch jwt.InvalidTokenError (which ExpiredSignatureError subclasses).
    """
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_alg])


# ---------------------------------------------------------------------------
# Passwords — bcrypt direct (NOT via passlib)
# ---------------------------------------------------------------------------


def hash_password(plain: str) -> str:
    """Hash a plaintext password with bcrypt. Returns a $2b$-prefixed string."""
    hashed_bytes = bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt())
    return hashed_bytes.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Constant-time bcrypt comparison. Returns True if plain matches hashed."""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def _dummy_verify() -> None:
    """Run a verify against the dummy hash. Consumes the same time as a real verify.

    Call this when the user is not found so timing is indistinguishable from a real verify.
    """
    bcrypt.checkpw(b"dummy-timing-padding", _DUMMY_HASH.encode("utf-8"))


# ---------------------------------------------------------------------------
# Refresh tokens
# ---------------------------------------------------------------------------


def generate_refresh_token() -> str:
    """Return a cryptographically secure URL-safe random token (raw value for the client)."""
    return secrets.token_urlsafe(32)


def hash_refresh_token(raw_token: str) -> str:
    """SHA-256 hex digest of the raw token. This value is stored in the DB.

    SHA-256 is appropriate here (not bcrypt) because the token has 256 bits of entropy —
    brute-force pre-image attacks are not feasible.
    """
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
