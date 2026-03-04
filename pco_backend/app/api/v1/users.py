"""User profile endpoints.

GET /v1/users/me — returns the authenticated user's own profile
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """Return the authenticated user's profile."""
    return current_user
