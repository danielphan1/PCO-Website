from fastapi import APIRouter

from app.api.v1 import auth, events, interest, public
from app.api.v1.admin import events as admin_events
from app.api.v1.admin import settings as admin_settings
from app.api.v1.admin import users as admin_users

router = APIRouter()
router.include_router(public.router, prefix="/v1/public", tags=["public"])
router.include_router(interest.router, prefix="/v1/interest", tags=["interest"])
router.include_router(events.router, prefix="/v1/events", tags=["events"])
router.include_router(auth.router, prefix="/v1/auth", tags=["auth"])

router.include_router(admin_users.router, prefix="/v1/admin/users", tags=["admin-users"])
router.include_router(admin_events.router, prefix="/v1/admin/events", tags=["admin-events"])
router.include_router(admin_settings.router, prefix="/v1/admin/settings", tags=["admin-settings"])
