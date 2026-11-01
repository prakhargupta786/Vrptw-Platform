"""Step 3. Orders -> Deliveries (1:N) -> TimeWindows (incl. deliberate boundary cases)."""
from datetime import date, datetime, timedelta

import pandas as pd

from vrptw_core.config import RunConfig

SUPPLIERS = tuple(f"SUP-{i:03d}" for i in range(1, 11))
WINDOW_PRIORITY = {"high": 1, "normal": 2, "low": 3}


def required_vehicle_type(weight_kg: float, volume_m3: float) -> str:
    """Smallest vehicle type that can physically carry the delivery."""
    if weight_kg > 1000 or volume_m3 > 6:
        return "truck"
    if weight_kg > 350 or volume_m3 > 2.5:
        return "van"
    return "mini"


def generate_demand(cfg: RunConfig, master: dict[str, pd.DataFrame], rng: dict) -> dict[str, pd.DataFrame]:
    r = rng["demand"]
    start = date.fromisoformat(cfg.start_date)
    site_ids = master["customer_sites"]["site_id"].to_numpy()

    # ~1.3 deliveries per order: every order gets one, the rest are spread randomly (Order 1:N Delivery).
    n_orders = max(1, min(cfg.deliveries, round(cfg.deliveries / 1.3)))
    per_order = [1] * n_orders
    for k in r.integers(0, n_orders, size=cfg.deliveries - n_orders):
        per_order[k] += 1

    orders, deliveries, windows = [], [], []
    d_no = 0
    for o in range(1, n_orders + 1):
        order_id = f"ORD-2026-{o:06d}"
        day = int(r.integers(0, cfg.days))
        delivery_date = start + timedelta(days=day)
        priority = str(r.choice(["low", "normal", "high"], p=[0.2, 0.6, 0.2]))
        total_kg = total_m3 = 0.0
        for _ in range(per_order[o - 1]):
            d_no += 1
            delivery_id = f"DEL-2026-{d_no:06d}"
            heavy = r.random() < 0.05
            kg = round(float(r.uniform(800, 2500) if heavy else min(r.lognormal(4.0, 0.8), 900)), 1)
            m3 = round(kg / float(r.uniform(150, 300)), 3)
            total_kg, total_m3 = total_kg + kg, total_m3 + m3
            deliveries.append({"delivery_id": delivery_id, "order_id": order_id,
                               "service_minutes": int(r.choice([5, 10, 15, 20, 30])),
                               "required_vehicle_type": required_vehicle_type(kg, m3),
                               "weight_kg": kg, "volume_m3": m3, "status": "pending"})

            day_start = datetime.combine(delivery_date, datetime.min.time())
            roll = r.random()
            if roll < 0.03:    # boundary: window opens exactly at the earliest shift start
                earliest, width = day_start + timedelta(hours=6), 60
            elif roll < 0.06:  # boundary: very narrow window
                earliest, width = day_start + timedelta(minutes=480 + 30 * int(r.integers(0, 15))), 15
            else:
                earliest = day_start + timedelta(minutes=480 + 30 * int(r.integers(0, 15)))  # 08:00 - 15:00
                width = int(r.choice([60, 120, 180, 240]))
            windows.append({"window_id": f"TW-2026-{d_no:06d}", "delivery_id": delivery_id, "earliest": earliest,
                            "latest": earliest + timedelta(minutes=width),
                            "type": "hard" if r.random() < 0.7 else "soft", "priority": WINDOW_PRIORITY[priority]})

        created_at = datetime.combine(delivery_date - timedelta(days=int(r.integers(1, 4))), datetime.min.time()) \
            + timedelta(minutes=int(r.integers(9 * 60, 19 * 60)))
        orders.append({"order_id": order_id, "site_id": str(r.choice(site_ids)), "supplier_id": str(r.choice(SUPPLIERS)),
                       "quantity": int(r.integers(1, 50)), "weight_kg": round(total_kg, 1),
                       "volume_m3": round(total_m3, 3), "priority": priority, "status": "created",
                       "created_at": created_at})

    return {"orders": pd.DataFrame(orders), "deliveries": pd.DataFrame(deliveries),
            "time_windows": pd.DataFrame(windows)}
