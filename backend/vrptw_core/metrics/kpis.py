"""On-time rate, failed rate by reason, capacity utilization, distance/time, avg delay, unserved count,
shift utilization/overtime, anomaly precision/recall. Pure functions over DataFrames."""


def compute_all(tables, validation, ground_truth) -> dict:
    raise NotImplementedError
