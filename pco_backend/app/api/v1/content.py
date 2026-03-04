"""Content router — GET /{section}, PUT /{section}, GET /leadership."""

from typing import Annotated, List, Literal

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_admin
from app.models.org_content import OrgContent
from app.models.user import OFFICER_ROLES, User
from app.schemas.content import ContentResponse, ContentUpdate, LeadershipEntry

router = APIRouter()

VALID_SECTIONS = {"history", "philanthropy", "contacts"}


@router.get("/leadership", response_model=List[LeadershipEntry])
def get_leadership(db: Annotated[Session, Depends(get_db)]):
    """Return active users with officer roles. Public endpoint — no auth required."""
    officers = (
        db.query(User)
        .filter(User.role.in_(OFFICER_ROLES), User.is_active == True)  # noqa: E712
        .all()
    )
    return [LeadershipEntry(full_name=u.full_name, role=u.role) for u in officers]


@router.get("/{section}", response_model=ContentResponse)
def get_section(
    section: str,
    db: Annotated[Session, Depends(get_db)],
):
    """Return org content for the given section. Public endpoint — no auth required."""
    if section not in VALID_SECTIONS:
        raise HTTPException(status_code=404, detail=f"Section '{section}' not found")
    row = db.query(OrgContent).filter(OrgContent.section == section).first()
    return ContentResponse(section=section, content=row.content if row else "")


@router.put("/{section}", response_model=ContentResponse)
def update_section(
    section: Annotated[Literal["history", "philanthropy", "contacts"], Path(...)],
    payload: ContentUpdate,
    db: Annotated[Session, Depends(get_db)],
    _admin: Annotated[User, Depends(require_admin)],
):
    """Upsert org content for the given section. Admin only."""
    row = db.query(OrgContent).filter(OrgContent.section == section).first()
    if row is None:
        row = OrgContent(section=section)
        db.add(row)
    row.content = payload.content
    db.commit()
    db.refresh(row)
    return ContentResponse(section=row.section, content=row.content)
