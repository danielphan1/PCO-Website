from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    env: str = "dev"
    app_name: str = "psi-chi-omega-api"
    cors_origins: str = "http://localhost:3000"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/pco"
    jwt_secret: str = "change-me"
    jwt_alg: str = "HS256"
    access_token_expire_minutes: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
