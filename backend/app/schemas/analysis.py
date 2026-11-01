from datetime import date, datetime

from pydantic import BaseModel

from app.models.enums import AnomalyType, OutcomeStatus, ReasonCode, ValidationCheck
from app.schemas.common import ORM


class OutcomeOut(ORM):
    outcome_id: str
    delivery_id: str
    stop_id: str | None
    actual_arrival: datetime | None
    actual_departure: datetime | None
    status: OutcomeStatus
    reason_code: ReasonCode | None
    delay_minutes: float


class SimulateIn(BaseModel):
    dates: list[date]
    scenario_override: str | None = None


class GroundTruthOut(ORM):
    issue_type: AnomalyType
    affected_entity: str
    affected_id: str
    expected_decision: str


class DetectedAnomalyOut(BaseModel):
    check: ValidationCheck
    detected_type: str | None
    affected_id: str


class ValidationRunIn(BaseModel):
    checks: list[ValidationCheck] = list(ValidationCheck)


class CheckResult(BaseModel):
    name: ValidationCheck
    status: str
    failed_rows: int
    sample_ids: list[str]


class ValidationSummaryOut(BaseModel):
    passed: int
    failed: int
    checks: list[CheckResult]
    at: datetime | None


class KpisOut(BaseModel):
    on_time_rate: float
    failed_rate: float
    avg_delay_min: float
    unserved_count: int
    total_distance_km: float
    total_travel_min: float
    overtime_count: int


class ReasonShare(BaseModel):
    reason_code: ReasonCode
    count: int
    share: float


class VehicleUtilization(BaseModel):
    vehicle_id: str
    weight_pct: float
    volume_pct: float
    stops_pct: float


class ShiftUtilization(BaseModel):
    driver_id: str
    used_hours: float
    available_hours: float
    overtime_minutes: float


class DetectionScore(BaseModel):
    issue_type: AnomalyType
    tp: int
    fp: int
    fn: int
    precision: float
    recall: float


class TimeseriesPoint(BaseModel):
    bucket: date
    value: float


class ExportIn(BaseModel):
    formats: list[str] = ["csv", "json", "sql"]
    include: list[str] = ["data", "ground_truth", "docs", "validation", "generator"]


class ExportOut(ORM):
    id: str
    formats: list[str]
    include: list[str]
    size_bytes: int | None
    sha256: str | None
    created_at: datetime


class EventOut(ORM):
    entity: str
    entity_id: str
    from_state: str | None
    to_state: str
    payload: dict
    actor_id: str | None
    at: datetime
