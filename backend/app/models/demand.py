from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKeyConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models._mixins import RunScoped, Timestamped
from app.models.enums import DeliveryStatus, OrderStatus, Priority, VehicleType, WindowType


class Order(RunScoped, Timestamped, Base):
    __tablename__ = "orders"
    __table_args__ = (
        ForeignKeyConstraint(["run_id", "site_id"], ["customer_sites.run_id", "customer_sites.site_id"]),
    )
    order_id: Mapped[str] = mapped_column(String(24), primary_key=True)  # ORD-2026-000001
    site_id: Mapped[str] = mapped_column(String(20), index=True)
    supplier_id: Mapped[str | None] = mapped_column(String(40), nullable=True, index=True)  # open question
    quantity: Mapped[int] = mapped_column(Integer)
    weight_kg: Mapped[float] = mapped_column(Float)
    volume_m3: Mapped[float] = mapped_column(Float)
    priority: Mapped[Priority] = mapped_column(Enum(Priority, native_enum=False))
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus, native_enum=False), default=OrderStatus.CREATED)


class Delivery(RunScoped, Base):
    __tablename__ = "deliveries"
    __table_args__ = (
        ForeignKeyConstraint(["run_id", "order_id"], ["orders.run_id", "orders.order_id"], ondelete="CASCADE"),
    )
    delivery_id: Mapped[str] = mapped_column(String(24), primary_key=True)  # DEL-2026-000001
    order_id: Mapped[str] = mapped_column(String(24), index=True)
    service_minutes: Mapped[int] = mapped_column(Integer)
    required_vehicle_type: Mapped[VehicleType] = mapped_column(Enum(VehicleType, native_enum=False))
    weight_kg: Mapped[float] = mapped_column(Float)
    volume_m3: Mapped[float] = mapped_column(Float)
    status: Mapped[DeliveryStatus] = mapped_column(Enum(DeliveryStatus, native_enum=False), default=DeliveryStatus.PENDING)


class TimeWindow(RunScoped, Base):
    __tablename__ = "time_windows"
    __table_args__ = (
        ForeignKeyConstraint(["run_id", "delivery_id"], ["deliveries.run_id", "deliveries.delivery_id"], ondelete="CASCADE"),
    )
    window_id: Mapped[str] = mapped_column(String(24), primary_key=True)
    delivery_id: Mapped[str] = mapped_column(String(24), index=True)
    earliest: Mapped[datetime] = mapped_column(DateTime)
    latest: Mapped[datetime] = mapped_column(DateTime)
    type: Mapped[WindowType] = mapped_column(Enum(WindowType, native_enum=False))
    priority: Mapped[int] = mapped_column(Integer, default=1)
