from fastapi import APIRouter

router = APIRouter()

# MVP: keep open/closed in memory; Phase 2: DB setting
STATE = {"open": True}


@router.get("/status")
def status():
    return STATE


@router.post("/submit")
def submit_interest(form: dict):
    # MVP: store to DB later; for now just echo
    return {"received": True, "data": form}
