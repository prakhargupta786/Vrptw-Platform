from collections.abc import Callable
from typing import Annotated

import jwt
from fastapi import Depends, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions import Conflict, Forbidden, NotFound, Unauthorized
from app.core.permissions import P, Role, permissions_for
from app.core.security import decode_token
from app.db.session import get_db
from app.models import Run, User
from app.models.enums import RunStatus
from app.schemas.common import PageParams

bearer = HTTPBearer(auto_error=False)
DB = Annotated[Session, Depends(get_db)]


def get_current_user(db: DB, creds: HTTPAuthorizationCredentials | None = Depends(bearer)) -> User:
    if creds is None:
        raise Unauthorized("Missing bearer token")
    try:
        payload = decode_token(creds.credentials, "access")
    except (jwt.PyJWTError, ValueError):
        raise Unauthorized("Invalid or expired token", code="TOKEN_INVALID")
    user = db.get(User, payload["sub"])
    if user is None or not user.is_active:
        raise Unauthorized("User inactive or not found")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_permission(*perms: P) -> Callable[..., User]:
    """Usage: user: User = Depends(require_permission(P.ROUTES_PLAN))"""
    def checker(user: CurrentUser) -> User:
        granted = permissions_for(user.role)
        missing = [p for p in perms if p not in granted]
        if missing:
            raise Forbidden("Missing permission", details={"missing": missing})
        return user
    return checker


def get_run(run_id: str, db: DB) -> Run:
    run = db.get(Run, run_id)
    if run is None:
        raise NotFound(f"Run {run_id} not found")
    return run


RunDep = Annotated[Run, Depends(get_run)]


def writable_run(run: RunDep) -> Run:
    if run.status == RunStatus.LOCKED:
        raise Conflict("Run is locked", code="RUN_LOCKED")
    if run.status in (RunStatus.QUEUED, RunStatus.GENERATING):
        raise Conflict("Run is still generating", code="RUN_NOT_READY")
    return run


WritableRun = Annotated[Run, Depends(writable_run)]


def page_params(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    sort: str | None = Query(None, description="field or -field"),
) -> PageParams:
    return PageParams(page=page, page_size=page_size, sort=sort)


Paging = Annotated[PageParams, Depends(page_params)]


def supplier_scope(user: User) -> str | None:
    """Returns supplier_id to filter by, or None when the user sees all rows."""
    return user.supplier_id if user.role == Role.SUPPLIER else None
