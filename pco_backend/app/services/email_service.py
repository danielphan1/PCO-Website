"""Email service for sending transactional emails via SMTP.

All send functions are async and swallow SMTP errors — callers get a response
immediately without waiting for delivery and without propagating send failures.
"""

import logging
from email.message import EmailMessage

import aiosmtplib

from app.core.config import settings

logger = logging.getLogger(__name__)


async def send_welcome_email(to_email: str, full_name: str, temp_password: str) -> None:
    """Send a welcome email with temporary credentials to a newly created member.

    SMTP failures are logged and swallowed so the HTTP response is not affected.
    """
    msg = EmailMessage()
    msg["From"] = settings.smtp_user
    msg["To"] = to_email
    msg["Subject"] = "Welcome to Psi Chi Omega!"
    msg.set_content(
        f"Hi {full_name},\n\n"
        "Welcome to Psi Chi Omega! Your member account has been created.\n\n"
        f"Email: {to_email}\n"
        f"Temporary Password: {temp_password}\n\n"
        f"Please log in and change your password: {settings.frontend_url}/login\n\n"
        "Best,\nPsi Chi Omega"
    )

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user,
            password=settings.smtp_password,
            start_tls=True,
        )
    except Exception as exc:
        logger.error("Failed to send welcome email to %s: %s", to_email, exc)


async def send_interest_confirmation(to_email: str, full_name: str) -> None:
    """Send a confirmation email to a prospective member who submitted an interest form.

    SMTP failures are logged and swallowed so the HTTP response is not affected.
    """
    msg = EmailMessage()
    msg["From"] = settings.smtp_user
    msg["To"] = to_email
    msg["Subject"] = "Interest Form Received — Psi Chi Omega"
    msg.set_content(
        f"Hi {full_name},\n\n"
        "We received your interest form and will reach out soon.\n\n"
        "Thank you for your interest in Psi Chi Omega!\n\n"
        "Best,\nPsi Chi Omega"
    )

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user,
            password=settings.smtp_password,
            start_tls=True,
        )
    except Exception as exc:
        logger.error("Failed to send interest confirmation to %s: %s", to_email, exc)
