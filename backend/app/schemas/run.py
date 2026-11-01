from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import AnomalyType, RunStatus
from app.schemas.common import ORM


class Scale(BaseModel):
    sites: int = Field(500, ge=1, le=50_000)
    deliveries: int = Field(2000, ge=1, le=500_000)
    vehicles: int = Field(100, ge=1, le=10_000)
    days: int = Field(30, ge=1, le=366)


class RunCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    seed: int = 20261022
    scale: Scale = Scale()
    anomaly_rate: float = Field(0.02, ge=0, le=0.2)
    anomaly_types: list[AnomalyType] = list(AnomalyType)


class RunOut(ORM):
    id: str
    name: str
    seed: int
    config: dict
    status: RunStatus
    row_counts: dict | None
    created_at: datetime
    locked_at: datetime | None


class ReproduceIn(BaseModel):
    reruns: int = Field(2, ge=2, le=5)


class FileCompare(BaseModel):
    name: str
    rows_a: int
    rows_b: int
    sha256_a: str
    sha256_b: str
    match: bool


class ReproducibilityOut(BaseModel):
    match: bool
    files: list[FileCompare]
