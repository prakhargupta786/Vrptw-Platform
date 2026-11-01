"""Sites, vehicles (+capacities), drivers (+shifts), travel matrix. All scoped to /runs/{run_id}."""
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select

from app.api.deps import DB, Paging, RunDep, WritableRun, require_permission
from app.core.exceptions import NotFound
from app.core.permissions import P
from app.models import CustomerSite, Driver, Shift, TravelTime, Vehicle, VehicleCapacity
from app.models.enums import TrafficScenario, VehicleStatus, VehicleType
from app.repositories.base import list_run_scoped
from app.schemas.common import Page
from app.schemas.master import (CapacityIn, CapacityOut, DriverOut, ShiftIn, ShiftOut, SiteOut, SiteUpdate,
                                TravelLookupOut, VehicleOut, VehicleUpdate)

router = APIRouter(prefix="/runs/{run_id}", tags=["master-data"])
READ = [Depends(require_permission(P.MASTER_READ))]
WRITE = [Depends(require_permission(P.MASTER_WRITE))]


def _get(db, model, run_id: str, key: str):
    obj = db.get(model, (key, run_id))  # PK order is (entity_id, run_id)
    if obj is None:
        raise NotFound(f"{model.__name__} {key} not found")
    return obj


# ---- sites
@router.get("/sites", response_model=Page[SiteOut], dependencies=READ)
def list_sites(run: RunDep, db: DB, paging: Paging, region: str | None = None, address_type: str | None = None,
               in_region: bool | None = Query(None, description="false = sites outside the defined region")):
    # TODO: in_region filter via geo bounds (vrptw_core.geo.in_region)
    return list_run_scoped(db, CustomerSite, run.id, paging, region=region, address_type=address_type)


@router.get("/sites/{site_id}", response_model=SiteOut, dependencies=READ)
def get_site(run: RunDep, site_id: str, db: DB):
    return _get(db, CustomerSite, run.id, site_id)


@router.patch("/sites/{site_id}", response_model=SiteOut, dependencies=WRITE)
def update_site(run: WritableRun, site_id: str, data: SiteUpdate, db: DB):
    site = _get(db, CustomerSite, run.id, site_id)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(site, k, v)
    db.commit()  # TODO: re-check region bounds, append EntityEvent
    return site


# ---- vehicles
@router.get("/vehicles", response_model=Page[VehicleOut], dependencies=READ)
def list_vehicles(run: RunDep, db: DB, paging: Paging, type: VehicleType | None = None,
                  status: VehicleStatus | None = None):
    return list_run_scoped(db, Vehicle, run.id, paging, type=type, status=status)


@router.get("/vehicles/{vehicle_id}", response_model=VehicleOut, dependencies=READ)
def get_vehicle(run: RunDep, vehicle_id: str, db: DB):
    return _get(db, Vehicle, run.id, vehicle_id)


@router.patch("/vehicles/{vehicle_id}", response_model=VehicleOut, dependencies=WRITE)
def update_vehicle(run: WritableRun, vehicle_id: str, data: VehicleUpdate, db: DB):
    v = _get(db, Vehicle, run.id, vehicle_id)
    for k, val in data.model_dump(exclude_unset=True).items():
        setattr(v, k, val)
    db.commit()
    return v


@router.get("/vehicles/{vehicle_id}/capacities", response_model=list[CapacityOut], dependencies=READ)
def list_capacities(run: RunDep, vehicle_id: str, db: DB, at: date | None = None):
    stmt = select(VehicleCapacity).where(VehicleCapacity.run_id == run.id, VehicleCapacity.vehicle_id == vehicle_id)
    if at:
        stmt = stmt.where(VehicleCapacity.effective_from <= at,
                          (VehicleCapacity.effective_to.is_(None)) | (VehicleCapacity.effective_to >= at))
    return db.scalars(stmt.order_by(VehicleCapacity.effective_from)).all()


@router.post("/vehicles/{vehicle_id}/capacities", response_model=CapacityOut, status_code=201, dependencies=WRITE)
def add_capacity(run: WritableRun, vehicle_id: str, data: CapacityIn, db: DB):
    # TODO: close previous open range at data.effective_from - 1 day; 409 CAPACITY_RANGE_OVERLAP
    raise NotImplementedError


# ---- drivers / shifts
@router.get("/drivers", response_model=Page[DriverOut], dependencies=READ)
def list_drivers(run: RunDep, db: DB, paging: Paging, license_class: str | None = None,
                 home_depot: str | None = None, is_active: bool | None = None):
    return list_run_scoped(db, Driver, run.id, paging, license_class=license_class, home_depot=home_depot,
                           is_active=is_active)


@router.get("/drivers/{driver_id}/shifts", response_model=list[ShiftOut], dependencies=READ)
def list_shifts(run: RunDep, driver_id: str, db: DB):
    stmt = select(Shift).where(Shift.run_id == run.id, Shift.driver_id == driver_id).order_by(Shift.start_at)
    return db.scalars(stmt).all()


@router.post("/drivers/{driver_id}/shifts", response_model=ShiftOut, status_code=201, dependencies=WRITE)
def add_shift(run: WritableRun, driver_id: str, data: ShiftIn, db: DB):
    # TODO: reject overlapping shifts for the driver (409 SHIFT_OVERLAP); generate SHF id
    raise NotImplementedError


# ---- travel matrix
@router.get("/travel-matrix", dependencies=READ)
def list_travel(run: RunDep, db: DB, paging: Paging, from_site: str = Query(...), to_site: str | None = None):
    # from_site is required: the full matrix is too large to page through unfiltered
    return list_run_scoped(db, TravelTime, run.id, paging, from_site=from_site, to_site=to_site)


@router.get("/travel-matrix/lookup", response_model=TravelLookupOut, dependencies=READ)
def travel_lookup(run: RunDep, db: DB, from_site: str, to_site: str, day: int = Query(..., ge=1, le=366),
                  scenario: TrafficScenario = TrafficScenario.OFF_PEAK):
    # TODO: join TrafficFactor(day, scenario, region of from_site); minutes = km / speed * 60 * factor
    raise NotImplementedError
