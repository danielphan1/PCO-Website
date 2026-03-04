"""Pydantic schemas for org content endpoints."""

from pydantic import BaseModel


class ContentUpdate(BaseModel):
    content: str


class ContentResponse(BaseModel):
    section: str
    content: str


class LeadershipEntry(BaseModel):
    full_name: str
    role: str
