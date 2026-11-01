from typing import Any

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.schemas.common import Page, PageParams


def apply_filters(stmt: Select, model: type, **filters: Any) -> Select:
    for field, value in filters.items():
        if value is not None:
            stmt = stmt.where(getattr(model, field) == value)
    return stmt


def apply_sort(stmt: Select, model: type, sort: str | None) -> Select:
    if not sort:
        return stmt
    desc = sort.startswith("-")
    col = getattr(model, sort.lstrip("-"), None)
    if col is None:
        return stmt
    return stmt.order_by(col.desc() if desc else col.asc())


def paginate(db: Session, stmt: Select, model: type, params: PageParams) -> Page:
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    stmt = apply_sort(stmt, model, params.sort)
    rows = db.scalars(stmt.offset((params.page - 1) * params.page_size).limit(params.page_size)).all()
    return Page(items=list(rows), total=total, page=params.page, page_size=params.page_size)


def list_run_scoped(db: Session, model: type, run_id: str, params: PageParams, **filters: Any) -> Page:
    stmt = apply_filters(select(model).where(model.run_id == run_id), model, **filters)
    return paginate(db, stmt, model, params)
