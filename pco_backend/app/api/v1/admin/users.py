"""Member management router — admin-only endpoints.

Registered at /v1/admin/users (prefix set in router.py — do not change here).

Endpoints:
    GET    /                    — list members (filterable by active status)
    POST   /                    — create member (welcome email queued as BackgroundTask)
    PATCH  /{user_id}/role      — update member role
    PATCH  /{user_id}/deactivate — deactivate member (revokes tokens)
    PATCH  /{user_id}/reactivate — reactivate member
"""

import uuid
from typing import Annotated, List

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_admin
from app.models.user import User
from app.schemas.user import MemberCreate, MemberRoleUpdate, UserResponse
from app.services import email_service, user_service

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
def list_users(
    active: bool | None = None,
    current_user: Annotated[User, Depends(require_admin)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """List all members. Optionally filter by is_active status."""
    return user_service.list_members(db, active_only=active)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: MemberCreate,
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Depends(require_admin)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """Create a new member account. Welcome email is queued as a background task."""
    new_user, temp_pw = user_service.create_member(db, payload, current_user)
    background_tasks.add_task(
        email_service.send_welcome_email,
        new_user.email,
        new_user.full_name,
        temp_pw,
    )
    return new_user


@router.patch("/{user_id}/role", response_model=UserResponse)
def update_role(
    user_id: uuid.UUID,
    payload: MemberRoleUpdate,
    current_user: Annotated[User, Depends(require_admin)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """Update a member's role."""
    return user_service.update_member_role(db, user_id, payload.role, current_user)


@router.patch("/{user_id}/deactivate", response_model=UserResponse)
def deactivate_member(
    user_id: uuid.UUID,
    current_user: Annotated[User, Depends(require_admin)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """Deactivate a member and revoke all their refresh tokens."""
    return user_service.deactivate_member(db, user_id, current_user)


@router.patch("/{user_id}/reactivate", response_model=UserResponse)
def reactivate_member(
    user_id: uuid.UUID,
    current_user: Annotated[User, Depends(require_admin)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """Reactivate a previously deactivated member."""
    return user_service.reactivate_member(db, user_id, current_user)
