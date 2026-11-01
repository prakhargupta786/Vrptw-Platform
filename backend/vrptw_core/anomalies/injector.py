"""Step 6. Corrupt a small labelled share of rows. Labels go ONLY to ground_truth; no is_anomaly column anywhere,
and IDs are assigned before injection so ordering leaks nothing."""
import pandas as pd


def inject(tables: dict[str, pd.DataFrame], rate: float, types: tuple[str, ...], rng) -> tuple[dict, pd.DataFrame]:
    """Returns (corrupted_tables, ground_truth[issue_type, affected_entity, affected_id, expected_decision])."""
    raise NotImplementedError


def capacity_exceeded(tables, ids, rng): raise NotImplementedError
def stop_omitted(tables, ids, rng): raise NotImplementedError
def stop_duplicated(tables, ids, rng): raise NotImplementedError
def arrival_before_departure(tables, ids, rng): raise NotImplementedError
def shift_exceeded(tables, ids, rng): raise NotImplementedError
def coordinate_out_of_region(tables, ids, rng): raise NotImplementedError
