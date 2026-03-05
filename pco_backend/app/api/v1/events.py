from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.services.event_service import list_events

router = APIRouter()


@router.get("/", response_model=list[dict])
def get_events(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),  # authentication required (EVNT-01)
) -> list[dict]:
    """List all event PDFs with signed download URLs. Sorted by date, newest first."""
    return list_events(db)
