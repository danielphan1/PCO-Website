"""Pydantic schemas for rush info."""

import uuid
from datetime import datetime

from pydantic import BaseModel


class RushInfoUpdate(BaseModel):
    dates: str
    times: str
    locations: str
    description: str


class RushInfoResponse(BaseModel):
    id: uuid.UUID
    dates: str
    times: str
    locations: str
    description: str
    is_published: bool
    updated_at: datetime

    model_config = {"from_attributes": True}
