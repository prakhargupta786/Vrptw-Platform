from datetime import date, datetime

from pydantic import BaseModel, Field, model_validator

from app.models.enums import TrafficScenario, VehicleStatus, VehicleType
from app.schemas.common import ORM


class SiteOut(ORM):
    site_id: str
    name: str
    lat: float
    lon: float
    region: str
    address_type: str
    access_restrictions: dict


class SiteUpdate(BaseModel):
    lat: float | None = Field(None, ge=-90, le=90)
    lon: float | None = Field(None, ge=-180, le=180)
    access_restrictions: dict | None = None


class VehicleOut(ORM):
    vehicle_id: str
    type: VehicleType
    status: VehicleStatus
    restricted_zones: list[str]
    effective_from: date
    effective_to: date | None


class VehicleUpdate(BaseModel):
    status: VehicleStatus | None = None
    restricted_zones: list[str] | None = None


class CapacityIn(BaseModel):
    max_weight_kg: float = Field(gt=0)
    max_volume_m3: float = Field(gt=0)
    max_stops: int = Field(gt=0)
    effective_from: date


class CapacityOut(ORM, CapacityIn):
    capacity_id: str
    vehicle_id: str
    effective_to: date | None


class DriverOut(ORM):
    driver_id: str
    name: str
    license_class: str
    home_depot: str
    is_active: bool


class ShiftIn(BaseModel):
    start_at: datetime
    end_at: datetime
    break_minutes: int = Field(ge=0, le=180)
    max_driving_hours: float = Field(gt=0, le=14)

    @model_validator(mode="after")
    def end_after_start(self):
        if self.end_at <= self.start_at:
            raise ValueError("end_at must be after start_at")
        return self


class ShiftOut(ORM, ShiftIn):
    shift_id: str
    driver_id: str


class TravelLookupOut(BaseModel):
    from_site: str
    to_site: str
    day: int
    scenario: TrafficScenario
    distance_km: float
    traffic_factor: float
    travel_minutes: float
