"""Step 4. Greedy insertion per day: for each delivery (priority, earliest window), append it to the cheapest feasible
route (open routes first, else open a new vehicle+driver route); if none, mark unserved with reason.
Returns routes, route_stops, unserved_deliveries plus updated deliveries/orders and lifecycle events."""
from datetime import date, datetime, timedelta

import pandas as pd

from vrptw_core.config import RunConfig
from vrptw_core.geo import travel_minutes
from vrptw_core.planning.rules import check_capacity, check_vehicle_site

TYPE_RANK = {"mini": 0, "van": 1, "truck": 2}
LOADING_MINUTES = 30          # depot loading before the first stop
NEW_ROUTE_PENALTY = 60        # prefer filling open routes over opening new ones
# Failure stages in check order: the reason reported for an unserved delivery is the furthest stage any route reached.
STAGES = ("NO_VEHICLE_TYPE", "ACCESS_RESTRICTED", "NO_CAPACITY", "OUTSIDE_WINDOW", "SHIFT_LIMIT")


class Travel:
    """Travel-time lookup: base distance/speed from the matrix x traffic factor (day, scenario, region of origin)."""

    def __init__(self, master: dict[str, pd.DataFrame], disrupted_days: set[int]):
        m = master["travel_time_matrix"]
        self.pairs = dict(zip(zip(m["from_site"], m["to_site"]), zip(m["distance_km"], m["base_speed_kmh"])))
        t = master["traffic_factors"]
        self.factors = dict(zip(zip(t["day"], t["scenario"], t["region"]), t["factor"]))
        s = master["customer_sites"]
        self.region = dict(zip(s["site_id"], s["region"]))
        self.disrupted_days = disrupted_days

    @staticmethod
    def scenario(at: datetime, disrupted: bool) -> str:
        if disrupted:
            return "disruption"
        return "peak" if 8 <= at.hour < 10 or 17 <= at.hour < 20 else "off_peak"

    def between(self, from_site: str, to_site: str, day: int, at: datetime) -> tuple[float, float]:
        """Returns (km, minutes). day is 1-based."""
        if from_site == to_site:
            return 0.0, 0.0
        km, speed = self.pairs[(from_site, to_site)]
        factor = self.factors[(day, self.scenario(at, day in self.disrupted_days), self.region[from_site])]
        return km, travel_minutes(km, speed, factor)


