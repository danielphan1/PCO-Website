"""FastAPI dependency functions.

get_db          — yields a SQLAlchemy Session (established in Phase 1)
get_current_user — validates Bearer JWT, returns active User
require_admin    — gates admin-only routes, returns User if role == "admin"
"""

import uuid
from typing import Annotated, Generator

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import SessionLocal
from app.models.user import User

# ---------------------------------------------------------------------------
# DB session dependency
# ---------------------------------------------------------------------------


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Auth dependencies
# ---------------------------------------------------------------------------

# HTTPBearer shows a simple "Value:" token input in Swagger UI.
bearer_scheme = HTTPBearer()

_credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Validate Bearer JWT and return the authenticated User.

    Raises:
        401 — missing token, malformed token, expired token, user not found
        403 — user account is deactivated
    """
    try:
        payload = decode_access_token(credentials.credentials)
        user_id_str: str | None = payload.get("sub")
        if user_id_str is None:
            raise _credentials_exception
        user_id = uuid.UUID(user_id_str)
    except (jwt.InvalidTokenError, ValueError):
        raise _credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise _credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    return user


def require_admin(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Require the authenticated user to have admin role.

    Raises:
        403 — user does not have admin role
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
