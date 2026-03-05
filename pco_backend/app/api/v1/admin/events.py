import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_admin
from app.schemas.event import EventResponse
from app.services.event_service import delete_event, upload_event

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=EventResponse)
async def upload_event_pdf(
    file: Annotated[UploadFile, File()],
    title: Annotated[str, Form()],
    date: Annotated[date, Form()],  # Pydantic parses YYYY-MM-DD automatically
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
) -> EventResponse:
    """Upload a PDF event. Max 10 MB. PDF magic bytes validated. Storage-first write."""
    data = await file.read()  # Must await — UploadFile.read() is a coroutine (Pitfall 7)
    event, url = upload_event(
        db=db,
        title=title,
        event_date=date,
        data=data,
        uploader_id=current_user.id,
    )
    return EventResponse(id=event.id, title=event.title, date=event.date, url=url)


@router.delete("/{event_id}", status_code=status.HTTP_200_OK)
def remove_event(
    event_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
) -> dict:
    """Delete an event PDF. Best-effort storage removal. Always deletes DB record."""
    delete_event(db=db, event_id=event_id)
    return {"deleted": True, "event_id": str(event_id)}
