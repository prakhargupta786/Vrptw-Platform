from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.api.deps import DB, Paging, RunDep, require_permission, supplier_scope
from app.core.exceptions import NotFound
from app.core.permissions import P
from app.models import Delivery, DeliveryOutcome, Order, RouteStop, User
from app.models.enums import OutcomeStatus, ReasonCode
from app.repositories.base import apply_filters, paginate
from app.schemas.analysis import OutcomeOut, SimulateIn
from app.schemas.common import JobAccepted, Page
from app.services import run_service

router = APIRouter(prefix="/runs/{run_id}", tags=["outcomes"])


@router.get("/outcomes", response_model=Page[OutcomeOut])
def list_outcomes(run: RunDep, db: DB, paging: Paging, status: OutcomeStatus | None = None,
                  reason_code: ReasonCode | None = None, route_id: str | None = None, min_delay: float | None = None,
                  user: User = Depends(require_permission(P.OUTCOMES_READ))):
    stmt = apply_filters(select(DeliveryOutcome).where(DeliveryOutcome.run_id == run.id), DeliveryOutcome,
                         status=status, reason_code=reason_code)
    if min_delay is not None:
        stmt = stmt.where(DeliveryOutcome.delay_minutes >= min_delay)
    if route_id:
        stmt = stmt.join(RouteStop, (RouteStop.run_id == DeliveryOutcome.run_id) &
                         (RouteStop.stop_id == DeliveryOutcome.stop_id)).where(RouteStop.route_id == route_id)
    if scope := supplier_scope(user):
        stmt = (stmt.join(Delivery, (Delivery.run_id == DeliveryOutcome.run_id) &
                          (Delivery.delivery_id == DeliveryOutcome.delivery_id))
                    .join(Order, (Order.run_id == Delivery.run_id) & (Order.order_id == Delivery.order_id))
                    .where(Order.supplier_id == scope))
    return paginate(db, stmt, DeliveryOutcome, paging)


@router.get("/outcomes/{outcome_id}", response_model=OutcomeOut,
            dependencies=[Depends(require_permission(P.OUTCOMES_READ))])
def get_outcome(run: RunDep, outcome_id: str, db: DB):
    o = db.get(DeliveryOutcome, (outcome_id, run.id))
    if o is None:
        raise NotFound("Outcome not found")
    return o


@router.post("/simulate", response_model=JobAccepted, status_code=202,
             dependencies=[Depends(require_permission(P.RUNS_CREATE))])
def simulate(run: RunDep, data: SimulateIn, db: DB):
    job = run_service.enqueue(db, run, "simulate", data.model_dump(mode="json"))
    return JobAccepted(job_id=job.id, run_id=run.id)
