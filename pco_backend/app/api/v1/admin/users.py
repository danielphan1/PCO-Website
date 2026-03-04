from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.deps import require_admin
from app.models.user import User

router = APIRouter()


@router.get("/")
def list_users(current_user: Annotated[User, Depends(require_admin)]):
    # Phase 3 will implement this fully
    return []


@router.post("/")
def create_user(payload: dict, current_user: Annotated[User, Depends(require_admin)]):
    return {"created": True, "user": payload}


@router.patch("/{user_id}/role")
def update_role(user_id: str, payload: dict, current_user: Annotated[User, Depends(require_admin)]):
    return {"updated": True, "user_id": user_id, "role": payload}
