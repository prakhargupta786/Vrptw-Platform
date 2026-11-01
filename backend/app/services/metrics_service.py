"""KPI queries. Thin wrapper around vrptw_core.metrics.kpis so CLI and API compute identical numbers."""
from datetime import date

from sqlalchemy.orm import Session


def kpis(db: Session, run_id: str, date_from: date | None, date_to: date | None, vehicle_id: str | None) -> dict:
    raise NotImplementedError


def failures_by_reason(db: Session, run_id: str, date_from: date | None, date_to: date | None) -> list[dict]:
    raise NotImplementedError


def capacity_utilization(db: Session, run_id: str, on: date | None) -> list[dict]:
    raise NotImplementedError


def shift_utilization(db: Session, run_id: str, on: date | None) -> list[dict]:
    raise NotImplementedError


def detection_scores(db: Session, run_id: str) -> list[dict]:
    """Join validation_results (detected) with ground_truth (expected) per issue_type -> tp/fp/fn."""
    raise NotImplementedError


def timeseries(db: Session, run_id: str, metric: str, granularity: str) -> list[dict]:
    raise NotImplementedError
