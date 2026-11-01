from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select

from app.api.deps import DB, Paging, RunDep, WritableRun, require_permission
from app.core.exceptions import NotFound
from app.core.permissions import P
from app.models import Route, RouteStop, UnservedDelivery, User
from app.models.enums import ReasonCode
from app.repositories.base import apply_filters, list_run_scoped, paginate
from app.schemas.common import JobAccepted, Page
from app.schemas.planning import (AddStopIn, ManifestOut, PlanIn, ReorderIn, RouteDetailOut, RouteOut, UnservedIn,
                                  UnservedOut)
from app.services import planning_service, run_service

router = APIRouter(prefix="/runs/{run_id}", tags=["planning"])
READ = [Depends(require_permission(P.ROUTES_READ))]
PLAN = Depends(require_permission(P.ROUTES_PLAN))


def _route(db, run_id: str, route_id: str) -> Route:
    r = db.get(Route, (route_id, run_id))  # PK order is (entity_id, run_id)
    if r is None:
        raise NotFound("Route not found")
    return r


@router.get("/routes", response_model=Page[RouteOut], dependencies=READ)
def list_routes(run: RunDep, db: DB, paging: Paging, route_date: date | None = None, vehicle_id: str | None = None,
                driver_id: str | None = None, flag: str | None = None):
    stmt = apply_filters(select(Route).where(Route.run_id == run.id), Route,
                         route_date=route_date, vehicle_id=vehicle_id, driver_id=driver_id)
    if flag:
        stmt = stmt.where(Route.flags.contains([flag]))  # JSONB containment on Postgres
    return paginate(db, stmt, Route, paging)


@router.get("/routes/{route_id}", response_model=RouteDetailOut, dependencies=READ)
def get_route(run: RunDep, route_id: str, db: DB):
    route = _route(db, run.id, route_id)
    # TODO: active stops ordered by sequence + effective capacity + utilization %
    raise NotImplementedError


@router.get("/routes/{route_id}/manifest", response_model=ManifestOut, dependencies=READ)
def manifest(run: RunDep, route_id: str, db: DB):
    _route(db, run.id, route_id)
    stops = db.scalars(select(RouteStop).where(RouteStop.run_id == run.id, RouteStop.route_id == route_id,
                                               RouteStop.removed_at.is_(None))
                       .order_by(RouteStop.sequence.desc())).all()
    return ManifestOut(route_id=route_id, load_order=list(stops))


@router.post("/routes/plan", response_model=JobAccepted, status_code=202)
def plan(run: WritableRun, data: PlanIn, db: DB, _: User = PLAN):
    job = run_service.enqueue(db, run, "plan", data.model_dump(mode="json", by_alias=True))
    return JobAccepted(job_id=job.id, run_id=run.id)


@router.post("/routes/{route_id}/stops", response_model=RouteOut)
def add_stop(run: WritableRun, route_id: str, data: AddStopIn, db: DB, user: User = PLAN):
    return planning_service.add_stop(db, run.id, _route(db, run.id, route_id), data, user)


@router.patch("/routes/{route_id}/stops/reorder", response_model=RouteOut)
def reorder(run: WritableRun, route_id: str, data: ReorderIn, db: DB, user: User = PLAN):
    return planning_service.reorder_stops(db, run.id, _route(db, run.id, route_id), data, user)


@router.delete("/routes/{route_id}/stops/{stop_id}", status_code=204)
def remove_stop(run: WritableRun, route_id: str, stop_id: str, db: DB,
                reason: str = Query(..., min_length=2, max_length=60), user: User = PLAN):
    stop = db.get(RouteStop, (stop_id, run.id))
    if stop is None or stop.route_id != route_id:
        raise NotFound("Stop not found on this route")
    planning_service.remove_stop(db, run.id, _route(db, run.id, route_id), stop, reason, user)


@router.get("/unserved", response_model=Page[UnservedOut], dependencies=READ)
def list_unserved(run: RunDep, db: DB, paging: Paging, reason: ReasonCode | None = None):
    return list_run_scoped(db, UnservedDelivery, run.id, paging, reason=reason)


@router.post("/deliveries/{delivery_id}/unserve", response_model=UnservedOut, status_code=201)
def unserve(run: WritableRun, delivery_id: str, data: UnservedIn, db: DB, user: User = PLAN):
    # TODO: close any active stop for this delivery, set delivery.status=unserved, EntityEvent
    raise NotImplementedError
