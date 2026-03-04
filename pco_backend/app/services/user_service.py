"""Member management service layer.

All database mutations write an AuditLog row atomically in the same commit.
Deactivation also revokes all active refresh tokens for the target user.
"""

import secrets
import string
import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.audit_log import AuditLog
from app.models.refresh_token import RefreshToken
from app.models.user import ALL_ROLES, User
from app.schemas.user import MemberCreate

_TEMP_PW_CHARS = string.ascii_letters + string.digits
_TEMP_PW_LEN = 12


def _generate_temp_password() -> str:
    return "".join(secrets.choice(_TEMP_PW_CHARS) for _ in range(_TEMP_PW_LEN))


def list_members(db: Session, active_only: bool | None = None) -> list[User]:
    """Return all users, optionally filtered by is_active."""
    q = db.query(User)
    if active_only is True:
        q = q.filter(User.is_active.is_(True))
    elif active_only is False:
        q = q.filter(User.is_active.is_(False))
    return q.all()


def create_member(db: Session, payload: MemberCreate, actor: User) -> tuple[User, str]:
    """Create a new member, write audit log, and return (user, temp_password).

    Raises:
        409 — email already in use
    """
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A member with that email already exists.",
        )

    temp_pw = _generate_temp_password()
    new_user = User(
        email=payload.email,
        full_name=payload.full_name,
        role=payload.role,
        hashed_password=hash_password(temp_pw),
        is_active=True,
    )
    db.add(new_user)
    db.flush()  # populate new_user.id before audit log

    audit = AuditLog(
        actor_id=actor.id,
        action="member.created",
        target_id=new_user.id,
        target_type="user",
    )
    db.add(audit)
    db.commit()
    db.refresh(new_user)
    return new_user, temp_pw


def update_member_role(
    db: Session, user_id: uuid.UUID, new_role: str, actor: User
) -> User:
    """Update a member's role and write audit log.

    Raises:
        404 — user not found
        422 — invalid role value
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found.",
        )

    if new_role not in ALL_ROLES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid role '{new_role}'. Must be one of: {ALL_ROLES}",
        )

    user.role = new_role
    audit = AuditLog(
        actor_id=actor.id,
        action="member.role_updated",
        target_id=user.id,
        target_type="user",
        extra_data={"new_role": new_role},
    )
    db.add(audit)
    db.commit()
    db.refresh(user)
    return user


def deactivate_member(db: Session, user_id: uuid.UUID, actor: User) -> User:
    """Set is_active=False, revoke all active refresh tokens, write audit log.

    Raises:
        404 — user not found
        409 — user already deactivated
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Member already deactivated.",
        )

    user.is_active = False

    # Revoke all active refresh tokens for this user
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.revoked.is_(False),
    ).update({"revoked": True}, synchronize_session="fetch")

    audit = AuditLog(
        actor_id=actor.id,
        action="member.deactivated",
        target_id=user.id,
        target_type="user",
    )
    db.add(audit)
    db.commit()
    db.refresh(user)
    return user


def reactivate_member(db: Session, user_id: uuid.UUID, actor: User) -> User:
    """Set is_active=True and write audit log.

    Raises:
        404 — user not found
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found.",
        )

    user.is_active = True
    audit = AuditLog(
        actor_id=actor.id,
        action="member.reactivated",
        target_id=user.id,
        target_type="user",
    )
    db.add(audit)
    db.commit()
    db.refresh(user)
    return user
