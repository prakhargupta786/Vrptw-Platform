"""Step 7. Each check returns (status, failing_ids, detected_type|None)."""
CHECKS = ("pk_unique", "fk_integrity", "enum_values", "datetime_order", "arithmetic", "lifecycle", "duplicates",
          "anomaly_match")


def pk_unique(tables): raise NotImplementedError
def fk_integrity(tables): raise NotImplementedError
def enum_values(tables): raise NotImplementedError
def datetime_order(tables): raise NotImplementedError
def arithmetic(tables): raise NotImplementedError
def lifecycle(tables, events): raise NotImplementedError
def duplicates(tables): raise NotImplementedError
def anomaly_match(detected, ground_truth): raise NotImplementedError
