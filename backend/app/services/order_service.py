from sqlalchemy.orm import Session

from app.core.exceptions import Conflict
from app.models import EntityEvent, Order, User
from app.models.enums import ORDER_TRANSITIONS


def transition(db: Session, order: Order, to_status, reason: str | None, user: User) -> Order:
    allowed = ORDER_TRANSITIONS[order.status]
    if to_status not in allowed:
        raise Conflict(f"Cannot move order from {order.status} to {to_status}", code="INVALID_TRANSITION",
                       details={"allowed": sorted(allowed)})
    db.add(EntityEvent(run_id=order.run_id, entity="Order", entity_id=order.order_id,
                       from_state=order.status, to_state=to_status, payload={"reason": reason}, actor_id=user.id))
    order.status = to_status
    db.commit()
    return order
