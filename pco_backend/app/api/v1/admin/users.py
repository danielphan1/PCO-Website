from fastapi import APIRouter

router = APIRouter()

@router.post("/")
def create_user(payload: dict):
    # Admin-only (T6)
    return {"created": True, "user": payload}

@router.patch("/{user_id}/role")
def update_role(user_id: int, payload: dict):
    return {"updated": True, "user_id": user_id, "role": payload}
