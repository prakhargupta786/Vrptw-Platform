"""Anomalies, ground truth, validation."""
from fastapi import APIRouter, Depends
from sqlalchemy import func, select

from app.api.deps import DB, Paging, RunDep, require_permission
from app.core.permissions import P
from app.models import GroundTruth, ValidationResult
from app.models.enums import AnomalyType, ValidationCheck
from app.repositories.base import apply_filters, paginate
from app.schemas.analysis import (CheckResult, DetectedAnomalyOut, GroundTruthOut, ValidationRunIn,
                                  ValidationSummaryOut)
from app.schemas.common import JobAccepted, Page
from app.services import run_service

router = APIRouter(prefix="/runs/{run_id}", tags=["quality"])


@router.get("/anomalies/detected", response_model=list[DetectedAnomalyOut],
            dependencies=[Depends(require_permission(P.ANOMALIES_READ))])
def detected(run: RunDep, db: DB, issue_type: AnomalyType | None = None):
    stmt = select(ValidationResult).where(ValidationResult.run_id == run.id, ValidationResult.status == "fail")
    if issue_type:
        stmt = stmt.where(ValidationResult.detected_type == issue_type)
    return [DetectedAnomalyOut(check=r.check_name, detected_type=r.detected_type, affected_id=i)
            for r in db.scalars(stmt) for i in r.failing_ids]


@router.get("/ground-truth", response_model=Page[GroundTruthOut],
            dependencies=[Depends(require_permission(P.GROUND_TRUTH_READ))])
def ground_truth(run: RunDep, db: DB, paging: Paging, issue_type: AnomalyType | None = None):
    stmt = apply_filters(select(GroundTruth).where(GroundTruth.run_id == run.id), GroundTruth, issue_type=issue_type)
    return paginate(db, stmt, GroundTruth, paging)


@router.post("/validation/run", response_model=JobAccepted, status_code=202,
             dependencies=[Depends(require_permission(P.VALIDATION_RUN))])
def run_validation(run: RunDep, data: ValidationRunIn, db: DB):
    job = run_service.enqueue(db, run, "validate", data.model_dump(mode="json"))
    return JobAccepted(job_id=job.id, run_id=run.id)


@router.get("/validation/summary", response_model=ValidationSummaryOut,
            dependencies=[Depends(require_permission(P.VALIDATION_READ))])
def validation_summary(run: RunDep, db: DB):
    latest = db.scalar(select(func.max(ValidationResult.at)).where(ValidationResult.run_id == run.id))
    rows = db.scalars(select(ValidationResult).where(ValidationResult.run_id == run.id,
                                                     ValidationResult.at == latest)).all() if latest else []
    checks = [CheckResult(name=r.check_name, status=r.status, failed_rows=r.failed_rows,
                          sample_ids=r.failing_ids[:10]) for r in rows]
    return ValidationSummaryOut(passed=sum(c.status == "pass" for c in checks),
                                failed=sum(c.status == "fail" for c in checks), checks=checks, at=latest)


@router.get("/validation/checks/{name}/failures", response_model=Page[str],
            dependencies=[Depends(require_permission(P.VALIDATION_READ))])
def check_failures(run: RunDep, name: ValidationCheck, db: DB, paging: Paging):
    row = db.scalar(select(ValidationResult).where(ValidationResult.run_id == run.id,
                                                   ValidationResult.check_name == name)
                    .order_by(ValidationResult.at.desc()))
    ids = row.failing_ids if row else []
    start = (paging.page - 1) * paging.page_size
    return Page(items=ids[start:start + paging.page_size], total=len(ids), page=paging.page,
                page_size=paging.page_size)
