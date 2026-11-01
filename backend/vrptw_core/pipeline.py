import pandas as pd

from vrptw_core.config import RunConfig
from vrptw_core.rng import streams


def generate(cfg: RunConfig) -> dict:
    """Runs steps 2-6 in order and returns {"tables": {...}, "ground_truth": df}."""
    rng = streams(cfg.seed)
    from vrptw_core.generators.demand import generate_demand
    from vrptw_core.generators.master import generate_master
    from vrptw_core.planning.planner import plan_routes
    from vrptw_core.simulation.simulator import simulate
    master = generate_master(cfg, rng)
    demand = generate_demand(cfg, master, rng)
    planned = plan_routes(cfg, master, demand, rng)
    simulated = simulate(planned, master, demand, rng)

    events = sorted(simulated["events"], key=lambda e: (e[4], e[0], e[1]))
    entity_events = pd.DataFrame(
        [{"id": f"EVT-{i:07d}", "entity": entity, "entity_id": eid, "from_state": frm, "to_state": to,
          "payload": {}, "actor_id": None, "at": at} for i, (entity, eid, frm, to, at) in enumerate(events, start=1)])

    tables = {**master, "orders": simulated["orders"], "deliveries": simulated["deliveries"],
              "time_windows": demand["time_windows"], "routes": planned["routes"],
              "route_stops": planned["route_stops"], "unserved_deliveries": planned["unserved_deliveries"],
              "delivery_outcomes": simulated["delivery_outcomes"], "entity_events": entity_events}
    # TODO: step 6 anomaly injection (vrptw_core.anomalies.injector.inject) is not implemented yet,
    # so the dataset is the clean baseline and ground truth is empty.
    ground_truth = pd.DataFrame(columns=["issue_type", "affected_entity", "affected_id", "expected_decision"])
    return {"tables": tables, "ground_truth": ground_truth}
