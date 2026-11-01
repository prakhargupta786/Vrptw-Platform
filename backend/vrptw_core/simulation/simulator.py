"""Step 5. Rule-driven (not random) outcomes: arrival outside window -> late; customer absent / access restricted
-> failed + reason_code. Randomness only decides *which* events occur (seeded), rules decide the status."""
from datetime import timedelta

import pandas as pd

CUSTOMER_ABSENT_RATE = 0.03
ACCESS_ISSUE_RATE = 0.05      # only at sites that have access restrictions


def simulate(planned: dict, master: dict[str, pd.DataFrame], demand: dict[str, pd.DataFrame], rng: dict) -> dict:
    r = rng["simulation"]
    travel = planned["travel"]
    routes = planned["routes"].set_index("route_id").to_dict("index")
    deliveries = planned["deliveries"].set_index("delivery_id").to_dict("index")
    order_site = dict(zip(planned["orders"]["order_id"], planned["orders"]["site_id"]))
    windows = demand["time_windows"].set_index("delivery_id").to_dict("index")
    restrictions = master["customer_sites"].set_index("site_id")["access_restrictions"].to_dict()
    start = pd.Timestamp(master["shifts"]["start_at"].min()).normalize()

    outcomes, outcome_no = [], 0
    stops = planned["route_stops"]
    for route_id, group in (stops.groupby("route_id", sort=True) if len(stops) else []):
        day = (pd.Timestamp(routes[route_id]["route_date"]) - start).days + 1
        prev_site = prev_departure = None
        for s in group.sort_values("sequence").itertuples(index=False):
            d, w = deliveries[s.delivery_id], windows[s.delivery_id]
            site = order_site[d["order_id"]]
            if prev_site is None:
                arrival = s.planned_arrival + timedelta(minutes=float(r.normal(0, 8)))
            else:
                _, minutes = travel.between(prev_site, site, day, prev_departure)
                arrival = prev_departure + timedelta(minutes=minutes * float(r.lognormal(0, 0.2)))

            reason, delay = None, 0.0
            if r.random() < CUSTOMER_ABSENT_RATE:
                status, reason, departure = "failed", "CUSTOMER_ABSENT", arrival + timedelta(minutes=5)
            elif restrictions[site] and r.random() < ACCESS_ISSUE_RATE:
                status, reason, departure = "failed", "ACCESS_RESTRICTED", arrival + timedelta(minutes=5)
            else:
                departure = max(arrival, w["earliest"]) + timedelta(minutes=d["service_minutes"])
                if arrival > w["latest"]:
                    status, reason = "late", "OUTSIDE_WINDOW"
                    delay = round((arrival - w["latest"]).total_seconds() / 60, 1)
                else:
                    status = "delivered"
            outcome_no += 1
            outcomes.append({"outcome_id": f"OUT-2026-{outcome_no:06d}", "delivery_id": s.delivery_id,
                             "stop_id": s.stop_id, "actual_arrival": arrival.round("s"),
                             "actual_departure": departure.round("s"), "status": status, "reason_code": reason,
                             "delay_minutes": delay})
            prev_site, prev_departure = site, departure

    for u in planned["unserved_deliveries"].itertuples(index=False):  # never left the depot
        outcome_no += 1
        outcomes.append({"outcome_id": f"OUT-2026-{outcome_no:06d}", "delivery_id": u.delivery_id, "stop_id": None,
                         "actual_arrival": None, "actual_departure": None, "status": "skipped",
                         "reason_code": u.reason, "delay_minutes": 0.0})
    outcomes_df = pd.DataFrame(outcomes)

    # Lifecycle: delivered/late -> delivery done; order completed when every delivery is done,
    # cancelled when none could be planned at all.
    deliveries_df, orders_df, events = planned["deliveries"].copy(), planned["orders"].copy(), list(planned["events"])
    done_at = {o["delivery_id"]: o["actual_departure"] for o in outcomes if o["status"] in ("delivered", "late")}
    deliveries_df.loc[deliveries_df["delivery_id"].isin(done_at), "status"] = "done"
    for did, at in sorted(done_at.items()):
        events.append(("Delivery", did, "assigned", "done", at.to_pydatetime()))
    by_order = deliveries_df.groupby("order_id")["status"].agg(set)
    for order_id, statuses in by_order.items():
        current = orders_df.loc[orders_df["order_id"] == order_id, "status"].iloc[0]
        if statuses == {"done"} and current == "planned":
            at = max(done_at[d] for d in deliveries_df.loc[deliveries_df["order_id"] == order_id, "delivery_id"])
            events.append(("Order", order_id, "planned", "completed", at.to_pydatetime()))
            orders_df.loc[orders_df["order_id"] == order_id, "status"] = "completed"
        elif statuses == {"unserved"} and current == "created":
            first = deliveries_df.loc[deliveries_df["order_id"] == order_id, "delivery_id"].iloc[0]
            at = windows[first]["earliest"].to_pydatetime()
            events.append(("Order", order_id, "created", "cancelled", at))
            orders_df.loc[orders_df["order_id"] == order_id, "status"] = "cancelled"

    return {"delivery_outcomes": outcomes_df, "deliveries": deliveries_df, "orders": orders_df, "events": events}
