import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict


class EventCreate(BaseModel):
    title: str
    date: date


class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    date: date
    url: str | None
