import uuid


def event_pdf_path(event_id: uuid.UUID) -> str:
    """Return relative storage path for an event PDF: events/{uuid}.pdf"""
    return f"events/{event_id}.pdf"
