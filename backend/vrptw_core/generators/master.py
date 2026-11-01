"""Step 2. Returns pandas DataFrames: sites, vehicles, vehicle_capacities, drivers, shifts, travel_time, traffic_factors."""
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd

from vrptw_core.config import RunConfig

VEHICLE_TYPES = ("mini", "van", "truck")
# Base capacity per vehicle type: (max_weight_kg, max_volume_m3, max_stops); +-10% jitter per vehicle.
BASE_CAPACITY = {"mini": (500, 3.0, 15), "van": (1200, 8.0, 25), "truck": (4000, 25.0, 35)}
ROAD_FACTOR = 1.3  # straight-line haversine -> approximate road distance
FIRST_NAMES = ("Amit", "Rahul", "Priya", "Sunita", "Vikram", "Neha", "Arjun", "Kavita", "Rohit", "Pooja", "Sanjay",
               "Anjali", "Manoj", "Deepak", "Ritu", "Karan", "Meera", "Suresh", "Nisha", "Ajay")
LAST_NAMES = ("Sharma", "Verma", "Gupta", "Singh", "Kumar", "Yadav", "Jain", "Mishra", "Chauhan", "Rawat")
TRAFFIC_RANGES = {"peak": (1.3, 1.6), "off_peak": (0.9, 1.1), "disruption": (1.6, 2.2)}


def _bounds(cfg: RunConfig) -> tuple[float, float, float, float]:
    lons = [p[0] for p in cfg.region_polygon]
    lats = [p[1] for p in cfg.region_polygon]
    return min(lons), max(lons), min(lats), max(lats)


def region_of(lon: float, lat: float, cfg: RunConfig) -> str:
    """Region = quadrant of the bounding box (NE/NW/SE/SW)."""
    lon_min, lon_max, lat_min, lat_max = _bounds(cfg)
    ns = "N" if lat >= (lat_min + lat_max) / 2 else "S"
    ew = "E" if lon >= (lon_min + lon_max) / 2 else "W"
    return ns + ew


def _sites(cfg: RunConfig, rng: np.random.Generator) -> pd.DataFrame:
    lon_min, lon_max, lat_min, lat_max = _bounds(cfg)
    rows = []
    for i in range(1, cfg.sites + 1):
        lon, lat = rng.uniform(lon_min, lon_max), rng.uniform(lat_min, lat_max)
        address_type = rng.choice(["residential", "commercial", "industrial"], p=[0.5, 0.35, 0.15])
        restrictions = {}
        roll = rng.random()
        if address_type == "residential" and roll < 0.25:
            restrictions["max_vehicle_type"] = "van"  # narrow lanes: no trucks
        elif roll < 0.05:
            restrictions["max_vehicle_type"] = "mini"
        if rng.random() < 0.05:
            restrictions["zone"] = "Z1"  # low-emission zone
        rows.append({"site_id": f"SITE-{i:06d}", "name": f"{address_type.title()} Site {i}",
                     "lat": round(lat, 6), "lon": round(lon, 6), "region": region_of(lon, lat, cfg),
                     "address_type": str(address_type), "access_restrictions": restrictions})
    return pd.DataFrame(rows)


def _fleet(cfg: RunConfig, rng: np.random.Generator, start: date) -> tuple[pd.DataFrame, pd.DataFrame]:
    vehicles, capacities = [], []
    for i in range(1, cfg.vehicles + 1):
        vtype = str(rng.choice(VEHICLE_TYPES, p=[0.3, 0.5, 0.2]))
        status = str(rng.choice(["active", "maintenance", "retired"], p=[0.9, 0.07, 0.03]))
        effective_from = start - timedelta(days=int(rng.integers(30, 730)))
        vehicles.append({"vehicle_id": f"VEH-{i:06d}", "type": vtype, "status": status,
                         "restricted_zones": ["Z1"] if vtype != "mini" and rng.random() < 0.15 else [],
                         "effective_from": effective_from, "effective_to": None})
        kg, m3, stops = BASE_CAPACITY[vtype]
        jitter = rng.uniform(0.9, 1.1)
        capacities.append({"capacity_id": f"CAP-{i:06d}", "vehicle_id": f"VEH-{i:06d}",
                           "max_weight_kg": round(kg * jitter, 1), "max_volume_m3": round(m3 * jitter, 2),
                           "max_stops": stops, "effective_from": effective_from, "effective_to": None})
    return pd.DataFrame(vehicles), pd.DataFrame(capacities)


