import uuid
from typing import Literal

from pydantic import BaseModel, EmailStr

# Build a Literal type from ALL_ROLES for validation
_AllRolesLiteral = Literal[
    "member",
    "admin",
    "president",
    "vp",
    "treasurer",
    "secretary",
    "historian",
]


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    role: str
    is_active: bool

    model_config = {"from_attributes": True}


class MemberCreate(BaseModel):
    email: EmailStr
    full_name: str
    role: _AllRolesLiteral = "member"


class MemberRoleUpdate(BaseModel):
    role: _AllRolesLiteral
