"""Role -> permission mapping. Endpoints check permissions, never role names."""
from enum import StrEnum


class Role(StrEnum):
    ADMIN = "ADMIN"
    PLANNER = "PLANNER"
    WAREHOUSE = "WAREHOUSE"
    ANALYST = "ANALYST"
    OPS_MANAGER = "OPS_MANAGER"
    SUPPLIER = "SUPPLIER"


class P(StrEnum):
    USERS_MANAGE = "users:manage"
    RUNS_CREATE = "runs:create"
    RUNS_RERUN = "runs:rerun"
    RUNS_DELETE = "runs:delete"
    RUNS_LOCK = "runs:lock"
    RUNS_READ = "runs:read"
    MASTER_READ = "master:read"
    MASTER_WRITE = "master:write"
    ORDERS_READ = "orders:read"
    ORDERS_WRITE = "orders:write"
    ROUTES_READ = "routes:read"
    ROUTES_PLAN = "routes:plan"
    OUTCOMES_READ = "outcomes:read"
    ANOMALIES_READ = "anomalies:read"
    VALIDATION_READ = "validation:read"
    VALIDATION_RUN = "validation:run"
    METRICS_READ = "metrics:read"
    EXPORTS_DOWNLOAD = "exports:download"
    GROUND_TRUTH_READ = "ground_truth:read"


_READ_ALL = {P.RUNS_READ, P.MASTER_READ, P.ORDERS_READ, P.ROUTES_READ, P.OUTCOMES_READ}

ROLE_PERMISSIONS: dict[Role, frozenset[P]] = {
    Role.ADMIN: frozenset(P),
    Role.PLANNER: frozenset(_READ_ALL | {
        P.MASTER_WRITE, P.ORDERS_WRITE, P.ROUTES_PLAN,
        P.ANOMALIES_READ, P.VALIDATION_READ, P.METRICS_READ,
    }),
    Role.WAREHOUSE: frozenset(_READ_ALL),
    Role.ANALYST: frozenset(_READ_ALL | {
        P.RUNS_CREATE, P.ANOMALIES_READ, P.VALIDATION_READ, P.VALIDATION_RUN,
        P.METRICS_READ, P.EXPORTS_DOWNLOAD, P.GROUND_TRUTH_READ,
    }),
    Role.OPS_MANAGER: frozenset(_READ_ALL | {
        P.ANOMALIES_READ, P.VALIDATION_READ, P.METRICS_READ, P.EXPORTS_DOWNLOAD,
    }),
    # Row-level filtered to own supplier_id in repositories.
    Role.SUPPLIER: frozenset({P.ORDERS_READ, P.OUTCOMES_READ}),
}


def permissions_for(role: Role) -> frozenset[P]:
    return ROLE_PERMISSIONS[role]
