from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    env: str = "dev"
    app_name: str = "psi-chi-omega-api"
    app_version: str = "0.1.0"
    cors_origins: str = "http://localhost:3000"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/pco"
    jwt_secret: str  # NO default — required field
    jwt_alg: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30
    supabase_url: str = ""
    supabase_service_key: str = ""
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""

    @field_validator("jwt_secret", mode="after")
    @classmethod
    def jwt_secret_min_length(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError(f"JWT_SECRET must be at least 32 characters. Got {len(v)}.")
        return v

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()  # Fails at import time if JWT_SECRET missing or too short
