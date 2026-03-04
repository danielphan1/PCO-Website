"""Interest form endpoints.

POST /  — Public; submit an interest form and queue a confirmation email.
GET  /  — Admin only; list all interest form submissions.
"""

from typing import Annotated, List

from fastapi import APIRouter, BackgroundTasks, Depends

from app.core.deps import get_db, require_admin
from app.schemas.interest_form import InterestFormCreate, InterestFormResponse
from app.services import email_service, interest_service
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/", response_model=InterestFormResponse, status_code=201)
def submit_interest_form(
    payload: InterestFormCreate,
    background_tasks: BackgroundTasks,
    db: Annotated[Session, Depends(get_db)],
):
    """Submit an interest form. Queues a confirmation email non-blocking."""
    submission = interest_service.submit_interest(db, payload)
    background_tasks.add_task(
        email_service.send_interest_confirmation,
        submission.email,
        submission.name,
    )
    return submission


@router.get("/", response_model=List[InterestFormResponse])
def list_interest(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_admin)],
):
    """List all interest form submissions. Admin only."""
    return interest_service.list_submissions(db)
