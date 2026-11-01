from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.enums import ReasonCode
from app.schemas.common import ORM


class StopOut(ORM):
    stop_id: str
    route_id: str
    delivery_id: str
    sequence: int
    planned_arrival: datetime
    planned_departure: datetime
    travel_km_from_prev: float
    removed_at: datetime | None


class RouteOut(ORM):
    route_id: str
    route_date: date
    vehicle_id: str
    driver_id: str
    shift_id: str
    total_weight_kg: float
    total_volume_m3: float
    total_distance_km: float
    planned_duration_min: float
    flags: list[str]


class RouteDetailOut(RouteOut):
    stops: list[StopOut]
    capacity: dict  # effective capacity at route_date
    utilization: dict  # weight_pct, volume_pct, stops_pct


class ManifestOut(BaseModel):
    route_id: str
    load_order: list[StopOut]  # reverse of stop sequence (last stop loaded first)


class PlanIn(BaseModel):
    model_config = {"populate_by_name": True}
    plan_date: date = Field(alias="date")
    delivery_ids: list[str] = []  # empty = all unassigned for that date
    strategy: str = Field("greedy_insertion", pattern="^(greedy_insertion|ortools)$")


class AddStopIn(BaseModel):
    delivery_id: str
    position: int = Field(ge=1)
    force: bool = False  # true = allow rule violation, route gets flagged


class ReorderIn(BaseModel):
    stop_ids: list[str] = Field(min_length=1)


class UnservedIn(BaseModel):
    reason: ReasonCode


class UnservedOut(ORM):
    delivery_id: str
    reason: ReasonCode
