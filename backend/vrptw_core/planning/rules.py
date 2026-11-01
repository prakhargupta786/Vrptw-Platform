"""Business rules shared by the generator planner AND the API's manual re-planning."""
from dataclasses import dataclass


@dataclass
class RuleViolation:
    code: str  # CAPACITY_EXCEEDED | SHIFT_EXCEEDED | VEHICLE_RESTRICTED | TIME_SEQUENCE | OUTSIDE_WINDOW
    detail: str


def check_capacity(load_kg: float, load_m3: float, stops: int, cap: dict) -> list[RuleViolation]:
    out = []
    if load_kg > cap["max_weight_kg"]:
        out.append(RuleViolation("CAPACITY_EXCEEDED", f"weight {load_kg} > {cap['max_weight_kg']}"))
    if load_m3 > cap["max_volume_m3"]:
        out.append(RuleViolation("CAPACITY_EXCEEDED", f"volume {load_m3} > {cap['max_volume_m3']}"))
    if stops > cap["max_stops"]:
        out.append(RuleViolation("CAPACITY_EXCEEDED", f"stops {stops} > {cap['max_stops']}"))
    return out


def check_vehicle_site(vehicle_type: str, vehicle_zones: list[str], site_restrictions: dict) -> list[RuleViolation]:
    order = {"mini": 0, "van": 1, "truck": 2}
    max_type = site_restrictions.get("max_vehicle_type")
    if max_type and order[vehicle_type] > order[max_type]:
        return [RuleViolation("VEHICLE_RESTRICTED", f"{vehicle_type} exceeds site limit {max_type}")]
    if site_restrictions.get("zone") in vehicle_zones:
        return [RuleViolation("VEHICLE_RESTRICTED", f"vehicle barred from zone {site_restrictions['zone']}")]
    return []
