import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models._mixins import Timestamped
from app.models.enums import RunStatus


class Run(Timestamped, Base):
    """One generation run = one seed + scale config. All data tables hang off run_id."""
    __tablename__ = "runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(120))
    seed: Mapped[int] = mapped_column(Integer)
    config: Mapped[dict] = mapped_column(JSON)  # scale, anomaly_rate, anomaly_types
    status: Mapped[RunStatus] = mapped_column(Enum(RunStatus, native_enum=False), default=RunStatus.QUEUED)
    row_counts: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    checksums: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # file -> sha256
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    locked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Job(Timestamped, Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("runs.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(30))  # generate | validate | plan | simulate | reproduce | export
    status: Mapped[str] = mapped_column(String(20), default="queued")  # queued | running | succeeded | failed
    step: Mapped[str | None] = mapped_column(String(60), nullable=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
