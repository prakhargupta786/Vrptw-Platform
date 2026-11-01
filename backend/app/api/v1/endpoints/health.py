from fastapi import APIRouter
from sqlalchemy import text

from app.api.deps import DB

router = APIRouter(tags=["health"])


@router.get("/health")
def health(db: DB):
    try:
        db.execute(text("SELECT 1"))
        db_ok = "ok"
    except Exception:  # noqa: BLE001
        db_ok = "down"
    return {"status": "ok" if db_ok == "ok" else "degraded", "db": db_ok}
