def data_dictionary() -> list[dict]:
    """TODO: build from SQLAlchemy-free table specs: table, column, type, description, allowed_values."""
    return []


def source_manifest(seed: int, config: dict) -> dict:
    return {
        "provenance": "synthetic",
        "statement": "All data is synthetically generated. No external or personal data was used.",
        "generator": "vrptw_core",
        "seed": seed,
        "config": config,
    }
