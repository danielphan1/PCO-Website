"""Unit tests for the email service (XCUT-04).

Verifies that:
  1. After POST /v1/admin/users, the welcome email is queued as a BackgroundTask
     (not sent inline — HTTP response is returned first).
  2. SMTP failure inside send_welcome_email does not propagate as an exception.
"""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from app.services import email_service


def test_send_welcome_email_called(auth_client):
    """After POST /v1/admin/users, assert background_tasks.add_task was invoked
    with send_welcome_email as the target.

    Strategy: patch BackgroundTasks.add_task so we can inspect calls, then
    POST a new member and confirm add_task was called with the email function.
    """
    from fastapi import BackgroundTasks

    from app.services.email_service import send_welcome_email

    called_with = []

    original_add_task = BackgroundTasks.add_task

    def capturing_add_task(self, func, *args, **kwargs):
        called_with.append((func, args, kwargs))
        # Do not actually schedule the task — just record it

    with patch.object(BackgroundTasks, "add_task", capturing_add_task):
        resp = auth_client.post(
            "/v1/auth/login",
            data={"username": "admin@test.com", "password": "admin-password"},
        )
        assert resp.status_code == 200
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        create_resp = auth_client.post(
            "/v1/admin/users/",
            json={
                "email": "emailtest@test.com",
                "full_name": "Email Test",
                "role": "member",
            },
            headers=headers,
        )
        assert create_resp.status_code == 201

    # Verify add_task was called with send_welcome_email
    assert len(called_with) >= 1, "add_task was never called"
    funcs = [c[0] for c in called_with]
    assert send_welcome_email in funcs, (
        f"send_welcome_email not found in add_task calls; got: {funcs}"
    )


def test_smtp_failure_does_not_propagate():
    """send_welcome_email logs the error and does not raise when SMTP fails."""
    with patch("aiosmtplib.send", new_callable=AsyncMock, side_effect=Exception("SMTP down")):
        # Should complete without raising
        asyncio.run(
            email_service.send_welcome_email(
                to_email="anyone@example.com",
                full_name="Test User",
                temp_password="tempPw123",
            )
        )
        # If we reach here, the exception was swallowed correctly
