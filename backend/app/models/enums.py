from enum import StrEnum


class RunStatus(StrEnum):
    QUEUED = "queued"
    GENERATING = "generating"
    READY = "ready"
    VALIDATING = "validating"
    VALIDATED = "validated"
    LOCKED = "locked"
    FAILED = "failed"


class VehicleType(StrEnum):
    MINI = "mini"
    VAN = "van"
    TRUCK = "truck"


class VehicleStatus(StrEnum):
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    RETIRED = "retired"


class TrafficScenario(StrEnum):
    PEAK = "peak"
    OFF_PEAK = "off_peak"
    DISRUPTION = "disruption"


class OrderStatus(StrEnum):
    CREATED = "created"
    PLANNED = "planned"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


ORDER_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.CREATED: {OrderStatus.PLANNED, OrderStatus.CANCELLED},
    OrderStatus.PLANNED: {OrderStatus.COMPLETED, OrderStatus.CANCELLED, OrderStatus.CREATED},
    OrderStatus.COMPLETED: set(),
    OrderStatus.CANCELLED: set(),
}


class Priority(StrEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class DeliveryStatus(StrEnum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    UNSERVED = "unserved"
    DONE = "done"


class WindowType(StrEnum):
    HARD = "hard"
    SOFT = "soft"


class OutcomeStatus(StrEnum):
    DELIVERED = "delivered"
    LATE = "late"
    FAILED = "failed"
    SKIPPED = "skipped"


class ReasonCode(StrEnum):
    # TODO: confirm full list with the business (open question in design doc)
    CUSTOMER_ABSENT = "CUSTOMER_ABSENT"
    ACCESS_RESTRICTED = "ACCESS_RESTRICTED"
    OUTSIDE_WINDOW = "OUTSIDE_WINDOW"
    NO_CAPACITY = "NO_CAPACITY"
    NO_VEHICLE_TYPE = "NO_VEHICLE_TYPE"
    SHIFT_LIMIT = "SHIFT_LIMIT"
    REPLANNED = "REPLANNED"


class AnomalyType(StrEnum):
    CAPACITY_EXCEEDED = "capacity_exceeded"
    STOP_OMITTED = "stop_omitted"
    STOP_DUPLICATED = "stop_duplicated"
    ARRIVAL_BEFORE_DEPARTURE = "arrival_before_departure"
    SHIFT_EXCEEDED = "shift_exceeded"
    COORDINATE_OUT_OF_REGION = "coordinate_out_of_region"


class ValidationCheck(StrEnum):
    PK_UNIQUE = "pk_unique"
    FK_INTEGRITY = "fk_integrity"
    ENUM_VALUES = "enum_values"
    DATETIME_ORDER = "datetime_order"
    ARITHMETIC = "arithmetic"
    LIFECYCLE = "lifecycle"
    DUPLICATES = "duplicates"
    ANOMALY_MATCH = "anomaly_match"
