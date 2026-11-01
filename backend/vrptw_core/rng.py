"""One independent seeded stream per module, so changing e.g. anomaly_rate never shifts the clean baseline."""
import numpy as np

MODULES = ("sites", "fleet", "drivers", "matrix", "demand", "planning", "simulation", "anomalies")


def streams(seed: int) -> dict[str, np.random.Generator]:
    children = np.random.SeedSequence(seed).spawn(len(MODULES))
    return {name: np.random.default_rng(child) for name, child in zip(MODULES, children)}
