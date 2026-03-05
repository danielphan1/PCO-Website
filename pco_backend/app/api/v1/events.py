from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.services.event_service import list_events

router = APIRouter()


@router.get("/")
def get_events(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return list_events(db)
