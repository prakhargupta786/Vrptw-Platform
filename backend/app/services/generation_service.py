"""Runs the vrptw_core pipeline for a Run and bulk-loads its tables (all rows tagged with run_id)."""
import pandas as pd
from sqlalchemy import insert
from sqlalchemy.orm import Session

from app.db.base import Base
from app.models import GroundTruth, Run
from app.models.enums import RunStatus
from vrptw_core.config import RunConfig
from vrptw_core.pipeline import generate

# Parents before children so composite FKs resolve.
LOAD_ORDER = ("customer_sites", "vehicles", "vehicle_capacities", "drivers", "shifts", "travel_time_matrix",
              "traffic_factors", "orders", "deliveries", "time_windows", "routes", "route_stops",
              "unserved_deliveries", "delivery_outcomes", "entity_events")
CHUNK = 5000


def config_for(run: Run) -> RunConfig:
    scale = run.config.get("scale", {})
    return RunConfig(seed=run.seed, sites=scale.get("sites", 500), deliveries=scale.get("deliveries", 2000),
                     vehicles=scale.get("vehicles", 100), days=scale.get("days", 30),
                     anomaly_rate=run.config.get("anomaly_rate", 0.02),
                     anomaly_types=tuple(run.config.get("anomaly_types", RunConfig.anomaly_types)))


def _records(df: pd.DataFrame, run_id: str) -> list[dict]:
    """DataFrame -> DB-ready dicts: NaN/NaT -> None, pandas Timestamps -> datetime, numpy scalars -> Python."""
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_datetime64_any_dtype(out[col]):
            out[col] = out[col].map(lambda x: None if pd.isna(x) else x.to_pydatetime())
    out = out.astype(object).where(out.notna(), None)
    out["run_id"] = run_id
    return out.to_dict("records")


def generate_into(db: Session, run: Run) -> dict[str, int]:
    """Generates and loads one run's dataset in a single transaction; sets status=ready and row_counts."""
    result = generate(config_for(run))
    tables = result["tables"]
    counts = {}
    for name in LOAD_ORDER:
        rows = _records(tables[name], run.id)
        table = Base.metadata.tables[name]
        for i in range(0, len(rows), CHUNK):
            db.execute(insert(table), rows[i:i + CHUNK])
        counts[name] = len(rows)
    gt = _records(result["ground_truth"], run.id)
    if gt:
        db.execute(insert(GroundTruth), gt)
    counts["ground_truth"] = len(gt)
    run.row_counts, run.status = counts, RunStatus.READY
    db.commit()
    return counts