def _drivers_and_shifts(cfg: RunConfig, rng: np.random.Generator, start: date) -> tuple[pd.DataFrame, pd.DataFrame]:
    """One driver per vehicle; every active driver gets one shift per day (Driver 1:N Shift)."""
    drivers, shifts = [], []
    shift_no = 0
    for i in range(1, cfg.vehicles + 1):
        active = bool(rng.random() < 0.95)
        drivers.append({"driver_id": f"DRV-{i:06d}",
                        "name": f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}",
                        "license_class": str(rng.choice(["LMV", "HMV"], p=[0.7, 0.3])),
                        "home_depot": str(rng.choice(["DEPOT-NORTH", "DEPOT-SOUTH"])), "is_active": active})
        if not active:
            continue
        for day in range(cfg.days):
            shift_no += 1
            start_at = datetime.combine(start + timedelta(days=day), datetime.min.time()) + timedelta(
                minutes=int(rng.choice([360, 390, 420, 450, 480, 510, 540])))  # 06:00 - 09:00
            shifts.append({"shift_id": f"SHF-{shift_no:06d}", "driver_id": f"DRV-{i:06d}", "start_at": start_at,
                           "end_at": start_at + timedelta(hours=int(rng.choice([8, 9, 10]))),
                           "break_minutes": int(rng.choice([30, 45, 60])), "max_driving_hours": 8.0})
    return pd.DataFrame(drivers), pd.DataFrame(shifts)


def _travel_matrix(sites: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """Full directed site x site matrix (diagonal excluded); vectorised haversine."""
    lat, lon = np.radians(sites["lat"].to_numpy()), np.radians(sites["lon"].to_numpy())
    dlat, dlon = lat[None, :] - lat[:, None], lon[None, :] - lon[:, None]
    a = np.sin(dlat / 2) ** 2 + np.cos(lat[:, None]) * np.cos(lat[None, :]) * np.sin(dlon / 2) ** 2
    km = 2 * 6371.0088 * np.arcsin(np.sqrt(a)) * ROAD_FACTOR
    speed = rng.uniform(22, 38, size=km.shape)
    n = len(sites)
    i, j = np.where(~np.eye(n, dtype=bool))
    ids = sites["site_id"].to_numpy()
    return pd.DataFrame({"from_site": ids[i], "to_site": ids[j], "distance_km": np.round(km[i, j], 3),
                         "base_speed_kmh": np.round(speed[i, j], 2)})


def _traffic(cfg: RunConfig, rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    for day in range(1, cfg.days + 1):
        for scenario, (lo, hi) in TRAFFIC_RANGES.items():
            for region in ("NE", "NW", "SE", "SW"):
                rows.append({"day": day, "scenario": scenario, "region": region,
                             "factor": round(float(rng.uniform(lo, hi)), 3)})
    return pd.DataFrame(rows)


def generate_master(cfg: RunConfig, rng: dict) -> dict[str, pd.DataFrame]:
    start = date.fromisoformat(cfg.start_date)
    sites = _sites(cfg, rng["sites"])
    vehicles, capacities = _fleet(cfg, rng["fleet"], start)
    drivers, shifts = _drivers_and_shifts(cfg, rng["drivers"], start)
    return {"customer_sites": sites, "vehicles": vehicles, "vehicle_capacities": capacities, "drivers": drivers,
            "shifts": shifts, "travel_time_matrix": _travel_matrix(sites, rng["matrix"]),
            "traffic_factors": _traffic(cfg, rng["matrix"])}
