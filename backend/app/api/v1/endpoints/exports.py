from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy import select

from app.api.deps import DB, RunDep, require_permission
from app.core.exceptions import NotFound
from app.core.permissions import P, permissions_for
from app.models import EntityEvent, Export, User
from app.schemas.analysis import EventOut, ExportIn, ExportOut
from app.schemas.common import JobAccepted
from app.services import run_service

router = APIRouter(prefix="/runs/{run_id}", tags=["exports"])


@router.post("/exports", response_model=JobAccepted, status_code=202)
def create_export(run: RunDep, data: ExportIn, db: DB, user: User = Depends(require_permission(P.EXPORTS_DOWNLOAD))):
    payload = data.model_dump()
    if P.GROUND_TRUTH_READ not in permissions_for(user.role):
        payload["include"] = [i for i in payload["include"] if i != "ground_truth"]  # never leak labels
    job = run_service.enqueue(db, run, "export", payload)
    return JobAccepted(job_id=job.id, run_id=run.id)


@router.get("/exports", response_model=list[ExportOut], dependencies=[Depends(require_permission(P.EXPORTS_DOWNLOAD))])
def list_exports(run: RunDep, db: DB):
    return db.scalars(select(Export).where(Export.run_id == run.id).order_by(Export.created_at.desc())).all()


@router.get("/exports/{export_id}/download", dependencies=[Depends(require_permission(P.EXPORTS_DOWNLOAD))])
def download(run: RunDep, export_id: str, db: DB):
    exp = db.get(Export, export_id)
    if exp is None or exp.run_id != run.id or not exp.path:
        raise NotFound("Export not ready")
    return FileResponse(exp.path, media_type="application/zip", filename=f"vrptw_{run.id}_{export_id}.zip")


@router.get("/docs/data-dictionary", dependencies=[Depends(require_permission(P.RUNS_READ))])
def data_dictionary(run: RunDep):
    from vrptw_core.export.docs import data_dictionary as build
    return build()


@router.get("/docs/source-manifest", dependencies=[Depends(require_permission(P.RUNS_READ))])
def source_manifest(run: RunDep):
    from vrptw_core.export.docs import source_manifest as build
    return build(run.seed, run.config)


@router.get("/events", response_model=list[EventOut], dependencies=[Depends(require_permission(P.RUNS_READ))])
def events(run: RunDep, db: DB, entity: str, entity_id: str):
    return db.scalars(select(EntityEvent).where(EntityEvent.run_id == run.id, EntityEvent.entity == entity,
                                                EntityEvent.entity_id == entity_id).order_by(EntityEvent.at)).all()
