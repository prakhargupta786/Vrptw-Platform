from app.core.permissions import P, Role, permissions_for


def test_only_admin_and_analyst_see_ground_truth():
    allowed = {r for r in Role if P.GROUND_TRUTH_READ in permissions_for(r)}
    assert allowed == {Role.ADMIN, Role.ANALYST}


def test_supplier_is_read_only_on_orders_and_outcomes():
    assert permissions_for(Role.SUPPLIER) == {P.ORDERS_READ, P.OUTCOMES_READ}


def test_warehouse_cannot_replan():
    assert P.ROUTES_PLAN not in permissions_for(Role.WAREHOUSE)
