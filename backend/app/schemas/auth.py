from pydantic import BaseModel, EmailStr, Field

from app.core.permissions import Role
from app.schemas.common import ORM


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserOut(ORM):
    id: str
    email: EmailStr
    name: str
    role: Role
    supplier_id: str | None
    is_active: bool


class MeOut(UserOut):
    permissions: list[str]


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: MeOut


class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=8)
    role: Role
    supplier_id: str | None = None


class UserUpdate(BaseModel):
    name: str | None = None
    role: Role | None = None
    is_active: bool | None = None
    supplier_id: str | None = None
