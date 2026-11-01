from datetime import date, datetime

from sqlalchemy import JSON, Date, DateTime, Enum, Float, ForeignKeyConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models._mixins import RunScoped
from app.models.enums import ReasonCode


class Route(RunScoped, Base):
    __tablename__ = "routes"
    __table_args__ = (
        ForeignKeyConstraint(["run_id", "vehicle_id"], ["vehicles.run_id", "vehicles.vehicle_id"]),
        ForeignKeyConstraint(["run_id", "driver_id"], ["drivers.run_id", "drivers.driver_id"]),
        ForeignKeyConstraint(["run_id", "shift_id"], ["shifts.run_id", "shifts.shift_id"]),
    )
    route_id: Mapped[str] = mapped_column(String(24), primary_key=True)  # RTE-2026-000001
    route_date: Mapped[date] = mapped_column(Date, index=True)
    vehicle_id: Mapped[str] = mapped_column(String(20))
    driver_id: Mapped[str] = mapped_column(String(20))
    shift_id: Mapped[str] = mapped_column(String(20))
    # Derived from active stops by planning_service.recompute_totals(); never set by clients.
    total_weight_kg: Mapped[float] = mapped_column(Float, default=0)
    total_volume_m3: Mapped[float] = mapped_column(Float, default=0)
    total_distance_km: Mapped[float] = mapped_column(Float, default=0)
    planned_duration_min: Mapped[float] = mapped_column(Float, default=0)
    flags: Mapped[list] = mapped_column(JSON, default=list)  # ["capacity_exceeded", "shift_exceeded", ...]


class RouteStop(RunScoped, Base):
    """Bridge Route <-> Delivery. Re-planning closes a stop (removed_at) instead of deleting it."""
    __tablename__ = "route_stops"
    __table_args__ = (
        ForeignKeyConstraint(["run_id", "route_id"], ["routes.run_id", "routes.route_id"], ondelete="CASCADE"),
        ForeignKeyConstraint(["run_id", "delivery_id"], ["deliveries.run_id", "deliveries.delivery_id"]),
    )
    stop_id: Mapped[str] = mapped_column(String(40), primary_key=True)  # STOP-RTE-2026-000001-001
    route_id: Mapped[str] = mapped_column(String(24), index=True)
    delivery_id: Mapped[str] = mapped_column(String(24), index=True)
    sequence: Mapped[int] = mapped_column(Integer)
    planned_arrival: Mapped[datetime] = mapped_column(DateTime)
    planned_departure: Mapped[datetime] = mapped_column(DateTime)
    travel_km_from_prev: Mapped[float] = mapped_column(Float, default=0)
    removed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    removed_reason: Mapped[str | None] = mapped_column(String(60), nullable=True)


class UnservedDelivery(RunScoped, Base):
    __tablename__ = "unserved_deliveries"
    __table_args__ = (
        ForeignKeyConstraint(["run_id", "delivery_id"], ["deliveries.run_id", "deliveries.delivery_id"]),
    )
    delivery_id: Mapped[str] = mapped_column(String(24), primary_key=True)
    reason: Mapped[ReasonCode] = mapped_column(Enum(ReasonCode, native_enum=False))
