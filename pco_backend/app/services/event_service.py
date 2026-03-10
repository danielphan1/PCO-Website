import logging
import uuid
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.event_pdf import EventPDF
from app.storage.files import storage_service
from app.storage.paths import event_pdf_path

MAX_SIZE_BYTES = 10 * 1024 * 1024
logger = logging.getLogger(__name__)


def list_events(db: Session) -> list[dict]:
    events = db.query(EventPDF).order_by(EventPDF.date.desc()).all()
    result = []
    for event in events:
        url = storage_service.create_signed_url(event.storage_path, expires_in=3600)
        result.append(
            {
                "id": str(event.id),
                "title": event.title,
                "date": str(event.date),
                "signed_url": url,
            }
        )
    return result


def upload_event(
    db: Session,
    title: str,
    event_date: date,
    data: bytes,
    uploader_id: uuid.UUID,
) -> tuple[EventPDF, str | None]:
    if len(data) > MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File exceeds 10 MB limit.",
        )
    if data[:4] != b"%PDF":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="File is not a valid PDF (missing %PDF header).",
        )

    event_id = uuid.uuid4()
    path = event_pdf_path(event_id)

    storage_service.upload(path, data)

    try:
        event = EventPDF(
            id=event_id,
            title=title,
            date=event_date,
            storage_path=path,
            uploaded_by=uploader_id,
        )
        db.add(event)
        db.commit()
        db.refresh(event)
    except Exception:
        try:
            storage_service.remove(path)
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save event record.",
        )

    url = storage_service.create_signed_url(path, expires_in=3600)
    return event, url


def delete_event(db: Session, event_id: uuid.UUID) -> None:
    event = db.query(EventPDF).filter(EventPDF.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found.")

    try:
        storage_service.remove(event.storage_path)
    except Exception as exc:
        logger.warning("Storage removal failed for %s: %s", event.storage_path, exc)

    db.delete(event)
    db.commit()
