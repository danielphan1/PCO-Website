"""Pydantic v2 schemas for authentication endpoints."""

from pydantic import BaseModel


class LoginRequest(BaseModel):
    """Request body for POST /v1/auth/login."""

    email: str
    password: str

    model_config = {"str_strip_whitespace": True}


class RefreshRequest(BaseModel):
    """Request body for POST /v1/auth/refresh."""

    refresh_token: str


class TokenResponse(BaseModel):
    """Response body for login and refresh endpoints."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
