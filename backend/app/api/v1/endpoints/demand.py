"""Orders, deliveries, time windows. SUPPLIER users are row-filtered to their supplier_id."""
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.api.deps import DB, Paging, RunDep, WritableRun, require_permission, supplier_scope
from app.core.exceptions import NotFound
from app.core.permissions import P
from app.models import Delivery, Order, User
from app.models.enums import DeliveryStatus, OrderStatus, Priority, VehicleType
from app.repositories.base import apply_filters, paginate
from app.schemas.common import Page
from app.schemas.demand import (DeliveryCreate, DeliveryDetailOut, DeliveryOut, OrderCreate, OrderDetailOut, OrderOut,
                                OrderTransitionIn, TimeWindowIn, TimeWindowOut)
from app.services import order_service

router = APIRouter(prefix="/runs/{run_id}", tags=["demand"])
WRITE = [Depends(require_permission(P.ORDERS_WRITE))]


def _order(db, run_id: str, order_id: str, user: User) -> Order:
    order = db.get(Order, (order_id, run_id))
    scope = supplier_scope(user)
    if order is None or (scope and order.supplier_id != scope):
        raise NotFound("Order not found")  # 404 not 403: don't reveal other suppliers' IDs
    return order


@router.get("/orders", response_model=Page[OrderOut])
def list_orders(run: RunDep, db: DB, paging: Paging, status: OrderStatus | None = None,
                priority: Priority | None = None, site_id: str | None = None,
                date_from: date | None = None, date_to: date | None = None,
                user: User = Depends(require_permission(P.ORDERS_READ))):
    stmt = apply_filters(select(Order).where(Order.run_id == run.id), Order,
                         status=status, priority=priority, site_id=site_id, supplier_id=supplier_scope(user))
    if date_from:
        stmt = stmt.where(Order.created_at >= date_from)
    if date_to:
        stmt = stmt.where(Order.created_at < date_to)
    return paginate(db, stmt, Order, paging)


@router.get("/orders/{order_id}", response_model=OrderDetailOut)
def get_order(run: RunDep, order_id: str, db: DB, user: User = Depends(require_permission(P.ORDERS_READ))):
    order = _order(db, run.id, order_id, user)
    # TODO: repositories.demand.order_trace(db, run.id, order_id) -> deliveries + outcomes
    raise NotImplementedError


@router.post("/orders", response_model=OrderOut, status_code=201, dependencies=WRITE)
def create_order(run: WritableRun, data: OrderCreate, db: DB):
    # TODO: verify site exists; next ORD-YYYY-NNNNNN id; EntityEvent(created)
    raise NotImplementedError


@router.post("/orders/{order_id}/transition", response_model=OrderOut)
def transition_order(run: WritableRun, order_id: str, data: OrderTransitionIn, db: DB,
                     user: User = Depends(require_permission(P.ORDERS_WRITE))):
    return order_service.transition(db, _order(db, run.id, order_id, user), data.to_status, data.reason, user)


@router.get("/deliveries", response_model=Page[DeliveryOut])
def list_deliveries(run: RunDep, db: DB, paging: Paging, status: DeliveryStatus | None = None,
                    order_id: str | None = None, required_vehicle_type: VehicleType | None = None,
                    assigned: bool | None = None, user: User = Depends(require_permission(P.ORDERS_READ))):
    stmt = apply_filters(select(Delivery).where(Delivery.run_id == run.id), Delivery,
                         status=status, order_id=order_id, required_vehicle_type=required_vehicle_type)
    if assigned is not None:
        stmt = stmt.where((Delivery.status == DeliveryStatus.ASSIGNED) if assigned
                          else (Delivery.status != DeliveryStatus.ASSIGNED))
    if scope := supplier_scope(user):
        stmt = stmt.join(Order, (Order.run_id == Delivery.run_id) & (Order.order_id == Delivery.order_id)) \
                   .where(Order.supplier_id == scope)
    return paginate(db, stmt, Delivery, paging)


@router.get("/deliveries/{delivery_id}", response_model=DeliveryDetailOut,
            dependencies=[Depends(require_permission(P.ORDERS_READ))])
def get_delivery(run: RunDep, delivery_id: str, db: DB):
    if db.get(Delivery, (delivery_id, run.id)) is None:
        raise NotFound("Delivery not found")
    # TODO: include time window + all RouteStop rows (incl. removed) as stop_history
    raise NotImplementedError


@router.post("/orders/{order_id}/deliveries", response_model=DeliveryOut, status_code=201, dependencies=WRITE)
def create_delivery(run: WritableRun, order_id: str, data: DeliveryCreate, db: DB):
    raise NotImplementedError


@router.put("/deliveries/{delivery_id}/time-window", response_model=TimeWindowOut, dependencies=WRITE)
def set_time_window(run: WritableRun, delivery_id: str, data: TimeWindowIn, db: DB):
    # TODO: if delivery is on a route, re-check rule 3 and flag stop as late
    raise NotImplementedError
