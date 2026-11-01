from vrptw_core.geo import haversine_km, in_region
from vrptw_core.planning.rules import check_capacity, check_vehicle_site
from vrptw_core.rng import streams


def test_haversine_known_distance():
    # Delhi (28.6139, 77.2090) -> Noida (28.5355, 77.3910) ~ 19.5 km
    assert 19 < haversine_km(28.6139, 77.2090, 28.5355, 77.3910) < 20.5


def test_in_region():
    square = ((0, 0), (1, 0), (1, 1), (0, 1))
    assert in_region(0.5, 0.5, square)
    assert not in_region(1.5, 0.5, square)


def test_capacity_rule():
    cap = {"max_weight_kg": 100, "max_volume_m3": 5, "max_stops": 3}
    assert check_capacity(90, 4, 3, cap) == []
    assert check_capacity(101, 4, 3, cap)[0].code == "CAPACITY_EXCEEDED"


def test_truck_blocked_from_van_site():
    assert check_vehicle_site("truck", [], {"max_vehicle_type": "van"})[0].code == "VEHICLE_RESTRICTED"
    assert check_vehicle_site("van", [], {"max_vehicle_type": "van"}) == []


def test_rng_streams_are_independent_and_reproducible():
    a, b = streams(20261022), streams(20261022)
    assert a["sites"].random() == b["sites"].random()
    assert streams(20261022)["sites"].random() != streams(20261022)["anomalies"].random()
