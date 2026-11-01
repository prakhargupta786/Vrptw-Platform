import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models._mixins import RunScoped
from app.models.enums import AnomalyType, ValidationCheck


class EntityEvent(RunScoped, Base):
    """Append-only state history (business rule 8: never overwrite state).
    Generated events use EVT-0000001… per run, so the key is (run_id, id) like the other run-scoped tables."""
    __tablename__ = "entity_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity: Mapped[str] = mapped_column(String(30), index=True)
    entity_id: Mapped[str] = mapped_column(String(40), index=True)
    from_state: Mapped[str | None] = mapped_column(String(30), nullable=True)
    to_state: Mapped[str] = mapped_column(String(30))
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    actor_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class GroundTruth(Base):
    """Injected anomaly labels. Restricted to ground_truth:read. Never joined into input-table APIs."""
    __tablename__ = "ground_truth"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("runs.id", ondelete="CASCADE"), index=True)
    issue_type: Mapped[AnomalyType] = mapped_column(Enum(AnomalyType, native_enum=False))
    affected_entity: Mapped[str] = mapped_column(String(30))
    affected_id: Mapped[str] = mapped_column(String(40))
    expected_decision: Mapped[str] = mapped_column(String(60))


class ValidationResult(Base):
    __tablename__ = "validation_results"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("runs.id", ondelete="CASCADE"), index=True)
    check_name: Mapped[ValidationCheck] = mapped_column(Enum(ValidationCheck, native_enum=False))
    status: Mapped[str] = mapped_column(String(10))  # pass | fail
    failed_rows: Mapped[int] = mapped_column(Integer, default=0)
    failing_ids: Mapped[list] = mapped_column(JSON, default=list)
    detected_type: Mapped[str | None] = mapped_column(String(40), nullable=True)
    at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Export(Base):
    __tablename__ = "exports"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("runs.id", ondelete="CASCADE"), index=True)
    formats: Mapped[list] = mapped_column(JSON)
    include: Mapped[list] = mapped_column(JSON)
    path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
