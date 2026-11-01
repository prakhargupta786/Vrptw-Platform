from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.api.deps import DB, Paging, require_permission
from app.core.exceptions import Conflict, NotFound
from app.core.permissions import P, Role
from app.core.security import hash_password
from app.models import User
from app.repositories.base import apply_filters, paginate
from app.schemas.auth import UserCreate, UserOut, UserUpdate
from app.schemas.common import Page

router = APIRouter(prefix="/users", tags=["users"], dependencies=[Depends(require_permission(P.USERS_MANAGE))])


@router.get("", response_model=Page[UserOut])
def list_users(db: DB, paging: Paging, role: Role | None = None, is_active: bool | None = None):
    return paginate(db, apply_filters(select(User), User, role=role, is_active=is_active), User, paging)


@router.post("", response_model=UserOut, status_code=201)
def create_user(data: UserCreate, db: DB):
    if db.scalar(select(User).where(User.email == data.email)):
        raise Conflict("Email already registered", code="EMAIL_TAKEN")
    if data.role == Role.SUPPLIER and not data.supplier_id:
        raise Conflict("SUPPLIER users need supplier_id", code="SUPPLIER_ID_REQUIRED")
    user = User(**data.model_dump(exclude={"password"}), password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    return user


@router.patch("/{user_id}", response_model=UserOut)
def update_user(user_id: str, data: UserUpdate, db: DB):
    user = db.get(User, user_id)
    if not user:
        raise NotFound("User not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(user, k, v)
    db.commit()
    return user


@router.delete("/{user_id}", status_code=204)
def deactivate_user(user_id: str, db: DB):
    user = db.get(User, user_id)
    if not user:
        raise NotFound("User not found")
    user.is_active = False  # soft delete keeps audit trail (EntityEvent.actor_id)
    db.commit()
