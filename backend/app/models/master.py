from datetime import date, datetime

from sqlalchemy import (JSON, Boolean, Date, DateTime, Enum, Float, ForeignKeyConstraint, Integer, String)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models._mixins import RunScoped
from app.models.enums import TrafficScenario, VehicleStatus, VehicleType


class CustomerSite(RunScoped, Base):
    __tablename__ = "customer_sites"
    site_id: Mapped[str] = mapped_column(String(20), primary_key=True)  # SITE-000001
    name: Mapped[str] = mapped_column(String(120))
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    region: Mapped[str] = mapped_column(String(40), index=True)
    address_type: Mapped[str] = mapped_column(String(30))  # residential / commercial / industrial
    access_restrictions: Mapped[dict] = mapped_column(JSON, default=dict)  # {"max_vehicle_type": "van", "zone": "Z1"}


class Vehicle(RunScoped, Base):
    __tablename__ = "vehicles"
    vehicle_id: Mapped[str] = mapped_column(String(20), primary_key=True)  # VEH-000001
    type: Mapped[VehicleType] = mapped_column(Enum(VehicleType, native_enum=False))
    status: Mapped[VehicleStatus] = mapped_column(Enum(VehicleStatus, native_enum=False))
    restricted_zones: Mapped[list] = mapped_column(JSON, default=list)
    effective_from: Mapped[date] = mapped_column(Date)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)


class VehicleCapacity(RunScoped, Base):
    __tablename__ = "vehicle_capacities"
    __table_args__ = (
        ForeignKeyConstraint(["run_id", "vehicle_id"], ["vehicles.run_id", "vehicles.vehicle_id"], ondelete="CASCADE"),
    )
    capacity_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    vehicle_id: Mapped[str] = mapped_column(String(20), index=True)
    max_weight_kg: Mapped[float] = mapped_column(Float)
    max_volume_m3: Mapped[float] = mapped_column(Float)
    max_stops: Mapped[int] = mapped_column(Integer)
    effective_from: Mapped[date] = mapped_column(Date)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)  # no overlaps per vehicle (service check)


class Driver(RunScoped, Base):
    __tablename__ = "drivers"
    driver_id: Mapped[str] = mapped_column(String(20), primary_key=True)  # DRV-000001
    name: Mapped[str] = mapped_column(String(120))
    license_class: Mapped[str] = mapped_column(String(10))
    home_depot: Mapped[str] = mapped_column(String(40))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Shift(RunScoped, Base):
    __tablename__ = "shifts"
    __table_args__ = (
        ForeignKeyConstraint(["run_id", "driver_id"], ["drivers.run_id", "drivers.driver_id"], ondelete="CASCADE"),
    )
    shift_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    driver_id: Mapped[str] = mapped_column(String(20), index=True)
    start_at: Mapped[datetime] = mapped_column(DateTime)
    end_at: Mapped[datetime] = mapped_column(DateTime)
    break_minutes: Mapped[int] = mapped_column(Integer)
    max_driving_hours: Mapped[float] = mapped_column(Float)


class TravelTime(RunScoped, Base):
    """Base distance per site pair; scenario/day traffic factors applied on read
    (storing 500x500x30x3 = 22.5M rows is avoidable)."""
    __tablename__ = "travel_time_matrix"
    from_site: Mapped[str] = mapped_column(String(20), primary_key=True)
    to_site: Mapped[str] = mapped_column(String(20), primary_key=True)
    distance_km: Mapped[float] = mapped_column(Float)
    base_speed_kmh: Mapped[float] = mapped_column(Float)


class TrafficFactor(RunScoped, Base):
    __tablename__ = "traffic_factors"
    day: Mapped[int] = mapped_column(Integer, primary_key=True)  # 1..30
    scenario: Mapped[TrafficScenario] = mapped_column(Enum(TrafficScenario, native_enum=False), primary_key=True)
    region: Mapped[str] = mapped_column(String(40), primary_key=True)
    factor: Mapped[float] = mapped_column(Float)  # travel_minutes = distance / speed * 60 * factor
