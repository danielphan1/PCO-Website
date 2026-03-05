import uuid
from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from app.models.event_pdf import EventPDF
from app.services.event_service import upload_event

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_tokens(auth_client):
    """Return (member_token, admin_token) by logging in with each account."""
    member_resp = auth_client.post(
        "/v1/auth/login",
        json={"email": "active@test.com", "password": "correct-password"},
    )
    admin_resp = auth_client.post(
        "/v1/auth/login",
        json={"email": "admin@test.com", "password": "admin-password"},
    )
    return member_resp.json()["access_token"], admin_resp.json()["access_token"]


def make_pdf_bytes(size: int = 100) -> bytes:
    """Return synthetic PDF bytes that pass magic-byte validation."""
    return b"%PDF" + b"x" * (size - 4)


def seed_event(db_session) -> EventPDF:
    """Insert one EventPDF row directly and return it."""
    event = EventPDF(
        id=uuid.uuid4(),
        title="Test Event",
        date=date(2024, 1, 15),
        storage_path="events/test.pdf",
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    return event


# ---------------------------------------------------------------------------
# Tests: list events (EVNT-01)
# ---------------------------------------------------------------------------


def test_list_events_unauthenticated(auth_client):
    resp = auth_client.get("/v1/events/")
    assert resp.status_code == 401


def test_list_events_member(auth_client, db_session):
    member_token, _ = get_tokens(auth_client)
    event = seed_event(db_session)

    mock_storage = MagicMock()
    mock_storage.create_signed_url.return_value = "https://signed.url/file.pdf"

    with patch("app.services.event_service.storage_service", mock_storage):
        resp = auth_client.get(
            "/v1/events/",
            headers={"Authorization": f"Bearer {member_token}"},
        )

    assert resp.status_code == 200
    events = resp.json()
    assert isinstance(events, list)
    assert len(events) >= 1
    item = next((e for e in events if e["id"] == str(event.id)), None)
    assert item is not None
    assert item["title"] == "Test Event"
    assert "date" in item
    assert item["url"] == "https://signed.url/file.pdf"


def test_list_events_url_failure_graceful(auth_client, db_session):
    """Signed URL failure for one event returns url: null; list still 200."""
    member_token, _ = get_tokens(auth_client)
    event = seed_event(db_session)

    mock_storage = MagicMock()
    mock_storage.create_signed_url.return_value = None  # simulate failure

    with patch("app.services.event_service.storage_service", mock_storage):
        resp = auth_client.get(
            "/v1/events/",
            headers={"Authorization": f"Bearer {member_token}"},
        )

    assert resp.status_code == 200
    events = resp.json()
    item = next((e for e in events if e["id"] == str(event.id)), None)
    assert item is not None
    assert item["url"] is None


# ---------------------------------------------------------------------------
# Tests: upload event (EVNT-02)
# ---------------------------------------------------------------------------


def test_upload_non_admin_forbidden(auth_client):
    member_token, _ = get_tokens(auth_client)
    resp = auth_client.post(
        "/v1/admin/events/",
        files={"file": ("test.pdf", make_pdf_bytes(), "application/pdf")},
        data={"title": "Event", "date": "2024-06-01"},
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert resp.status_code == 403


def test_upload_non_pdf_rejected(auth_client):
    _, admin_token = get_tokens(auth_client)
    not_pdf = b"NOTAPDF" + b"x" * 100

    mock_storage = MagicMock()
    with patch("app.services.event_service.storage_service", mock_storage):
        resp = auth_client.post(
            "/v1/admin/events/",
            files={"file": ("bad.pdf", not_pdf, "application/pdf")},
            data={"title": "Bad Event", "date": "2024-06-01"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

    assert resp.status_code == 422


def test_upload_oversized_rejected(auth_client):
    _, admin_token = get_tokens(auth_client)
    oversized = make_pdf_bytes(size=10 * 1024 * 1024 + 1)

    mock_storage = MagicMock()
    with patch("app.services.event_service.storage_service", mock_storage):
        resp = auth_client.post(
            "/v1/admin/events/",
            files={"file": ("big.pdf", oversized, "application/pdf")},
            data={"title": "Big Event", "date": "2024-06-01"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

    assert resp.status_code == 413


def test_upload_pdf_success(auth_client):
    _, admin_token = get_tokens(auth_client)

    mock_storage = MagicMock()
    mock_storage.upload.return_value = None
    mock_storage.create_signed_url.return_value = "https://signed.url/file.pdf"

    with patch("app.services.event_service.storage_service", mock_storage):
        resp = auth_client.post(
            "/v1/admin/events/",
            files={"file": ("test.pdf", make_pdf_bytes(), "application/pdf")},
            data={"title": "New Event", "date": "2024-07-04"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

    assert resp.status_code == 201
    body = resp.json()
    assert "id" in body
    assert body["title"] == "New Event"
    assert "date" in body
    assert body["url"] == "https://signed.url/file.pdf"


def test_upload_db_failure_triggers_storage_delete(db_session):
    """DB commit failure causes storage rollback (storage.remove is called)."""
    mock_storage = MagicMock()
    mock_storage.upload.return_value = None
    mock_storage.create_signed_url.return_value = None

    original_commit = db_session.commit
    call_count = [0]

    def failing_commit():
        call_count[0] += 1
        raise Exception("DB failure")

    db_session.commit = failing_commit
    try:
        with patch("app.services.event_service.storage_service", mock_storage):
            with pytest.raises(Exception):
                upload_event(
                    db=db_session,
                    title="Rollback Test",
                    event_date=date(2024, 8, 1),
                    data=make_pdf_bytes(),
                    uploader_id=uuid.uuid4(),
                )
    finally:
        db_session.commit = original_commit
        db_session.rollback()

    mock_storage.remove.assert_called_once()


# ---------------------------------------------------------------------------
# Tests: delete event (EVNT-03)
# ---------------------------------------------------------------------------


def test_delete_event_not_found(auth_client):
    _, admin_token = get_tokens(auth_client)
    nonexistent_id = uuid.uuid4()

    mock_storage = MagicMock()
    with patch("app.services.event_service.storage_service", mock_storage):
        resp = auth_client.delete(
            f"/v1/admin/events/{nonexistent_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

    assert resp.status_code == 404


def test_delete_event_success(auth_client, db_session):
    _, admin_token = get_tokens(auth_client)
    event = seed_event(db_session)
    event_id = event.id

    mock_storage = MagicMock()
    mock_storage.remove.return_value = None

    with patch("app.services.event_service.storage_service", mock_storage):
        resp = auth_client.delete(
            f"/v1/admin/events/{event_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

    assert resp.status_code == 200
    gone = db_session.query(EventPDF).filter(EventPDF.id == event_id).first()
    assert gone is None


def test_delete_event_storage_failure_still_succeeds(auth_client, db_session):
    _, admin_token = get_tokens(auth_client)
    event = seed_event(db_session)
    event_id = event.id

    mock_storage = MagicMock()
    mock_storage.remove.side_effect = Exception("Storage unavailable")

    with patch("app.services.event_service.storage_service", mock_storage):
        resp = auth_client.delete(
            f"/v1/admin/events/{event_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

    assert resp.status_code == 200
    gone = db_session.query(EventPDF).filter(EventPDF.id == event_id).first()
    assert gone is None
