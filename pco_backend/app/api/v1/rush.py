"""Rush info endpoints.

GET   /            — Public; returns coming_soon or full rush info when published.
PUT   /            — Admin only; upserts rush info content.
PATCH /visibility  — Admin only; toggles is_published flag.
"""

from typing import Annotated, Union

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_admin
from app.schemas.rush import RushInfoResponse, RushInfoUpdate
from app.services import rush_service

router = APIRouter()


@router.get("/")
def get_rush_info(
    db: Annotated[Session, Depends(get_db)],
) -> Union[RushInfoResponse, dict]:
    """Return rush info if published; otherwise return coming_soon status."""
    rush = rush_service.get_rush(db)
    if rush is None or not rush.is_published:
        return {"status": "coming_soon"}
    return RushInfoResponse.model_validate(rush)


@router.put("/", response_model=RushInfoResponse)
def update_rush_info(
    payload: RushInfoUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_admin)],
) -> RushInfoResponse:
    """Upsert rush info content. Admin only."""
    rush = rush_service.upsert_rush(db, payload)
    return RushInfoResponse.model_validate(rush)


@router.patch("/visibility", response_model=RushInfoResponse)
def toggle_rush_visibility(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_admin)],
) -> RushInfoResponse:
    """Toggle is_published flag on rush info. Admin only."""
    rush = rush_service.toggle_visibility(db)
    return RushInfoResponse.model_validate(rush)
