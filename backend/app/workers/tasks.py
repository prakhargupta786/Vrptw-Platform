"""Background jobs. Each task updates Job(status, step, progress) so GET /jobs/{id} can report progress."""
from app.workers.celery_app import celery_app


@celery_app.task(name="generate_run")
def generate_run(run_id: str, job_id: str) -> None:
    """Steps 1-6: config -> master -> demand -> planning -> simulation -> anomaly injection.
    Calls vrptw_core.pipeline.generate(RunConfig) then bulk-loads dataframes with run_id,
    sets Run.status=ready. TODO: chain validate_run once the validation checks exist."""
    from app.db.session import SessionLocal
    from app.models import Job, Run
    from app.models.enums import RunStatus
    from app.services.generation_service import generate_into

    with SessionLocal() as db:
        run, job = db.get(Run, run_id), db.get(Job, job_id)
        run.status, job.status, job.step = RunStatus.GENERATING, "running", "generating"
        db.commit()
        try:
            counts = generate_into(db, run)
        except Exception as e:
            db.rollback()
            run.status, job.status, job.error = RunStatus.FAILED, "failed", str(e)
            db.commit()
            raise
        job.status, job.step, job.progress, job.result = "succeeded", "done", 100, counts
        db.commit()


@celery_app.task(name="validate_run")
def validate_run(run_id: str, job_id: str, payload: dict) -> None:
    """Step 7: vrptw_core.validation.runner.run_checks -> ValidationResult rows -> Run.status=validated."""
    raise NotImplementedError


@celery_app.task(name="plan_routes")
def plan_routes(run_id: str, job_id: str, payload: dict) -> None:
    raise NotImplementedError


@celery_app.task(name="simulate_outcomes")
def simulate_outcomes(run_id: str, job_id: str, payload: dict) -> None:
    raise NotImplementedError


@celery_app.task(name="reproducibility_check")
def reproducibility_check(run_id: str, job_id: str, payload: dict) -> None:
    """Step 9: generate N times into temp dirs, compare row counts + SHA-256 per file -> Job.result."""
    raise NotImplementedError


@celery_app.task(name="export_run")
def export_run(run_id: str, job_id: str, payload: dict) -> None:
    """Step 8: write /data /ground_truth /docs /validation /generator, zip, store Export row."""
    raise NotImplementedError
