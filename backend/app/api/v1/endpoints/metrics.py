from datetime import date

from fastapi import APIRouter, Depends, Query

from app.api.deps import DB, RunDep, require_permission
from app.core.permissions import P
from app.schemas.analysis import (DetectionScore, KpisOut, ReasonShare, ShiftUtilization, TimeseriesPoint,
                                  VehicleUtilization)
from app.services import metrics_service as m

router = APIRouter(prefix="/runs/{run_id}/metrics", tags=["metrics"],
                   dependencies=[Depends(require_permission(P.METRICS_READ))])


@router.get("/kpis", response_model=KpisOut)
def kpis(run: RunDep, db: DB, date_from: date | None = None, date_to: date | None = None,
         vehicle_id: str | None = None):
    return m.kpis(db, run.id, date_from, date_to, vehicle_id)


@router.get("/failures-by-reason", response_model=list[ReasonShare])
def failures_by_reason(run: RunDep, db: DB, date_from: date | None = None, date_to: date | None = None):
    return m.failures_by_reason(db, run.id, date_from, date_to)


@router.get("/capacity-utilization", response_model=list[VehicleUtilization])
def capacity_utilization(run: RunDep, db: DB, on: date | None = None):
    return m.capacity_utilization(db, run.id, on)


@router.get("/shift-utilization", response_model=list[ShiftUtilization])
def shift_utilization(run: RunDep, db: DB, on: date | None = None):
    return m.shift_utilization(db, run.id, on)


@router.get("/anomaly-detection", response_model=list[DetectionScore])
def anomaly_detection(run: RunDep, db: DB):
    return m.detection_scores(db, run.id)


@router.get("/timeseries", response_model=list[TimeseriesPoint])
def timeseries(run: RunDep, db: DB,
               metric: str = Query(..., pattern="^(on_time_rate|failed_rate|avg_delay_min|unserved_count)$"),
               granularity: str = Query("day", pattern="^(day|week)$")):
    return m.timeseries(db, run.id, metric, granularity)
