from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.api.deps import DB, Paging, RunDep, require_permission
from app.core.exceptions import Conflict, NotFound
from app.core.permissions import P
from app.models import Job, Run, User
from app.models.enums import RunStatus
from app.repositories.base import apply_filters, paginate
from app.schemas.common import JobAccepted, JobOut, Page
from app.schemas.run import ReproduceIn, ReproducibilityOut, RunCreate, RunOut
from app.services import run_service

router = APIRouter(tags=["runs"])


@router.post("/runs", response_model=JobAccepted, status_code=202)
def create_run(data: RunCreate, db: DB, user: User = Depends(require_permission(P.RUNS_CREATE))):
    run, job = run_service.create_run(db, data, user)
    return JobAccepted(job_id=job.id, run_id=run.id)


@router.get("/runs", response_model=Page[RunOut], dependencies=[Depends(require_permission(P.RUNS_READ))])
def list_runs(db: DB, paging: Paging, status: RunStatus | None = None, seed: int | None = None):
    return paginate(db, apply_filters(select(Run), Run, status=status, seed=seed), Run, paging)


@router.get("/runs/{run_id}", response_model=RunOut, dependencies=[Depends(require_permission(P.RUNS_READ))])
def get_run(run: RunDep):
    return run


@router.delete("/runs/{run_id}", status_code=204, dependencies=[Depends(require_permission(P.RUNS_DELETE))])
def delete_run(run: RunDep, db: DB):
    if run.status == RunStatus.LOCKED:
        raise Conflict("Locked runs cannot be deleted", code="RUN_LOCKED")
    db.delete(run)
    db.commit()


@router.post("/runs/{run_id}/lock", response_model=RunOut, dependencies=[Depends(require_permission(P.RUNS_LOCK))])
def lock_run(run: RunDep, db: DB):
    if run.status != RunStatus.VALIDATED:
        raise Conflict("Only validated runs can be locked", code="RUN_NOT_VALIDATED")
    run.status, run.locked_at = RunStatus.LOCKED, datetime.now(timezone.utc)
    db.commit()
    return run


@router.post("/runs/{run_id}/reproduce", response_model=JobAccepted, status_code=202,
             dependencies=[Depends(require_permission(P.RUNS_RERUN))])
def reproduce(run: RunDep, data: ReproduceIn, db: DB):
    job = run_service.enqueue(db, run, "reproduce", data.model_dump())
    return JobAccepted(job_id=job.id, run_id=run.id)


@router.get("/runs/{run_id}/reproducibility", response_model=ReproducibilityOut,
            dependencies=[Depends(require_permission(P.RUNS_READ))])
def reproducibility(run: RunDep, db: DB):
    job = db.scalar(select(Job).where(Job.run_id == run.id, Job.kind == "reproduce", Job.status == "succeeded")
                    .order_by(Job.created_at.desc()))
    if not job:
        raise NotFound("No reproducibility check has completed for this run")
    return job.result


@router.get("/jobs/{job_id}", response_model=JobOut, dependencies=[Depends(require_permission(P.RUNS_READ))])
def get_job(job_id: str, db: DB):
    job = db.get(Job, job_id)
    if not job:
        raise NotFound("Job not found")
    return job
