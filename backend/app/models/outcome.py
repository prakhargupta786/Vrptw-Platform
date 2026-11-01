from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Enum, Float, ForeignKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models._mixins import RunScoped
from app.models.enums import OutcomeStatus, ReasonCode


class DeliveryOutcome(RunScoped, Base):
    __tablename__ = "delivery_outcomes"
    __table_args__ = (
        ForeignKeyConstraint(["run_id", "delivery_id"], ["deliveries.run_id", "deliveries.delivery_id"]),
        ForeignKeyConstraint(["run_id", "stop_id"], ["route_stops.run_id", "route_stops.stop_id"]),
        # Business rule 7: failed delivery must carry a reason code.
        CheckConstraint("status <> 'failed' OR reason_code IS NOT NULL", name="failed_needs_reason"),
    )
    outcome_id: Mapped[str] = mapped_column(String(24), primary_key=True)
    delivery_id: Mapped[str] = mapped_column(String(24), index=True)
    stop_id: Mapped[str | None] = mapped_column(String(40), nullable=True)
    actual_arrival: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    actual_departure: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[OutcomeStatus] = mapped_column(Enum(OutcomeStatus, native_enum=False))
    reason_code: Mapped[ReasonCode | None] = mapped_column(Enum(ReasonCode, native_enum=False), nullable=True)
    delay_minutes: Mapped[float] = mapped_column(Float, default=0)
