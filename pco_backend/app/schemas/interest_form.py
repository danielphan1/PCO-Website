"""Pydantic schemas for interest form submissions."""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class InterestFormCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    year: str
    major: str


class InterestFormResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    phone: str
    year: str
    major: str
    created_at: datetime

    model_config = {"from_attributes": True}
