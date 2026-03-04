from fastapi import APIRouter

from app.api.v1.interest import STATE

router = APIRouter()


@router.post("/interest/open")
def open_interest():
    STATE["open"] = True
    return STATE


@router.post("/interest/close")
def close_interest():
    STATE["open"] = False
    return STATE
