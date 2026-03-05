from supabase import Client, create_client

from app.core.config import settings

BUCKET = "events"

_client: Client | None = None


def _get_client() -> Client:
    global _client
    if _client is None:
        if not settings.supabase_url:
            raise RuntimeError("Supabase credentials not configured")
        _client = create_client(settings.supabase_url, settings.supabase_service_key)
    return _client


class StorageService:
    def upload(self, path: str, data: bytes, content_type: str = "application/pdf") -> None:
        _get_client().storage.from_(BUCKET).upload(
            path=path,
            file=data,
            file_options={"content-type": content_type, "upsert": "false"},
        )

    def create_signed_url(self, path: str, expires_in: int = 3600) -> str | None:
        try:
            result = _get_client().storage.from_(BUCKET).create_signed_url(path, expires_in)
            return result.get("signedURL")
        except Exception:
            return None

    def remove(self, path: str) -> None:
        _get_client().storage.from_(BUCKET).remove([path])


storage_service = StorageService()
