"""Service layer for rush info management."""

from sqlalchemy.orm import Session

from app.models.rush_info import RushInfo
from app.schemas.rush import RushInfoUpdate


def get_rush(db: Session) -> RushInfo | None:
    """Return the single rush info row, or None if no row exists."""
    return db.query(RushInfo).first()


def upsert_rush(db: Session, payload: RushInfoUpdate) -> RushInfo:
    """Create or update the single rush info row with new content.

    If no row exists, a new row is created. The is_published flag is not changed.
    """
    rush = db.query(RushInfo).first()
    if rush is None:
        rush = RushInfo()
        db.add(rush)
    rush.dates = payload.dates
    rush.times = payload.times
    rush.locations = payload.locations
    rush.description = payload.description
    db.commit()
    db.refresh(rush)
    return rush


def toggle_visibility(db: Session) -> RushInfo:
    """Toggle the is_published flag on the rush info row.

    If no row exists, creates one and sets is_published=True (first toggle = publish).
    """
    rush = db.query(RushInfo).first()
    if rush is None:
        rush = RushInfo()
        db.add(rush)
    rush.is_published = not rush.is_published
    db.commit()
    db.refresh(rush)
    return rush
