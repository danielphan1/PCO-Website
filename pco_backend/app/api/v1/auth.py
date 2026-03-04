"""Authentication endpoints — login and refresh token rotation.

POST /v1/auth/login  → returns access + refresh tokens
POST /v1/auth/refresh → rotates refresh token, returns new access + refresh tokens
"""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_db
from app.core.security import (
    _dummy_verify,
    create_access_token,
    generate_refresh_token,
    hash_refresh_token,
    verify_password,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Authenticate with email + password. Returns access token and refresh token."""
    user = db.query(User).filter(User.email == payload.email).first()

    # Always run a bcrypt verify to prevent timing-based user enumeration.
    if user is None:
        _dummy_verify()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    password_ok = verify_password(payload.password, user.hashed_password)
    if not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    raw_token = generate_refresh_token()
    token_hash = hash_refresh_token(raw_token)
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)

    db_token = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    db.add(db_token)
    db.commit()

    access_token = create_access_token(subject=str(user.id), role=user.role)
    return TokenResponse(
        access_token=access_token,
        refresh_token=raw_token,
        token_type="bearer",
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Exchange a valid refresh token for new access + refresh tokens (rotation).

    DB write order: insert new row first, then mark old row revoked.
    If the DB fails mid-way, the client retains the old (still-valid) token.
    """
    token_hash = hash_refresh_token(payload.refresh_token)
    db_token = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()

    now = datetime.now(timezone.utc)

    if db_token is None or db_token.revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # Handle timezone-aware vs naive comparison safely
    expires_at = db_token.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < now:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user = db_token.user
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    # Insert new token row BEFORE revoking old one
    new_raw = generate_refresh_token()
    new_hash = hash_refresh_token(new_raw)
    new_expires = now + timedelta(days=settings.refresh_token_expire_days)
    new_db_token = RefreshToken(user_id=user.id, token_hash=new_hash, expires_at=new_expires)
    db.add(new_db_token)

    # Revoke old token
    db_token.revoked = True
    db.commit()

    access_token = create_access_token(subject=str(user.id), role=user.role)
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_raw,
        token_type="bearer",
    )
