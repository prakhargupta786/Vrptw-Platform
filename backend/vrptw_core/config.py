from dataclasses import dataclass, field

ANOMALY_TYPES = ("capacity_exceeded", "stop_omitted", "stop_duplicated", "arrival_before_departure",
                 "shift_exceeded", "coordinate_out_of_region")


@dataclass(frozen=True)
class RunConfig:
    seed: int = 20261022
    sites: int = 500
    deliveries: int = 2000
    vehicles: int = 100
    days: int = 30
    anomaly_rate: float = 0.02
    anomaly_types: tuple[str, ...] = ANOMALY_TYPES
    start_date: str = "2026-10-01"
    # Region bounding polygon (lon, lat). TODO: confirm real region (open question in design doc).
    region_polygon: tuple[tuple[float, float], ...] = field(
        default=((77.30, 28.50), (77.45, 28.50), (77.45, 28.65), (77.30, 28.65)))

    @classmethod
    def starter(cls, seed: int = 20261022) -> "RunConfig":
        return cls(seed=seed, sites=50, deliveries=200, vehicles=10, days=3)