def plan_routes(cfg: RunConfig, master: dict[str, pd.DataFrame], demand: dict[str, pd.DataFrame],
                rng: dict) -> dict:
    r = rng["planning"]
    start = date.fromisoformat(cfg.start_date)
    disrupted = {d for d in range(1, cfg.days + 1) if r.random() < 0.1}
    travel = Travel(master, disrupted)

    sites = master["customer_sites"].set_index("site_id")["access_restrictions"].to_dict()
    vehicles = master["vehicles"].set_index("vehicle_id").to_dict("index")
    caps = master["vehicle_capacities"].set_index("vehicle_id").to_dict("index")
    drivers = master["drivers"].set_index("driver_id")["is_active"].to_dict()
    shifts = {(s.driver_id, s.start_at.date()): s._asdict() for s in master["shifts"].itertuples(index=False)}

    orders = demand["orders"].copy()
    deliveries = demand["deliveries"].copy()
    order_site = dict(zip(orders["order_id"], orders["site_id"]))
    windows = demand["time_windows"].set_index("delivery_id").to_dict("index")

    routes, stops, unserved, events = [], [], [], []
    status: dict[str, str] = {}
    route_no = 0
    for day in range(1, cfg.days + 1):
        day_date = start + timedelta(days=day - 1)
        todays = [d for d in deliveries.itertuples(index=False) if windows[d.delivery_id]["earliest"].date() == day_date]
        todays.sort(key=lambda d: (windows[d.delivery_id]["priority"], windows[d.delivery_id]["earliest"]))

        # Vehicle i is crewed by driver i. Only active vehicles in their effective range with an on-duty driver.
        pairs = []
        for vid, v in vehicles.items():
            did = "DRV-" + vid.split("-")[1]
            if v["status"] == "active" and v["effective_from"] <= day_date and drivers.get(did) \
                    and (did, day_date) in shifts:
                pairs.append((vid, did, shifts[(did, day_date)]))
        pairs = [pairs[i] for i in r.permutation(len(pairs))]

        open_routes: list[dict] = []
        for d in todays:
            w, site = windows[d.delivery_id], order_site[d.order_id]
            unopened = {}
            for p in pairs:  # first unopened pair of each vehicle type is a candidate for a new route
                unopened.setdefault(vehicles[p[0]]["type"], p)
            candidates = [(rt, False) for rt in open_routes] + [
                ({"vehicle_id": p[0], "driver_id": p[1], "shift": p[2], "stops": [], "kg": 0.0, "m3": 0.0,
                  "km": 0.0, "last_site": None, "last_departure": None}, True) for p in unopened.values()]

            best, best_cost, furthest = None, None, -1
            for rt, is_new in candidates:
                v, cap = vehicles[rt["vehicle_id"]], caps[rt["vehicle_id"]]
                if TYPE_RANK[v["type"]] < TYPE_RANK[d.required_vehicle_type]:
                    furthest = max(furthest, 0)
                    continue
                if check_vehicle_site(v["type"], v["restricted_zones"], sites[site]):
                    furthest = max(furthest, 1)
                    continue
                if check_capacity(rt["kg"] + d.weight_kg, rt["m3"] + d.volume_m3, len(rt["stops"]) + 1, cap):
                    furthest = max(furthest, 2)
                    continue
                if rt["last_site"] is None:
                    km, minutes = 0.0, 0.0
                    arrival = rt["shift"]["start_at"] + timedelta(minutes=LOADING_MINUTES)
                else:
                    km, minutes = travel.between(rt["last_site"], site, day, rt["last_departure"])
                    arrival = rt["last_departure"] + timedelta(minutes=minutes)
                if arrival > w["latest"]:
                    furthest = max(furthest, 3)
                    continue
                service_start = max(arrival, w["earliest"])
                departure = service_start + timedelta(minutes=d.service_minutes)
                if departure + timedelta(minutes=rt["shift"]["break_minutes"]) > rt["shift"]["end_at"]:
                    furthest = max(furthest, 4)
                    continue
                cost = minutes + (service_start - arrival).total_seconds() / 60 + (NEW_ROUTE_PENALTY if is_new else 0)
                if best_cost is None or cost < best_cost:
                    best, best_cost = (rt, is_new, km, arrival, departure), cost

            if best is None:
                reason = STAGES[max(furthest, 0)]
                unserved.append({"delivery_id": d.delivery_id, "reason": reason})
                status[d.delivery_id] = "unserved"
                continue
            rt, is_new, km, arrival, departure = best
            if is_new:
                open_routes.append(rt)
                pairs = [p for p in pairs if p[0] != rt["vehicle_id"]]
            rt["stops"].append({"delivery_id": d.delivery_id, "planned_arrival": arrival, "planned_departure": departure,
                                "travel_km_from_prev": round(km, 3)})
            rt["kg"] += d.weight_kg
            rt["m3"] += d.volume_m3
            rt["km"] += km
            rt["last_site"], rt["last_departure"] = site, departure
            status[d.delivery_id] = "assigned"

        for rt in open_routes:
            route_no += 1
            route_id = f"RTE-2026-{route_no:06d}"
            routes.append({"route_id": route_id, "route_date": day_date, "vehicle_id": rt["vehicle_id"],
                           "driver_id": rt["driver_id"], "shift_id": rt["shift"]["shift_id"],
                           "total_weight_kg": round(rt["kg"], 1), "total_volume_m3": round(rt["m3"], 3),
                           "total_distance_km": round(rt["km"], 3),
                           "planned_duration_min": round(
                               (rt["last_departure"] - rt["shift"]["start_at"]).total_seconds() / 60, 1),
                           "flags": []})
            for seq, s in enumerate(rt["stops"], start=1):
                stops.append({"stop_id": f"STOP-{route_id}-{seq:03d}", "route_id": route_id, "sequence": seq,
                              "removed_at": None, "removed_reason": None, **s})

    # Lifecycle: delivery pending -> assigned|unserved; order created -> planned (any delivery assigned).
    planned_at = {o.order_id: datetime.combine(o.created_at.date(), datetime.min.time()) + timedelta(hours=20)
                  for o in orders.itertuples(index=False)}
    deliveries["status"] = deliveries["delivery_id"].map(status).fillna("unserved")
    for d in deliveries.itertuples(index=False):
        events.append(("Delivery", d.delivery_id, "pending", d.status, planned_at[d.order_id]))
    assigned_orders = set(deliveries.loc[deliveries["status"] == "assigned", "order_id"])
    orders["status"] = orders["order_id"].map(lambda o: "planned" if o in assigned_orders else "created")
    for o in sorted(assigned_orders):
        events.append(("Order", o, "created", "planned", planned_at[o]))

    return {"routes": pd.DataFrame(routes), "route_stops": pd.DataFrame(stops),
            "unserved_deliveries": pd.DataFrame(unserved, columns=["delivery_id", "reason"]),
            "deliveries": deliveries, "orders": orders, "events": events, "travel": travel}
