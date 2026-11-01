"""Manual re-planning. Every mutation: check rules -> write -> recompute totals -> append EntityEvent.

Rules (from design doc):
 1 load <= capacity effective at route_date (weight, volume, stops)
 2 arrival >= prev departure + travel time
 3 arrival within window else 'late' flag
 4 route end <= shift end else 'shift_exceeded' flag
 5 restricted vehicle never to restricted site
 6 every delivery assigned or unserved with reason
"""
from sqlalchemy.orm import Session

from app.models import Route, RouteStop, User
from app.schemas.planning import AddStopIn, ReorderIn


def add_stop(db: Session, run_id: str, route: Route, data: AddStopIn, user: User) -> Route:
    # TODO: load delivery + window + capacity; vrptw_core.planning.rules.check_insert(...)
    # raise Conflict(code="CAPACITY_EXCEEDED" | "SHIFT_EXCEEDED" | "VEHICLE_RESTRICTED") unless data.force
    raise NotImplementedError


def reorder_stops(db: Session, run_id: str, route: Route, data: ReorderIn, user: User) -> Route:
    # TODO: validate stop_ids == active stops of route; re-time via travel matrix; recompute_totals
    raise NotImplementedError


def remove_stop(db: Session, run_id: str, route: Route, stop: RouteStop, reason: str, user: User) -> None:
    # Close, never delete: stop.removed_at = now, removed_reason = reason; delivery -> pending
    raise NotImplementedError


def recompute_totals(db: Session, route: Route) -> None:
    """Route totals are always derived from active stops (arithmetic reconciliation check depends on this)."""
    raise NotImplementedError
