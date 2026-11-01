from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from app.models.enums import DeliveryStatus, OrderStatus, Priority, VehicleType, WindowType
from app.schemas.common import ORM


class OrderCreate(BaseModel):
    site_id: str
    quantity: int = Field(gt=0)
    weight_kg: float = Field(gt=0)
    volume_m3: float = Field(gt=0)
    priority: Priority = Priority.NORMAL
    supplier_id: str | None = None


class OrderOut(ORM):
    order_id: str
    site_id: str
    supplier_id: str | None
    quantity: int
    weight_kg: float
    volume_m3: float
    priority: Priority
    status: OrderStatus
    created_at: datetime


class OrderTransitionIn(BaseModel):
    to_status: OrderStatus
    reason: str | None = None


class TimeWindowIn(BaseModel):
    earliest: datetime
    latest: datetime
    type: WindowType = WindowType.HARD
    priority: int = Field(1, ge=1, le=5)

    @model_validator(mode="after")
    def ordered(self):
        if self.earliest > self.latest:
            raise ValueError("earliest must be <= latest")
        return self


class TimeWindowOut(ORM, TimeWindowIn):
    window_id: str
    delivery_id: str


class DeliveryCreate(BaseModel):
    service_minutes: int = Field(gt=0, le=240)
    required_vehicle_type: VehicleType
    weight_kg: float | None = None  # defaults to share of order
    volume_m3: float | None = None
    time_window: TimeWindowIn


class DeliveryOut(ORM):
    delivery_id: str
    order_id: str
    service_minutes: int
    required_vehicle_type: VehicleType
    weight_kg: float
    volume_m3: float
    status: DeliveryStatus


class DeliveryDetailOut(DeliveryOut):
    time_window: TimeWindowOut | None
    stop_history: list[dict]


class OrderDetailOut(OrderOut):
    deliveries: list[DeliveryOut]
    outcomes: list[dict]
