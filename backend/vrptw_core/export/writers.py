"""Deterministic writers: rows sorted by PK, fixed float format, no wall-clock timestamps, LF line endings —
otherwise SHA-256 differs between identical runs."""
from pathlib import Path

import pandas as pd

FLOAT_FMT = "%.6f"


def write_csv(df: pd.DataFrame, path: Path, pk: list[str]) -> None:
    df.sort_values(pk).to_csv(path, index=False, float_format=FLOAT_FMT, lineterminator="\n")
