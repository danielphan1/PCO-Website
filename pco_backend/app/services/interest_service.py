"""Service layer for interest form submissions."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.interest_form import InterestSubmission
from app.schemas.interest_form import InterestFormCreate


def submit_interest(db: Session, payload: InterestFormCreate) -> InterestSubmission:
    """Create a new interest form submission.

    Raises:
        409 — if an entry with the same email already exists
    """
    existing = db.query(InterestSubmission).filter(InterestSubmission.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already submitted",
        )
    obj = InterestSubmission(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_submissions(db: Session) -> list[InterestSubmission]:
    """Return all interest form submissions."""
    return db.query(InterestSubmission).all()
