"""Generate a full run (sites, fleet, drivers, orders, routes, outcomes...) straight into the DB — no Redis/Celery.

python -m app.seed_data                      # full scale: 500 sites, 2,000 deliveries, 100 vehicles, 30 days
python -m app.seed_data --scale starter      # 50 sites, 200 deliveries, 10 vehicles, 3 days
python -m app.seed_data --name "My run" --seed 42
Requires a user to own the run: run `python -m app.seed` first.
"""
import argparse
import time

from sqlalchemy import select

from app.core.permissions import Role
from app.db.session import SessionLocal
from app.models import Job, Run, User
from app.models.enums import RunStatus
from app.schemas.run import RunCreate, Scale
from app.services.generation_service import generate_into
from vrptw_core.config import RunConfig


def main() -> None:
    ap = argparse.ArgumentParser(prog="seed_data")
    ap.add_argument("--scale", choices=["starter", "full"], default="full")
    ap.add_argument("--seed", type=int, default=20261022)
    ap.add_argument("--name", default=None)
    args = ap.parse_args()

    c = RunConfig(seed=args.seed) if args.scale == "full" else RunConfig.starter(args.seed)
    data = RunCreate(name=args.name or f"{args.scale.title()} – Seed {args.seed}", seed=args.seed,
                     scale=Scale(sites=c.sites, deliveries=c.deliveries, vehicles=c.vehicles, days=c.days))

    with SessionLocal() as db:
        owner = db.scalar(select(User).where(User.role == Role.ADMIN, User.is_active.is_(True)))
        if owner is None:
            raise SystemExit("No active ADMIN user. Run `python -m app.seed` first.")
        run = Run(name=data.name, seed=data.seed, config=data.model_dump(mode="json", exclude={"name", "seed"}),
                  status=RunStatus.GENERATING, created_by=owner.id)
        db.add(run)
        db.flush()
        job = Job(run_id=run.id, kind="generate", status="running", step="generating")
        db.add(job)
        db.commit()

        print(f"Generating '{run.name}' ({c.sites} sites, {c.deliveries} deliveries, {c.vehicles} vehicles, "
              f"{c.days} days)...")
        t = time.time()
        try:
            counts = generate_into(db, run)
        except Exception as e:
            db.rollback()
            run.status, job.status, job.error = RunStatus.FAILED, "failed", str(e)
            db.commit()
            raise
        job.status, job.step, job.progress, job.result = "succeeded", "done", 100, counts
        db.commit()

    for name, n in counts.items():
        print(f"  {name:22} {n:>8,}")
    print(f"Done in {time.time() - t:.1f}s. Run id: {run.id}  (status: ready)")


if __name__ == "__main__":
    main()
