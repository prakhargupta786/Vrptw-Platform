"""Run lifecycle: create -> enqueue generation -> load core output into DB -> validate -> lock."""
from sqlalchemy.orm import Session

from app.models import Job, Run, User
from app.models.enums import RunStatus
from app.schemas.run import RunCreate


def create_run(db: Session, data: RunCreate, user: User) -> tuple[Run, Job]:
    run = Run(name=data.name, seed=data.seed, config=data.model_dump(mode="json", exclude={"name", "seed"}),
              status=RunStatus.QUEUED, created_by=user.id)
    db.add(run)
    db.flush()
    job = Job(run_id=run.id, kind="generate")
    db.add(job)
    db.commit()
    from app.workers.tasks import generate_run  # local import: avoid celery import at app start
    generate_run.delay(run.id, job.id)
    return run, job


def enqueue(db: Session, run: Run, kind: str, payload: dict | None = None) -> Job:
    """Creates a job row and dispatches the matching Celery task."""
    from app.workers import tasks
    job = Job(run_id=run.id, kind=kind)
    db.add(job)
    db.commit()
    task = {
        "validate": tasks.validate_run, "plan": tasks.plan_routes, "simulate": tasks.simulate_outcomes,
        "reproduce": tasks.reproducibility_check, "export": tasks.export_run,
    }[kind]
    task.delay(run.id, job.id, payload or {})
    return job
