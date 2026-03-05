import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_admin
from app.services.event_service import delete_event, upload_event

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_event_endpoint(
    file: Annotated[UploadFile, File()],
    title: Annotated[str, Form()],
    date: Annotated[date, Form()],
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    data = await file.read()
    event, url = upload_event(
        db=db,
        title=title,
        event_date=date,
        data=data,
        uploader_id=current_user.id,
    )
    return {
        "id": str(event.id),
        "title": event.title,
        "date": str(event.date),
        "url": url,
    }


@router.delete("/{event_id}", status_code=status.HTTP_200_OK)
def delete_event_endpoint(
    event_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    delete_event(db=db, event_id=event_id)
    return {"deleted": True, "event_id": str(event_id)}
