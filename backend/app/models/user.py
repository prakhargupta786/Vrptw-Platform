import uuid

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.permissions import Role
from app.db.base import Base
from app.models._mixins import Timestamped


class User(Timestamped, Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(Enum(Role, native_enum=False))
    supplier_id: Mapped[str | None] = mapped_column(String(40), nullable=True)  # row-level scope for SUPPLIER
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
