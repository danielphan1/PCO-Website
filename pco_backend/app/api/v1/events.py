from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_events():
    # MVP: return list; later: DB entries pointing to stored PDFs
    return {"events": []}
