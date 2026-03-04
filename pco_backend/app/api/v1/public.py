from fastapi import APIRouter

router = APIRouter()


@router.get("/info")
def get_public_info():
    # MVP: return static content; later: load from DB (admin editable)
    return {
        "org": "Psi Chi Omega (San Diego)",
        "history": "TODO",
        "philanthropy": "TODO",
        "join_now_url": "TODO",
        "rush_week": {"dates": "TODO", "details": "TODO"},
        "contact": {"rush_chairs": "TODO", "t6": "TODO"},
    }
